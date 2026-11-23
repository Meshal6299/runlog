from fastapi import FastAPI

from runlog.routers import runs, users

app = FastAPI()
app.include_router(users.router)
app.include_router(runs.router)

@app.get("/health")
def health():
    return {"status": "ok"}
