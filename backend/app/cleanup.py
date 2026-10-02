
import asyncio
import os
import shutil
import time

STORAGE_DIR = os.getenv("STORAGE_DIR", "/app/storage")
TTL = int(os.getenv("FILE_TTL_SECONDS", "1800"))

async def cleanup_loop():
    while True:
        try:
            now = time.time()
            if os.path.isdir(STORAGE_DIR):
                for name in os.listdir(STORAGE_DIR):
                    path = os.path.join(STORAGE_DIR, name)
                    try:
                        if now - os.path.getmtime(path) > TTL:
                            if os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                            else:
                                os.remove(path)
                    except OSError:
                        pass
        finally:
            await asyncio.sleep(300)
