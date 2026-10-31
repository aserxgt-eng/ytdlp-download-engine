
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yt_dlp import YoutubeDL
import os

app = FastAPI(title="Aadi Download Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {
        "status": "online",
        "engine": "yt-dlp",
        "message": "Download engine is running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/info")
def get_info(request: DownloadRequest):
    if not request.url.startswith(("https://", "http://")):
        raise HTTPException(400, "Invalid URL")

    try:
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }

        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=False)

        return {
            "success": True,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution"),
                    "filesize": f.get("filesize"),
                }
                for f in info.get("formats", [])
                if f.get("url") and f.get("vcodec") != "none"
            ][:30]
        }

    except Exception:
        raise HTTPException(
            400,
            "Unable to extract media information. Check the URL and try again."
        )
