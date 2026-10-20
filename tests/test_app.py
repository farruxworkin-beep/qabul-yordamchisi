"""Avtomatik testlar: python -m pytest -q"""
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["OPERATOR_PASSWORD"] = "test-pass"


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    os.environ["TRIAGE_DB"] = str(tmp_path_factory.mktemp("db") / "t.db")
    import importlib
    from app import config
    importlib.reload(config)
    from fastapi.testclient import TestClient
    from app import main
    importlib.reload(main)
    with TestClient(main.app) as c:
        yield c


def triage(c, text, lang="uz"):
    r = c.post("/api/triage", json={"text": text, "lang": lang})
    assert r.status_code == 200
    return r.json()


def test_textnorm():
    from app.textnorm import normalize
    assert normalize("Бошим қаттиқ оғрияпти") == "boshim qattiq og'riyapti"
    assert normalize("Сильно болит голова") == "сильно болит голова"
    assert normalize("og‘riq") == "og'riq"


def test_clear_complaint_routed(client):
    r = triage(client, "boshim qattiq og'riyapti, ko'nglim aynaydi")
    assert r["status"] == "routed" and r["department"] == "nevrologiya"


def test_explicit_department(client):
    r = triage(client, "Хочу записаться к кардиологу", "ru")
    assert r["status"] == "routed" and r["department"] == "kardiologiya" and r["confidence"] == 1.0


def test_red_flag(client):
    r = triage(client, "Давящая боль в груди отдаёт в левую руку", "ru")
    assert r["urgent"] and r["department"] == "kardiologiya"


def test_crisis(client):
    r = triage(client, "o'zimni o'ldirish fikrlari kelyapti")
    assert r["crisis"] and r["status"] == "operator"


def test_other_specialty(client):
    r = triage(client, "tishim qattiq og'riyapti")
    assert r["status"] == "other" and r["other"]["subtype"] == "stomatologiya"


def test_not_medical(client):
    assert triage(client, "salom")["status"] == "not_medical"
    assert triage(client, "!!")["status"] == "not_medical"


def test_question_flow(client):
    r = triage(client, "bel og'rig'i")
    assert r["status"] == "question"
    seen = set()
    for _ in range(3):
        if r["status"] != "question":
            break
        q = r["question"]; assert q["id"] not in seen; seen.add(q["id"])
        r = client.post("/api/answer", json={"case_id": r["case_id"], "question_id": q["id"],
                                             "option_id": q["options"][0]["id"]}).json()
    assert r["status"] in ("routed", "operator")
    assert len(r["answers"]) == len(seen)


def test_answer_wrong_question_rejected(client):
    r = triage(client, "bel og'rig'i")
    bad = client.post("/api/answer", json={"case_id": r["case_id"], "question_id": "skin", "option_id": "yes"})
    assert bad.status_code == 409


def test_operator_auth_and_resolve(client):
    assert client.get("/api/queue").status_code == 401
    assert client.post("/api/login", json={"password": "wrong"}).status_code == 401
    assert client.post("/api/login", json={"password": "test-pass"}).status_code == 200
    q = client.get("/api/queue").json()
    assert q, "navbat bo'sh bo'lmasligi kerak"
    cid = q[0]["id"]
    assert client.post(f"/api/cases/{cid}/resolve", json={"department": "terapiya"}).status_code == 200
    assert client.post(f"/api/cases/{cid}/resolve", json={"department": "yo'q"}).status_code == 422
    s = client.get("/api/stats").json()
    assert s["total"] >= 5
    assert client.get("/api/export.csv").status_code == 200


def test_bayes_and_info_gain():
    from app import clarify
    labels = ["ginekologiya_urologiya", "nevrologiya", "travmatologiya"]
    P = np.array([0.34, 0.33, 0.33])
    q, gain = clarify.select_question(P, labels, [], 0.0)
    assert q is not None and gain > 0
    post = clarify.update(P, labels, "back_where", "kidney")
    assert post.argmax() == 0 and abs(post.sum() - 1) < 1e-9
    assert np.allclose(clarify.update(P, labels, "back_where", "unknown"), P)
