import aiohttp
from ..core.logger import logger

class DownloadManager:
    @staticmethod
    async def stream_video(url: str, range_header: str = None):
        """
        Streams a video from a URL to the client, supporting Range requests.
        """
        headers = {}
        if range_header:
            headers["Range"] = range_header

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status not in [200, 206]:
                    logger.error(f"Failed to fetch video stream: {response.status}")
                    yield b""
                    return
                
                # First yield the headers so main.py can use them
                yield response.headers
                
                async for chunk in response.content.iter_any():
                    yield chunk

download_manager = DownloadManager()
