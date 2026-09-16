"""FastAPI backend — Pillow PNG generation + referral unlock + analytics DB."""
import io
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .generator import THEMES, THEME_CATS, render_graphic, CANVAS_SIZE, APP_NAME

app = FastAPI(title=f"{APP_NAME} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    text: str = Field(default="", max_length=280)
    author_name: str = Field(default="", max_length=40)
    handle: str = Field(default="", max_length=40)
    show_author: bool = True
    theme_name: str = "Tech Dark"
    font_size: int = Field(default=62, ge=24, le=140)
    visitor: str = Field(default="", max_length=64)  # pq_vid from browser


# ---------------------------------------------------------------------------
# Analytics + reviews database (SQLite — file-based, permanent across
# restarts/refreshes, zero cost, no extra services).
# ---------------------------------------------------------------------------
DB_FILE = Path(__file__).parent / "data" / "app.db"


def _db() -> sqlite3.Connection:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "CREATE TABLE IF NOT EXISTS events("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, visitor TEXT, "
        "event TEXT, meta TEXT)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS reviews("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, visitor TEXT UNIQUE, "
        "name TEXT, stars INTEGER)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS unlocks("
        "visitor TEXT PRIMARY KEY, ts TEXT, method TEXT)"
    )
    return con


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def has_review(visitor: str) -> bool:
    if not visitor:
        return False
    con = _db()
    try:
        row = con.execute("SELECT 1 FROM reviews WHERE visitor=?", (visitor,)).fetchone()
        return row is not None
    finally:
        con.close()


class TrackIn(BaseModel):
    visitor: str = Field(default="", max_length=64)
    event: str = Field(max_length=40)  # page_view | theme_select | download | ...
    meta: dict = Field(default_factory=dict)


class ReviewIn(BaseModel):
    visitor: str = Field(max_length=64)
    name: str = Field(max_length=30)
    stars: int = Field(ge=1, le=5)


@app.post("/api/track")
def track(body: TrackIn):
    con = _db()
    try:
        con.execute(
            "INSERT INTO events(ts, visitor, event, meta) VALUES(?,?,?,?)",
            (_now(), body.visitor[:64], body.event[:40],
             json.dumps(body.meta)[:2000]),
        )
        con.commit()
    finally:
        con.close()
    return {"ok": True}


@app.post("/api/review")
def review(body: ReviewIn):
    name = body.name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="name too short")
    con = _db()
    try:
        con.execute(
            "INSERT OR IGNORE INTO reviews(ts, visitor, name, stars) VALUES(?,?,?,?)",
            (_now(), body.visitor, name, body.stars),
        )
        con.commit()
    finally:
        con.close()
    return {"ok": True, "watermark": False}  # watermark now OFF for this visitor


@app.get("/api/status/{visitor}")
def status(visitor: str):
    reviewed = has_review(visitor)
    pro = _pro_unlocked(visitor)
    return {"reviewed": reviewed, "watermark": not reviewed,
            "pro_unlocked": pro, "unlocked": _all_pro() if pro else []}


@app.get("/api/stats")
def stats(request: Request):
    """Owner dashboard data — password protected (server-side check).

    Password kabhi code me nahi hota. Backend sirf ADMIN_PASSWORD
    environment variable se match karta hai (frontend ka source
    dekhne se kisi ko password nahi milega).
    """
    expected = os.environ.get("ADMIN_PASSWORD", "")
    given = request.headers.get("x-admin-password", "")
    if not expected or not secrets.compare_digest(given, expected):
        raise HTTPException(status_code=401, detail="admin password required")
    con = _db()
    try:
        con.row_factory = sqlite3.Row
        visitors = con.execute("SELECT COUNT(DISTINCT visitor) c FROM events").fetchone()["c"]
        views = con.execute("SELECT COUNT(*) c FROM events WHERE event='page_view'").fetchone()["c"]
        downloads = con.execute("SELECT COUNT(*) c FROM events WHERE event='download'").fetchone()["c"]
        by_theme = [
            {"theme": r["theme"], "downloads": r["c"]}
            for r in con.execute(
                "SELECT json_extract(meta,'$.theme') theme, COUNT(*) c "
                "FROM events WHERE event='download' GROUP BY theme ORDER BY c DESC"
            )
        ]
        rev = con.execute("SELECT COUNT(*) c, COALESCE(AVG(stars),0) a FROM reviews").fetchone()
        reviews = [
            dict(r) for r in con.execute(
                "SELECT ts, name, stars FROM reviews ORDER BY id DESC LIMIT 50")
        ]
        recent = [
            dict(r) for r in con.execute(
                "SELECT ts, visitor, event, meta FROM events ORDER BY id DESC LIMIT 100")
        ]
    finally:
        con.close()
    return {
        "visitors": visitors, "page_views": views, "downloads": downloads,
        "downloads_by_theme": by_theme,
        "reviews_count": rev["c"], "avg_stars": round(rev["a"], 2),
        "reviews": reviews, "recent_events": recent,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "app": APP_NAME, "canvas": CANVAS_SIZE}


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": APP_NAME,
        "message": "PixelQuote API is running 🚀",
        "try": ["/api/health", "/api/themes"],
    }


@app.get("/api/themes")
def themes():
    return {
        name: {"description": m["description"], "pro": m["pro"],
               "cat": THEME_CATS.get(name, "Modern")}
        for name, m in THEMES.items()
    }


@app.post("/api/generate")
def generate(req: GenerateRequest):
    theme = req.theme_name if req.theme_name in THEMES else "Tech Dark"
    reviewed = has_review(req.visitor)
    img = render_graphic(
        text=req.text[:280],
        author_name=req.author_name,
        handle=req.handle,
        show_author=req.show_author,
        theme_name=theme,
        font_size=req.font_size,
        show_watermark=not reviewed,  # review diya → watermark OFF
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{APP_NAME.lower()}-1080x1080.png"'},
    )


# ---------------------------------------------------------------------------
# Referral unlock system — 100% free, no paid APIs.
# Rule: when 2 UNIQUE visitors open your ?ref=CODE link, you unlock Pro themes.
# ---------------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data" / "referrals.json"
REFS_NEEDED = 1  # sirf 1 dost ka link kholna kaafi hai


def _load_refs() -> dict:
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_refs(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=1), encoding="utf-8")


def _new_code() -> str:
    for _ in range(20):
        code = secrets.token_hex(3).upper()  # e.g. "A7X2B9"
        if code not in _load_refs():
            return code
    return secrets.token_hex(4).upper()


class NewRefIn(BaseModel):
    visitor: str = Field(default="", max_length=64)


class VisitIn(BaseModel):
    code: str = Field(max_length=16)
    visitor: str = Field(max_length=64)


class UnlockIn(BaseModel):
    code: str = Field(max_length=16)
    theme: str = Field(max_length=40)


@app.post("/api/referral/new")
def referral_new(body: NewRefIn):
    data = _load_refs()
    code = _new_code()
    data[code] = {"owner": body.visitor, "visitors": [], "unlocked": []}
    _save_refs(data)
    return {"code": code, "needed": REFS_NEEDED}


@app.post("/api/referral/visit")
def referral_visit(body: VisitIn):
    data = _load_refs()
    rec = data.get(body.code.upper())
    if rec is None:
        raise HTTPException(status_code=404, detail="bad code")
    v = body.visitor.strip()
    # owner's own opens + repeat opens don't count
    if v and v != rec.get("owner") and v not in rec["visitors"]:
        rec["visitors"].append(v)
        _save_refs(data)
    return {"visits": len(rec["visitors"]), "needed": REFS_NEEDED,
            "unlocked": rec["unlocked"]}


@app.get("/api/referral/{code}")
def referral_status(code: str):
    rec = _load_refs().get(code.upper())
    if rec is None:
        raise HTTPException(status_code=404, detail="bad code")
    return {"visits": len(rec["visitors"]), "needed": REFS_NEEDED,
            "unlocked": rec["unlocked"]}


@app.post("/api/referral/unlock")
def referral_unlock(body: UnlockIn):
    data = _load_refs()
    rec = data.get(body.code.upper())
    if rec is None:
        raise HTTPException(status_code=404, detail="bad code")
    if len(rec["visitors"]) < REFS_NEEDED:
        raise HTTPException(status_code=403, detail="not enough referrals yet")
    # EK task = SAARE Pro themes unlock (single-theme unlock hata diya)
    all_pro = _all_pro()
    rec["unlocked"] = all_pro
    _save_refs(data)
    _unlock_all_visitor(rec.get("owner", ""), "referral")
    return {"ok": True, "unlocked": all_pro}


class SocialIn(BaseModel):
    visitor: str = Field(max_length=64)


@app.post("/api/social/unlock")
def social_unlock(body: SocialIn):
    """X-follow task. Honor system hai — X follow ko free me auto-verify
    karna possible nahi (X API paid hai), isliye 'I Followed' trust pe hai."""
    if not body.visitor.strip():
        raise HTTPException(status_code=400, detail="visitor missing")
    _unlock_all_visitor(body.visitor, "twitter")
    return {"ok": True, "unlocked": _all_pro()}


def _unlock_all_visitor(visitor: str, method: str) -> None:
    """Kisi bhi task (referral/X) se visitor ke liye permanent unlock record."""
    if not visitor:
        return
    con = _db()
    try:
        con.execute(
            "INSERT OR IGNORE INTO unlocks(ts, visitor, method) VALUES(?,?,?)",
            (_now(), visitor, method),
        )
        con.commit()
    finally:
        con.close()


def _pro_unlocked(visitor: str) -> bool:
    if not visitor:
        return False
    con = _db()
    try:
        return con.execute("SELECT 1 FROM unlocks WHERE visitor=?", (visitor,)).fetchone() is not None
    finally:
        con.close()


def _all_pro() -> list:
    return [n for n, m in THEMES.items() if m.get("pro")]
