from fastapi import APIRouter, HTTPException, Request
from app.services.api_ninjas import fetch_animal_data, fetch_sugerencias
from app.services.unsplash import fetch_unsplash_image
from app.services.wikipedia import fetch_wikipedia_resumen

router = APIRouter(prefix="/animales", tags=["Animales"])

def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not user_id or not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"user_id": int(user_id), "username": username}

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
        "en_peligro": peligro,
        "slogan": char.get("slogan", ""),
        "habitat": char.get("habitat", ""),
        "dieta": char.get("diet", ""),
        "longevidad": char.get("lifespan", ""),
        "peso": char.get("weight", ""),
        "velocidad": char.get("top_speed", "")
    }

@router.post("/")
async def save_animal(request: Request, animal: dict):
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO animales_guardados (usuario_id, nombre, reino, clase, familia, url_imagen, en_peligro)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, user_id, animal.get('nombre'), animal.get('reino'), animal.get('clase'), 
                 animal.get('familia'), animal.get('url_imagen'), animal.get('en_peligro', False))
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=400, detail="El animal ya existe en tu colección")

@router.get("/")
async def list_animales(request: Request):
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM animales_guardados WHERE usuario_id = $1", user_id)
        return [dict(r) for r in rows]

@router.delete("/{nombre}")
async def delete_animal(request: Request, nombre: str):
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM animales_guardados WHERE nombre = $1 AND usuario_id = $2", nombre, user_id)
        return {"status": "deleted"}

@router.get("/imagen/{nombre}")
async def get_animal_image(nombre: str):
    url = await fetch_unsplash_image(nombre)
    return {"url_imagen": url}

@router.get("/wikipedia/{nombre}")
async def get_wikipedia(nombre: str):
    return await fetch_wikipedia_resumen(nombre)