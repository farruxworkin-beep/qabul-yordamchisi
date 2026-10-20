"""
FastAPI ilovasi.

Sahifalar:  /  (bemor)   /operator  (operator paneli, parol bilan)   /stats  (statistika)   /docs (API)
"""
import csv
import hashlib
import hmac
import io
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import clarify, config, db, engine
from .i18n import DEPARTMENTS
from .predictor import Predictor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
STATIC = config.BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    app.state.predictor = Predictor()
    yield


app = FastAPI(title="Bemor murojaatini yo'naltirish tizimi", version="1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


# ----------------------------------------------------------------------------- sxemalar
class TriageIn(BaseModel):
    text: str = Field(..., max_length=1500)
    lang: str = "uz"


class AnswerIn(BaseModel):
    case_id: int
    question_id: str
    option_id: str


class LoginIn(BaseModel):
    password: str


class ResolveIn(BaseModel):
    department: str
    note: str | None = Field(None, max_length=500)


# ----------------------------------------------------------------------------- avtorizatsiya
COOKIE = "triage_op"


def _token():
    return hmac.new(config.SECRET_KEY.encode(), b"operator", hashlib.sha256).hexdigest()


def require_operator(request: Request):
    if not hmac.compare_digest(request.cookies.get(COOKIE, ""), _token()):
        raise HTTPException(401, "Operator sifatida kiring")


# ----------------------------------------------------------------------------- sahifalar
@app.get("/", include_in_schema=False)
def page_patient():
    return FileResponse(STATIC / "index.html")


@app.get("/operator", include_in_schema=False)
def page_operator():
    return FileResponse(STATIC / "operator.html")


@app.get("/stats", include_in_schema=False)
def page_stats():
    return FileResponse(STATIC / "stats.html")


# ----------------------------------------------------------------------------- bemor API
def _public(case_id, result, state):
    out = {k: v for k, v in result.items()}
    out["case_id"] = case_id
    out["answers"] = [{"q": a["q"], "a": a["a"], "text": clarify.option_text(a["q"], a["a"]),
                       "question": clarify._BY_ID[a["q"]]["text"]} for a in state["answers"]]
    return out


@app.post("/api/triage")
def triage(body: TriageIn, request: Request):
    p = request.app.state.predictor
    state = engine.new_state(body.text, p)
    result = engine.decide(state, p)
    case_id = db.create_case(body.text, body.lang, state, result)
    return _public(case_id, result, state)


@app.post("/api/answer")
def answer(body: AnswerIn, request: Request):
    p = request.app.state.predictor
    case = db.get_case(body.case_id)
    if not case:
        raise HTTPException(404, "Murojaat topilmadi")
    state = case["state"]
    if case["status"] != "question" or not state["asked"] or state["asked"][-1] != body.question_id:
        raise HTTPException(409, "Bu savolga hozir javob berib bo'lmaydi")
    try:
        engine.apply_answer(state, p.labels, body.question_id, body.option_id)
    except (KeyError, ValueError):
        raise HTTPException(422, "Noto'g'ri javob varianti")
    result = engine.decide(state, p)
    db.update_case(body.case_id, state, result)
    return _public(body.case_id, result, state)


@app.get("/api/info")
def info(request: Request):
    return {**request.app.state.predictor.info(), "max_questions": config.MAX_QUESTIONS}


@app.get("/api/departments")
def departments():
    return DEPARTMENTS


# ----------------------------------------------------------------------------- operator API
@app.post("/api/login")
def login(body: LoginIn, response: Response):
    if not hmac.compare_digest(body.password, config.OPERATOR_PASSWORD):
        raise HTTPException(401, "Parol noto'g'ri")
    response.set_cookie(COOKIE, _token(), httponly=True, samesite="strict", max_age=12 * 3600)
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE)
    return {"ok": True}


@app.get("/api/me", dependencies=[Depends(require_operator)])
def me():
    return {"ok": True}


@app.get("/api/queue", dependencies=[Depends(require_operator)])
def get_queue(resolved: bool = False):
    rows = db.queue(include_resolved=resolved)
    for r in rows:
        r["answers_text"] = [{"question": clarify._BY_ID[a["q"]]["text"], "answer": clarify.option_text(a["q"], a["a"])}
                             for a in (r["state"] or {}).get("answers", [])]
    return rows


@app.post("/api/cases/{case_id}/resolve", dependencies=[Depends(require_operator)])
def resolve_case(case_id: int, body: ResolveIn):
    if body.department not in DEPARTMENTS:
        raise HTTPException(422, "Bunday bo'lim yo'q")
    if not db.resolve(case_id, body.department, body.note):
        raise HTTPException(404, "Murojaat topilmadi")
    return {"ok": True}


@app.get("/api/stats", dependencies=[Depends(require_operator)])
def get_stats():
    return db.stats()


@app.get("/api/export.csv", dependencies=[Depends(require_operator)])
def export_csv():
    rows = db.export_labeled()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["id", "created", "text", "ai_dept", "operator_dept"])
    w.writeheader(); w.writerows(rows)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=operator_labeled.csv"})
