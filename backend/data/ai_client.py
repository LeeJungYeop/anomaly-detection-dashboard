import httpx

from config import AI_MODEL_URL


async def call(filename: str, file_bytes: bytes) -> dict:
    async with httpx.AsyncClient() as client:
        files = {"file": (filename, file_bytes)}
        response = await client.post(AI_MODEL_URL, files=files)
        response.raise_for_status()
        return response.json()
