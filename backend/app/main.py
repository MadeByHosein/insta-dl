import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from .instagram import extract_gallery

app = FastAPI(title="Public Instagram Downloader", version="2.2.1")

BASE = Path(__file__).resolve().parents[2]
DOWNLOADS = BASE / "downloads"
FRONTEND = BASE / "frontend"

DOWNLOADS.mkdir(exist_ok=True)

app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS)), name="downloads")
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


class DownloadRequest(BaseModel):
    url: HttpUrl


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(str(FRONTEND / "index.html"))


@app.post("/api/gallery")
async def gallery(req: DownloadRequest):
    try:
        return {"items": await extract_gallery(str(req.url))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    return {"ok": True, "version": "2.2.1"}


@app.get("/api/diagnostics")
async def diagnostics():
    return {"ok": True, "version": "2.2.1", "extractor": "edge-gallery"}


@app.get("/how-to-download.html", include_in_schema=False)
async def howto():
    return FileResponse(str(FRONTEND / "how-to-download.html"))


@app.get("/faq.html", include_in_schema=False)
async def faq():
    return FileResponse(str(FRONTEND / "faq.html"))
