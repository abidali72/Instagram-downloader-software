from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.logger import logger
from .adapters.factory import adapter_factory
from .services.download_manager import download_manager
from fastapi.responses import StreamingResponse
from typing import Optional

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Legal Video Downloader API is running"}

@app.post("/api/v1/metadata")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_video_metadata(request: Request, url_data: dict):
    url = url_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    adapter = adapter_factory.get_adapter(url)
    if not adapter:
        logger.warning(f"Unsupported URL: {url}")
        raise HTTPException(status_code=400, detail="Unsupported or restricted platform. If using Instagram, try a direct media URL.")
    
    metadata = await adapter.get_metadata(url)
    if not metadata:
        raise HTTPException(status_code=404, detail="Could not retrieve video metadata. Check URL or direct link accessibility.")
    
    return metadata

@app.get("/api/v1/download")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def download_video(request: Request, url: str, range: Optional[str] = Header(None)):
    if not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Invalid download URL")
    
    stream_gen = download_manager.stream_video(url, range)
    
    # Get the first item which is the response headers from the source
    try:
        source_headers = await stream_gen.__anext__()
    except StopAsyncIteration:
        raise HTTPException(status_code=500, detail="Empty stream from source")

    # Map necessary headers back to our response
    response_headers = {
        "Content-Type": source_headers.get("Content-Type", "video/mp4"),
        "Accept-Ranges": "bytes",
        "Content-Disposition": f"attachment; filename=video.mp4"
    }
    
    if "Content-Range" in source_headers:
        response_headers["Content-Range"] = source_headers["Content-Range"]
    if "Content-Length" in source_headers:
        response_headers["Content-Length"] = source_headers["Content-Length"]

    status_code = 206 if range else 200

    return StreamingResponse(
        stream_gen,
        status_code=status_code,
        headers=response_headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
