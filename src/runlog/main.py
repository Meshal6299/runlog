from contextlib import asynccontextmanager

from fastapi import FastAPI

from runlog.database import init_db
from runlog.routers import runs, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(users.router)
app.include_router(runs.router)

@app.get("/health")
def health():
    return {"status": "ok"}


