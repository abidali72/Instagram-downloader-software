from typing import List, Optional
from .base import BaseAdapter
from .pexels_adapter import PexelsAdapter
from .direct_adapter import DirectAdapter
from .instagram_adapter import InstagramAdapter

class AdapterFactory:
    def __init__(self):
        self._adapters: List[BaseAdapter] = [
            PexelsAdapter(),
            DirectAdapter(),
            InstagramAdapter()
        ]

    def get_adapter(self, url: str) -> Optional[BaseAdapter]:
        for adapter in self._adapters:
            if adapter.URL_PATTERN.match(url):
                return adapter
        return None

adapter_factory = AdapterFactory()
