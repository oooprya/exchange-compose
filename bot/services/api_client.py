import aiohttp
import asyncio
from loguru import logger
from typing import Optional, Dict


class APIClient:
    def __init__(
        self,
        base_headers: Optional[Dict] = None,
        timeout: int = 10,
        retries: int = 3,
    ):
        self._session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retries = retries
        self.headers = base_headers or {}

    async def start(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers,
            )
            logger.info("API client started")

    async def close(self):
        if self._session:
            await self._session.close()
            logger.info("API client closed")

    async def get(self, url: str) -> dict:
        return await self._request("GET", url)

    async def patch(self, url: str, json_data: dict) -> dict:
        return await self._request("PATCH", url, json=json_data)

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        for attempt in range(1, self.retries + 1):
            try:
                async with self._session.request(method, url, **kwargs) as resp:
                    resp.raise_for_status()
                    logger.warning(
                        f"{method} {url} attempt {attempt}")
                    # return await resp.json()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"{method} {url} attempt {attempt} failed: {e}")
                if attempt == self.retries:
                    raise
                await asyncio.sleep(0.5 * attempt)
