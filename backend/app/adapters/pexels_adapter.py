import re
import aiohttp
from typing import Optional
from .base import BaseAdapter, VideoMetadata
from ..core.config import settings
from ..core.logger import logger

class PexelsAdapter(BaseAdapter):
    PLATFORM_NAME = "Pexels"
    URL_PATTERN = re.compile(r"https?://(www\.)?pexels\.com/video/[^/]+-(\d+)/?")

    def get_platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def validate_url(self, url: str) -> bool:
        return bool(self.URL_PATTERN.match(url))

    async def get_metadata(self, url: str) -> Optional[VideoMetadata]:
        match = self.URL_PATTERN.match(url)
        if not match:
            return None
        
        video_id = match.group(2)
        api_url = f"https://api.pexels.com/videos/videos/{video_id}"
        
        headers = {"Authorization": settings.PEXELS_API_KEY}
        
        if not settings.PEXELS_API_KEY:
            logger.warning("Pexels API key missing. Cannot fetch metadata.")
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Pexels API error: {response.status}")
                    return None
                
                data = await response.json()
                
                # Extract qualities
                qualities = []
                for file in data.get("video_files", []):
                    qualities.append({
                        "id": str(file.get("id")),
                        "label": f"{file.get('quality')} ({file.get('width')}x{file.get('height')})",
                        "url": file.get("link"),
                        "file_type": file.get("file_type")
                    })

                return VideoMetadata(
                    id=str(data.get("id")),
                    title=f"Pexels Video {data.get('id')}",
                    duration=data.get("duration", 0),
                    thumbnail=data.get("image"),
                    qualities=qualities,
                    platform=self.PLATFORM_NAME,
                    url=url
                )
