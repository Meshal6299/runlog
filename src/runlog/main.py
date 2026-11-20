import os
import sqlite3
from datetime import UTC, date, datetime, timedelta

import jwt
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

app = FastAPI()

hasher = PasswordHash.recommended()
security = HTTPBearer()

def get_connection():
    path = os.getenv("DATABASE_PATH", "runlog.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def get_secret_key():
    return os.environ["SECRET_KEY"]

def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials, get_secret_key(), algorithms=["HS256"]
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])

class RunCreate(BaseModel):
    run_date: date
    distance_km: float
    duration_seconds: int
    run_type: str | None = None
    notes: str | None = None

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/runs")
def list_runs(user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    rows = conn.execute("select * from runs where user_id = ? order by run_date desc",(user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/runs")
def create_run(run: RunCreate,user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    cursor = conn.execute(
        "insert into runs (user_id, run_date, distance_km, duration_seconds, run_type, notes) "
        "values (?, ?, ?, ?, ?, ?)",
        (user_id, run.run_date.isoformat(), run.distance_km, run.duration_seconds, run.run_type, run.notes),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id}

@app.post("/register")
def create_user(user: UserCreate):
    password_hashed = hasher.hash(user.password)
    conn = get_connection()

    try:
        cursor = conn.execute(
            "insert into users (email, password_hash) "
            "values (?, ?)",
            (user.email, password_hashed)
        )
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")
    finally:
        conn.close()
    
    return {"id": new_id, "email": user.email}


@app.post("/login")
def UserLogin(user: UserCreate):
    conn = get_connection()
    try:
        row = conn.execute("select id, password_hash from users where email = ?",(user.email,),).fetchone()
    finally:
        conn.close()

    if row is None or not hasher.verify(user.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    payload = {
        "sub": str(row["id"]),                              # subject: which user this token is for
        "exp": datetime.now(UTC) + timedelta(minutes=30),   # expiry: when the token stops working
    }

    token = jwt.encode(payload, get_secret_key(), algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}