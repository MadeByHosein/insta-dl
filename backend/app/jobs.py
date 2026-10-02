
import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Job:
    id: str
    status: str = "queued"
    progress: int = 0
    result: dict[str, Any] | None = None
    error: str | None = None

class JobQueue:
    def __init__(self, workers: int = 2):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.jobs: dict[str, Job] = {}
        self.workers = workers
        self.tasks = []

    async def start(self):
        if self.tasks:
            return
        self.tasks = [asyncio.create_task(self._worker()) for _ in range(self.workers)]

    async def _worker(self):
        while True:
            job_id, fn = await self.queue.get()
            job = self.jobs[job_id]
            job.status = "processing"
            try:
                job.result = await fn(job)
                job.progress = 100
                job.status = "done"
            except Exception as exc:
                job.error = str(exc)[:500]
                job.status = "error"
            finally:
                self.queue.task_done()

    async def submit(self, fn):
        job_id = uuid.uuid4().hex
        self.jobs[job_id] = Job(id=job_id)
        await self.queue.put((job_id, fn))
        return self.jobs[job_id]

    def get(self, job_id: str):
        return self.jobs.get(job_id)
