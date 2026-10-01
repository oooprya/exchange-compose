import aiohttp
from config import API_BASE, API_KEY

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json",
}


class APIClient:

    def __init__(self):
        self.base = API_BASE

    async def get(self, path, params=None):

        async with aiohttp.ClientSession(headers=HEADERS) as session:

            async with session.get(
                f"{self.base}{path}",
                params=params,
                timeout=15
            ) as resp:

                resp.raise_for_status()

                return await resp.json()

    async def post(self, path, json=None):

        async with aiohttp.ClientSession(headers=HEADERS) as session:

            async with session.post(
                f"{self.base}{path}",
                json=json,
                timeout=15
            ) as resp:

                if resp.status >= 400:
                    error_body = await resp.text()
                    raise RuntimeError(
                        f"API POST {path} failed with HTTP {resp.status}: "
                        f"{error_body[:1000]}"
                    )

                return await resp.json()

    async def patch(self, path, json=None):

        async with aiohttp.ClientSession(headers=HEADERS) as session:

            async with session.patch(
                f"{self.base}{path}",
                json=json,
                timeout=15
            ) as resp:

                resp.raise_for_status()

                return await resp.json()


api = APIClient()