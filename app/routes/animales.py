from fastapi import APIRouter, HTTPException, Request
from app.services.external_apis import fetch_animal_data, fetch_unsplash_image
import httpx

router = APIRouter(prefix="/animales", tags=["Animales"])

@router.get("/buscar-sugerencias")
async def sugerencias(q: str):
    data = await fetch_animal_data(q)
    # Si la API de Ninjas devuelve una lista, tomamos los nombres
    return [data["name"]] if data else []

@router.get("/info/{nombre}")
async def get_animal(nombre: str):
    data = await fetch_animal_data(nombre)
    if not data:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    char = data.get("characteristics", {})
    status = char.get("estimated_population_size", "").lower()
    peligro = any(x in status for x in ["threatened", "endangered", "low", "decreasing", "rare"])
    
    return {
        "nombre": data["name"],
        "reino": data["taxonomy"].get("kingdom", "Animalia"),
        "clase": data["taxonomy"].get("class", "Desconocida"),
        "familia": data["taxonomy"].get("family", "N/A"),
        "en_peligro": peligro
    }

@router.post("/")
async def save_animal(request: Request, animal: dict):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO animales_guardados (nombre, reino, clase, familia, url_imagen, en_peligro)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, animal.get('nombre'), animal.get('reino'), animal.get('clase'), 
                 animal.get('familia'), animal.get('url_imagen'), animal.get('en_peligro', False))
            return {"status": "success"}
        except:
            raise HTTPException(status_code=400, detail="El animal ya existe en tu colección")

@router.get("/")
async def list_animales(request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM animales_guardados")
        return [dict(r) for r in rows]

@router.get("/imagen/{nombre}")
async def get_animal_image(nombre: str):
    url = await fetch_unsplash_image(nombre)
    return {"url_imagen": url}