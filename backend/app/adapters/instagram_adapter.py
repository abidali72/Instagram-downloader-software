import re
from typing import Optional
from .base import BaseAdapter, VideoMetadata
from ..core.logger import logger

class InstagramAdapter(BaseAdapter):
    PLATFORM_NAME = "Instagram"
    # Matches Reels, Posts, and Stories
    URL_PATTERN = re.compile(r"https?://(www\.)?instagram\.com/(reel|p|stories)/[^/]+/?.*")

    def get_platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def validate_url(self, url: str) -> bool:
        return bool(self.URL_PATTERN.match(url))

    async def get_metadata(self, url: str) -> Optional[VideoMetadata]:
        # Instagram standard URLs require authentication/API tokens for metadata.
        # We return a dummy metadata with instructions to use a direct link.
        return VideoMetadata(
            id="ig-instruction",
            title="Instagram Media (Requires Direct Link)",
            duration=0,
            thumbnail="https://www.instagram.com/static/images/ico/favicon-192.png/b0a233632a51.png",
            qualities=[],
            platform=self.PLATFORM_NAME,
            url=url
        )
