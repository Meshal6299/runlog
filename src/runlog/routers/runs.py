#routers/runs.py
from fastapi import APIRouter, Depends, HTTPException

from runlog.auth import get_current_user_id
from runlog.database import get_connection
from runlog.schemas import RunCreate, RunType

router = APIRouter()

@router.get("/runs")
def list_runs(user_id: int = Depends(get_current_user_id), run_type: RunType | None = None, min_km: float | None = None, max_km: float | None = None, q: str | None = None,):
    conn = get_connection()

    conditions = ["user_id = ?"]
    values = [user_id]

    if run_type is not None:
        conditions.append("run_type = ?")
        values.append(run_type)

    if min_km is not None:
        conditions.append("distance_km >= ?")
        values.append(min_km)

    if max_km is not None:
        conditions.append("distance_km <= ?")
        values.append(max_km)

    if q is not None:
        conditions.append("notes like ?")
        values.append(f"%{q}%")

    sql = "select * from runs where " + " and ".join(conditions) + " order by run_date desc"

    rows = conn.execute(sql, values).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/runs")
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

@router.delete("/runs/{run_id}")
def delete_run(run_id: int, user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "delete from runs where id = ? and user_id = ?", 
            (run_id,user_id),
        )
        conn.commit()
    finally:
        conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Run not found")


    return {"id": run_id}

@router.put("/runs/{run_id}")
def update_run(run_id: int, run: RunCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "update runs set run_date = ?, distance_km = ?, duration_seconds = ?, "
            "run_type = ?, notes = ? "
            "where id = ? and user_id = ?",
            (run.run_date.isoformat(), run.distance_km, run.duration_seconds, run.run_type, run.notes, run_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"id": run_id}