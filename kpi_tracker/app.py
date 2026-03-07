from __future__ import annotations

import csv
import datetime as dt
import hashlib
import hmac
import os
import secrets
import smtplib
import sqlite3
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from kpi_tracker.analytics import DashboardSummary, calculate_dashboard, forecast_next

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("KPI_DB_PATH", BASE_DIR / "kpi_tracker.db"))

app = FastAPI(title="KPI Tracker App", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
security = HTTPBearer(auto_error=False)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'manager', 'admin')),
            provider TEXT NOT NULL DEFAULT 'local',
            department TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            kra TEXT NOT NULL,
            owner_user_id INTEGER,
            FOREIGN KEY(owner_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            department_id INTEGER NOT NULL,
            frequency TEXT NOT NULL CHECK(frequency IN ('monthly', 'quarterly', 'ytd')),
            threshold_pct REAL NOT NULL DEFAULT 90,
            target_owner_email TEXT,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS kpi_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            target_value REAL NOT NULL,
            actual_value REAL NOT NULL,
            submitted_by INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(kpi_id) REFERENCES kpis(id),
            FOREIGN KEY(submitted_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            owner_user_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('on_track', 'at_risk', 'delayed', 'completed')),
            progress_pct REAL NOT NULL,
            due_date TEXT,
            budget REAL,
            spent REAL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(department_id) REFERENCES departments(id),
            FOREIGN KEY(owner_user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()

    # seed admin
    cur.execute("SELECT id FROM users WHERE email = ?", ("admin@kpi.local",))
    if not cur.fetchone():
        now = dt.datetime.utcnow().isoformat()
        cur.execute(
            """INSERT INTO users(full_name, email, password_hash, role, provider, department, created_at)
            VALUES(?, ?, ?, 'admin', 'local', 'Executive', ?)""",
            (
                "Default Admin",
                "admin@kpi.local",
                hash_password("ChangeMe123!"),
                now,
            ),
        )
        conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    salt = b"kpi-tracker-v1"
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed)


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = (dt.datetime.utcnow() + dt.timedelta(hours=12)).isoformat()
    conn = get_db()
    conn.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES(?,?,?)", (token, user_id, expires))
    conn.commit()
    conn.close()
    return token


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> sqlite3.Row:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = credentials.credentials
    conn = get_db()
    row = conn.execute(
        """SELECT u.* FROM sessions s
        JOIN users u ON u.id=s.user_id
        WHERE s.token=? AND s.expires_at > ?""",
        (token, dt.datetime.utcnow().isoformat()),
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid session")
    return row


def require_manager(user: sqlite3.Row = Depends(get_current_user)) -> sqlite3.Row:
    if user["role"] not in {"manager", "admin"}:
        raise HTTPException(status_code=403, detail="Manager access required")
    return user


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(user|manager|admin)$")
    department: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class KpiCreate(BaseModel):
    title: str
    description: str | None = None
    department_id: int
    frequency: str = Field(pattern="^(monthly|quarterly|ytd)$")
    threshold_pct: float = 90
    target_owner_email: EmailStr | None = None


class KpiEntryCreate(BaseModel):
    kpi_id: int
    period: str
    target_value: float
    actual_value: float
    notes: str | None = None


class ProjectCreate(BaseModel):
    name: str
    department_id: int
    status: str = Field(pattern="^(on_track|at_risk|delayed|completed)$")
    progress_pct: float = Field(ge=0, le=100)
    due_date: str | None = None
    budget: float | None = None
    spent: float | None = None


def send_email_alert(to_email: str, subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    port = int(os.getenv("SMTP_PORT", "587"))
    sender = os.getenv("SMTP_SENDER", user or "noreply@kpi.local")

    if not host or not user or not password:
        # no SMTP configured in local/demo mode
        return

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/auth/register")
def register_user(payload: UserCreate):
    now = dt.datetime.utcnow().isoformat()
    conn = get_db()
    try:
        cur = conn.execute(
            """INSERT INTO users(full_name, email, password_hash, role, provider, department, created_at)
            VALUES(?,?,?,?, 'local', ?, ?)""",
            (payload.full_name, payload.email.lower(), hash_password(payload.password), payload.role, payload.department, now),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError as exc:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered") from exc
    conn.close()
    return {"user_id": user_id}


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (payload.email.lower(),)).fetchone()
    conn.close()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session(user["id"])
    return {"access_token": token, "role": user["role"], "user_id": user["id"]}


@app.get("/api/v1/auth/oauth/providers")
def oauth_providers() -> dict[str, Any]:
    return {
        "google": {
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "note": "Configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to enable.",
        },
        "microsoft": {
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "note": "Configure MS365_CLIENT_ID and MS365_CLIENT_SECRET to enable.",
        },
    }


@app.post("/api/v1/departments")
def create_department(name: str = Form(...), kra: str = Form(...), owner_user_id: int | None = Form(None), _: sqlite3.Row = Depends(require_manager)):
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO departments(name, kra, owner_user_id) VALUES(?,?,?)", (name, kra, owner_user_id))
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        raise HTTPException(status_code=400, detail="Department already exists") from exc
    conn.close()
    return {"department_id": cur.lastrowid}


@app.post("/api/v1/kpis")
def create_kpi(payload: KpiCreate, _: sqlite3.Row = Depends(require_manager)):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO kpis(title, description, department_id, frequency, threshold_pct, target_owner_email)
        VALUES(?,?,?,?,?,?)""",
        (payload.title, payload.description, payload.department_id, payload.frequency, payload.threshold_pct, payload.target_owner_email),
    )
    conn.commit()
    kpi_id = cur.lastrowid
    conn.close()
    return {"kpi_id": kpi_id}


@app.post("/api/v1/kpi-entries")
def create_kpi_entry(payload: KpiEntryCreate, user: sqlite3.Row = Depends(get_current_user)):
    conn = get_db()
    now = dt.datetime.utcnow().isoformat()
    cur = conn.execute(
        """INSERT INTO kpi_entries(kpi_id, period, target_value, actual_value, submitted_by, notes, created_at)
        VALUES(?,?,?,?,?,?,?)""",
        (payload.kpi_id, payload.period, payload.target_value, payload.actual_value, user["id"], payload.notes, now),
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return {"entry_id": entry_id}


@app.post("/api/v1/projects")
def create_project(payload: ProjectCreate, user: sqlite3.Row = Depends(get_current_user)):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO projects(name, department_id, owner_user_id, status, progress_pct, due_date, budget, spent, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            payload.name,
            payload.department_id,
            user["id"],
            payload.status,
            payload.progress_pct,
            payload.due_date,
            payload.budget,
            payload.spent,
            dt.datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    project_id = cur.lastrowid
    conn.close()
    return {"project_id": project_id}


@app.post("/api/v1/import/raw")
async def import_raw_csv(file: UploadFile = File(...), user: sqlite3.Row = Depends(get_current_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV file required")
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    conn = get_db()
    inserted = 0
    for row in reader:
        conn.execute(
            """INSERT INTO kpi_entries(kpi_id, period, target_value, actual_value, submitted_by, notes, created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (
                int(row["kpi_id"]),
                row["period"],
                float(row["target_value"]),
                float(row["actual_value"]),
                user["id"],
                row.get("notes"),
                dt.datetime.utcnow().isoformat(),
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return {"inserted": inserted}


@app.get("/api/v1/dashboard")
def dashboard(_: sqlite3.Row = Depends(require_manager)):
    conn = get_db()
    summary = calculate_dashboard(conn)

    dept_rows = conn.execute(
        """SELECT d.name as department, d.kra,
        AVG((e.actual_value / NULLIF(e.target_value, 0))*100) as achievement_pct
        FROM departments d
        LEFT JOIN kpis k ON k.department_id=d.id
        LEFT JOIN kpi_entries e ON e.kpi_id=k.id
        GROUP BY d.id
        ORDER BY d.name"""
    ).fetchall()

    forecast_rows = conn.execute(
        """SELECT k.id, k.title, e.actual_value
        FROM kpis k JOIN kpi_entries e ON e.kpi_id=k.id
        ORDER BY k.id, e.period"""
    ).fetchall()
    grouped: dict[int, dict[str, Any]] = {}
    for row in forecast_rows:
        grouped.setdefault(row["id"], {"title": row["title"], "values": []})["values"].append(row["actual_value"])

    forecasts = [
        {"kpi_id": kpi_id, "title": v["title"], "forecast_next": forecast_next(v["values"])}
        for kpi_id, v in grouped.items()
    ]

    conn.close()
    return {
        "summary": summary.__dict__,
        "department_kra": [dict(r) for r in dept_rows],
        "forecast": forecasts,
    }


@app.post("/api/v1/alerts/run")
def run_alerts(_: sqlite3.Row = Depends(require_manager)):
    conn = get_db()
    rows = conn.execute(
        """SELECT k.title, k.threshold_pct, k.target_owner_email, e.actual_value, e.target_value
        FROM kpis k JOIN kpi_entries e ON e.kpi_id=k.id
        WHERE k.target_owner_email IS NOT NULL"""
    ).fetchall()
    sent = 0
    for row in rows:
        if row["target_value"] and row["target_value"] > 0:
            pct = (row["actual_value"] / row["target_value"]) * 100
            if pct < row["threshold_pct"]:
                send_email_alert(
                    row["target_owner_email"],
                    f"KPI Alert: {row['title']}",
                    f"KPI {row['title']} is below threshold ({pct:.2f}% < {row['threshold_pct']}%).",
                )
                sent += 1
    conn.close()
    return {"alerts_processed": len(rows), "alerts_sent": sent}


@app.get("/app", response_class=HTMLResponse)
def app_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/v1/me")
def me(user: sqlite3.Row = Depends(get_current_user)):
    return {"id": user["id"], "name": user["full_name"], "role": user["role"], "email": user["email"]}


@app.post("/logout")
def logout(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if token:
        conn = get_db()
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
        conn.close()
    return RedirectResponse("/", status_code=302)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("kpi_tracker.app:app", host="0.0.0.0", port=8000, reload=True)
