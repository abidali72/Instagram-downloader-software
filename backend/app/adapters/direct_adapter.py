import aiohttp
import re
from typing import Optional
from .base import BaseAdapter, VideoMetadata
from ..core.logger import logger

class DirectAdapter(BaseAdapter):
    PLATFORM_NAME = "Direct Media"
    # Matches URLs containing common video extensions followed by optional parameters
    URL_PATTERN = re.compile(r"https?://.*(\.(mp4|mkv|mov|avi|webm)|[/.](mp4|mkv|mov|avi|webm))(\?.*)?$", re.IGNORECASE)

    def get_platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def validate_url(self, url: str) -> bool:
        return bool(self.URL_PATTERN.match(url))

    async def get_metadata(self, url: str) -> Optional[VideoMetadata]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True) as response:
                    if response.status not in [200, 206]:
                        logger.error(f"Direct URL head request failed: {response.status}")
                        return None
                    
                    content_type = response.headers.get("Content-Type", "")
                    if "video" not in content_type and "application/octet-stream" not in content_type:
                        logger.warning(f"URL does not appear to be a video: {content_type}")
                        return None

                    file_size = int(response.headers.get("Content-Length", 0))
                    
                    return VideoMetadata(
                        id="direct-" + str(hash(url)),
                        title=url.split("/")[-1].split("?")[0] or "Direct Video",
                        duration=0, # Duration often not available in headers
                        thumbnail="https://via.placeholder.com/200x120?text=Direct+Video",
                        qualities=[{
                            "id": "original",
                            "label": f"Original ({round(file_size / (1024*1024), 2)} MB)",
                            "url": url,
                            "file_type": content_type
                        }],
                        platform=self.PLATFORM_NAME,
                        url=url
                    )
        except Exception as e:
            logger.error(f"Error fetching direct metadata: {e}")
            return None
