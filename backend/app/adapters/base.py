from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional

class VideoMetadata(BaseModel):
    id: str
    title: str
    duration: int
    thumbnail: str
    qualities: List[dict]  # List of {label: "1080p", url: "...", size: 12345}
    platform: str
    url: str

class BaseAdapter(ABC):
    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        pass

    @abstractmethod
    async def get_metadata(self, url: str) -> Optional[VideoMetadata]:
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        pass
