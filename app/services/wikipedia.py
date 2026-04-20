import httpx


async def fetch_wikipedia_resumen(nombre: str) -> dict | None:
    url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"User-Agent": "WildInfo/1.0"})
        if res.status_code == 200:
            d = res.json()
            return {
                "resumen": d.get("extract"),
                "enlace_articulo": d.get("content_urls", {}).get("desktop", {}).get("page")
            }
        return None