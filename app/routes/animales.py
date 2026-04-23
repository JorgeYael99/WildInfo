from fastapi import APIRouter, HTTPException, Request, Header, Depends
from services.api_ninjas import fetch_animal_data, fetch_sugerencias
from services.unsplash import fetch_unsplash_image
from services.wikipedia import fetch_wikipedia_resumen
from core.config import settings

router = APIRouter(prefix="/animales", tags=["Animales"])

def verificar_firma(x_api_key: str = Header(None)):
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Firma digital no válida o ausente")

@router.get("/buscar-sugerencias")
async def sugerencias(q: str):
    return await fetch_sugerencias(q)

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

@router.post("/", dependencies=[Depends(verificar_firma)])
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

@router.delete("/{nombre}", dependencies=[Depends(verificar_firma)])
async def delete_animal(request: Request, nombre: str):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM animales_guardados WHERE nombre = $1", nombre)
        return {"status": "deleted"}

@router.get("/imagen/{nombre}")
async def get_animal_image(nombre: str):
    url = await fetch_unsplash_image(nombre)
    return {"url_imagen": url}

@router.get("/wikipedia/{nombre}")
async def get_wikipedia(nombre: str):
    return await fetch_wikipedia_resumen(nombre)