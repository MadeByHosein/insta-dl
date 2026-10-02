
import os
from fastapi import APIRouter, Header, HTTPException
from .main import queue

router = APIRouter(prefix="/api/admin")

def auth(token: str | None):
    expected = os.getenv("ADMIN_TOKEN")
    if not expected or token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/stats")
async def stats(x_admin_token: str | None = Header(default=None)):
    auth(x_admin_token)
    jobs = list(queue.jobs.values())
    return {
        "jobs_total": len(jobs),
        "queued": sum(j["status"] == "queued" for j in jobs),
        "processing": sum(j["status"] == "processing" for j in jobs),
        "done": sum(j["status"] == "done" for j in jobs),
        "error": sum(j["status"] == "error" for j in jobs),
    }
