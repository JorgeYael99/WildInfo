import httpx
from core.config import settings


async def fetch_unsplash_image(nombre: str) -> str:
    url = f"https://api.unsplash.com/search/photos?query={nombre}&per_page=1"
    async with httpx.AsyncClient() as client:
        res = await client.get(
            url,
            headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"}
        )
        data = res.json()
        return data["results"][0]["urls"]["regular"] if data.get("results") else ""