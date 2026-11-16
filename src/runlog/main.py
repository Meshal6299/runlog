import os
import sqlite3
from datetime import date

from fastapi import FastAPI, HTTPException
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

app = FastAPI()

hasher = PasswordHash.recommended()

def get_connection():
    path = os.getenv("DATABASE_PATH", "runlog.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

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
def list_runs():
    conn = get_connection()
    rows = conn.execute("select * from runs").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/runs")
def create_run(run: RunCreate):
    conn = get_connection()
    cursor = conn.execute(
        "insert into runs (user_id, run_date, distance_km, duration_seconds, run_type, notes) "
        "values (?, ?, ?, ?, ?, ?)",
        (1, run.run_date.isoformat(), run.distance_km, run.duration_seconds, run.run_type, run.notes),
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
    

