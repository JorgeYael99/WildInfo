import httpx
from core.config import settings


async def fetch_animal_data(nombre: str) -> dict | None:
    url = f"https://api.api-ninjas.com/v1/animals?name={nombre.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"X-Api-Key": settings.api_ninjas_key})
        data = res.json()
        return data[0] if data else None


async def fetch_sugerencias(q: str) -> list[str]:
    url = f"https://api.api-ninjas.com/v1/animals?name={q.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"X-Api-Key": settings.api_ninjas_key})
        data = res.json()
        return [a["name"] for a in data[:5]] if res.status_code == 200 else []