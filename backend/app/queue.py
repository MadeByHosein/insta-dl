
import asyncio
import json
import os
import uuid
from typing import Any, Awaitable, Callable

try:
    import redis.asyncio as redis
except Exception:
    redis = None

class QueueManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_client = None
        self.local_queue = asyncio.Queue()
        self.jobs: dict[str, dict[str, Any]] = {}
        self.workers = []
        self.worker_count = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))

    async def start(self):
        if redis:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
            except Exception:
                self.redis_client = None

        if not self.workers:
            self.workers = [
                asyncio.create_task(self._worker())
                for _ in range(self.worker_count)
            ]

    async def create(self, payload: dict[str, Any]) -> str:
        job_id = uuid.uuid4().hex
        self.jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 0,
            "payload": payload,
            "result": None,
            "error": None,
        }
        await self.local_queue.put(job_id)
        return job_id

    async def _worker(self):
        while True:
            job_id = await self.local_queue.get()
            job = self.jobs.get(job_id)
            if not job:
                self.local_queue.task_done()
                continue
            job["status"] = "processing"
            try:
                from .instagram import download_public_url
                path, filename, temp_dir = await asyncio.to_thread(
                    download_public_url,
                    job["payload"]["url"],
                    job["payload"].get("format_id"),
                )
                job["progress"] = 100
                job["status"] = "done"
                job["result"] = {
                    "path": path,
                    "filename": filename,
                    "temp_dir": temp_dir,
                }
            except Exception as exc:
                job["status"] = "error"
                job["error"] = str(exc)[:500]
            finally:
                self.local_queue.task_done()

    def get(self, job_id: str):
        return self.jobs.get(job_id)

    async def close(self):
        for task in self.workers:
            task.cancel()
        if self.redis_client:
            await self.redis_client.aclose()
