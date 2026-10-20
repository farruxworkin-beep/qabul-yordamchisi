"""SQLite: murojaatlar va operator qarorlari (alohida server kerak emas)."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created       TEXT NOT NULL,
    ui_lang       TEXT,
    text          TEXT NOT NULL,
    status        TEXT NOT NULL,          -- routed | question | operator | other | not_medical
    department    TEXT,                   -- AI tavsiyasi
    confidence    REAL,
    urgent        INTEGER DEFAULT 0,
    flags         TEXT,                   -- JSON
    state         TEXT,                   -- JSON: P, savollar, javoblar
    result        TEXT,                   -- JSON: bemorga ko'rsatilgan oxirgi javob
    operator_dept TEXT,                   -- operator tanlagan bo'lim (haqiqiy yorliq)
    operator_note TEXT,
    resolved_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_status ON cases(status, operator_dept);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect(path=None):
    con = sqlite3.connect(path or config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init(path=None):
    with connect(path) as c:
        c.executescript(SCHEMA)


def create_case(text, ui_lang, state, result, path=None):
    with connect(path) as c:
        cur = c.execute(
            "INSERT INTO cases (created, ui_lang, text, status, department, confidence, urgent, flags, state, result)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (now(), ui_lang, text, result["status"], result.get("department"), result.get("confidence"),
             int(result["urgent"]), json.dumps(result["flags"], ensure_ascii=False),
             json.dumps(state, ensure_ascii=False), json.dumps(result, ensure_ascii=False)))
        return cur.lastrowid


def update_case(case_id, state, result, path=None):
    with connect(path) as c:
        c.execute("UPDATE cases SET status=?, department=?, confidence=?, state=?, result=? WHERE id=?",
                  (result["status"], result.get("department"), result.get("confidence"),
                   json.dumps(state, ensure_ascii=False), json.dumps(result, ensure_ascii=False), case_id))


def get_case(case_id, path=None):
    with connect(path) as c:
        r = c.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        return _row(r) if r else None


def _row(r):
    d = dict(r)
    for k in ("flags", "state", "result"):
        d[k] = json.loads(d[k]) if d.get(k) else None
    return d


def queue(include_resolved=False, limit=200, path=None):
    """Operator ko'rishi kerak bo'lganlar: operator/other holatidagi va shoshilinch murojaatlar."""
    q = "SELECT * FROM cases WHERE (status IN ('operator','other') OR urgent=1)"
    if not include_resolved:
        q += " AND operator_dept IS NULL"
    q += " ORDER BY urgent DESC, id DESC LIMIT ?"
    with connect(path) as c:
        return [_row(r) for r in c.execute(q, (limit,)).fetchall()]


def resolve(case_id, dept, note=None, path=None):
    with connect(path) as c:
        cur = c.execute("UPDATE cases SET operator_dept=?, operator_note=?, resolved_at=? WHERE id=?",
                        (dept, note, now(), case_id))
        return cur.rowcount > 0


def stats(path=None):
    with connect(path) as c:
        total = c.execute("SELECT COUNT(*) FROM cases WHERE status!='question'").fetchone()[0]
        by_status = dict(c.execute("SELECT status, COUNT(*) FROM cases GROUP BY status").fetchall())
        by_dept = dict(c.execute(
            "SELECT COALESCE(operator_dept, department) d, COUNT(*) FROM cases "
            "WHERE status IN ('routed','operator','other') AND COALESCE(operator_dept, department) IS NOT NULL "
            "GROUP BY d ORDER BY 2 DESC").fetchall())
        urgent = c.execute("SELECT COUNT(*) FROM cases WHERE urgent=1").fetchone()[0]
        checked = c.execute("SELECT COUNT(*), SUM(operator_dept=department) FROM cases "
                            "WHERE operator_dept IS NOT NULL AND status='routed'").fetchone()
        pending = c.execute("SELECT COUNT(*) FROM cases WHERE (status IN ('operator','other') OR urgent=1) "
                            "AND operator_dept IS NULL").fetchone()[0]
        asked = c.execute("SELECT COUNT(*) FROM cases WHERE state LIKE '%\"asked\": [\"%'").fetchone()[0]
    return {"total": total, "by_status": by_status, "by_department": by_dept, "urgent": urgent,
            "pending": pending, "with_questions": asked,
            "operator_checked_routed": checked[0] or 0, "operator_agreed": checked[1] or 0}


def export_labeled(path=None):
    """Operator tasdiqlagan murojaatlar — keyingi o'qitish uchun haqiqiy ma'lumot."""
    with connect(path) as c:
        return [dict(r) for r in c.execute(
            "SELECT id, created, text, department AS ai_dept, operator_dept FROM cases "
            "WHERE operator_dept IS NOT NULL ORDER BY id").fetchall()]
