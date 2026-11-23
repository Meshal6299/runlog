import sqlite3
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException

router = APIRouter()

from runlog.auth import get_secret_key, hasher
from runlog.database import get_connection
from runlog.schemas import UserCreate


@router.post("/register")
def create_user(user: UserCreate):
    password_hashed = hasher.hash(user.password)
    conn = get_connection()

    try:
        cursor = conn.execute(
            "insert into users (email, password_hash) "
            "values (?, ?)",
            (user.email.lower(), password_hashed)
        )
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")
    finally:
        conn.close()
    
    return {"id": new_id, "email": user.email}

@router.post("/login")
def UserLogin(user: UserCreate):
    conn = get_connection()
    try:
        row = conn.execute("select id, password_hash from users where email = ?",(user.email.lower(),),).fetchone()
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