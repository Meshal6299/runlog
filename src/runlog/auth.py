import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

hasher = PasswordHash.recommended()
security = HTTPBearer()

def get_secret_key():
    return os.environ["SECRET_KEY"]

def get_current_user_id(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    try:
        payload = jwt.decode(
            credentials.credentials, get_secret_key(), algorithms=["HS256"]
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])