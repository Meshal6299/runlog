from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

RunType = Literal["long", "easy", "recovery", "interval", "tempo", "threshold", "race"]

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

class RunCreate(BaseModel):
    run_date: date
    distance_km: float = Field(gt=0)
    duration_seconds: int = Field(gt=0)
    run_type: RunType | None = None
    notes: str | None = None