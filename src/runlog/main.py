from fastapi import FastAPI
from pydantic import BaseModel

import sqlite3

app = FastAPI()

class RunCreate(BaseModel):
    run_date: str
    distance_km: float
    duration_seconds: int
    run_type: str | None = None
    notes: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/runs")
def list_runs():
    conn = sqlite3.connect("./runlog.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("select * from runs").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/runs")
def create_run(run: RunCreate):
    conn = sqlite3.connect("./runlog.db")
    cursor = conn.execute(
        "insert into runs (user_id, run_date, distance_km, duration_seconds, run_type, notes) "
        "values (?, ?, ?, ?, ?, ?)",
        (1, run.run_date, run.distance_km, run.duration_seconds, run.run_type, run.notes),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id}
    

