import httpx
from fastapi import APIRouter, HTTPException, Request, Header
from app.services.api_ninjas import fetch_animal_data, fetch_sugerencias
from app.services.unsplash import fetch_unsplash_image
from app.services.wikipedia import fetch_wikipedia_resumen
from app.core.config import settings

router = APIRouter(prefix="/animales", tags=["Animales"])

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key is not None and x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Firma digital no válida")

def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not user_id or not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"user_id": int(user_id), "username": username}

def validar_taxonomia_fauna(data: dict, nombre: str):
    """Función de validación estricta para asegurar que pertenezca exclusivamente al Reino Animalia."""
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"El término '{nombre}' no fue encontrado en el catálogo científico zoológico."
        )
        
    taxonomia = data.get("taxonomy", {})
    reino = taxonomia.get("kingdom", "").lower()
    clase = taxonomia.get("class", "")
    familia = taxonomia.get("family", "")
    
    # 1. Validación de Reino
    if reino and reino != "animalia":
        raise HTTPException(
            status_code=400, 
            detail=f"El término '{nombre}' pertenece al reino '{taxonomia.get('kingdom')}'. WildInfo es exclusivo para el reino Animalia."
        )
        
    # 2. Doble blindaje estricto (Detecta si faltan datos de clase o familia biológica)
    if not clase or clase.lower() in ["", "n/a", "none", "desconocida"] or not familia or familia.lower() in ["", "n/a", "none"]:
        raise HTTPException(
            status_code=400,
            detail=f"El término '{nombre}' no posee una estructura taxonómica de fauna válida. WildInfo es exclusivo para animales."
        )

@router.get("/buscar-sugerencias")
async def sugerencias(q: str):
    return await fetch_sugerencias(q)

@router.get("/info/{nombre}")
async def get_animal(nombre: str):
    data = await fetch_animal_data(nombre)
    validar_taxonomia_fauna(data, nombre)
    
    char = data.get("characteristics", {}) if data.get("characteristics") else {}
    
    status_poblacion = str(char.get("estimated_population_size", "")).lower()
    status_conservacion = str(char.get("conservation_status", "")).lower()
    
    palabras_riesgo = ["threatened", "endangered", "low", "decreasing", "rare", "critically", "vulnerable"]
    peligro = any(x in status_poblacion or x in status_conservacion for x in palabras_riesgo)
    
    return {
        "nombre": data.get("name", nombre),
        "reino": data.get("taxonomy", {}).get("kingdom", "Animalia"),
        "clase": data.get("taxonomy", {}).get("class", "Desconocida"),
        "familia": data.get("taxonomy", {}).get("family", "N/A"),
        "en_peligro": peligro,
        "slogan": char.get("slogan") or "No disponible",
        "habitat": char.get("habitat") or "No disponible",
        "dieta": char.get("diet") or char.get("main_prey") or "No disponible",
        "longevidad": char.get("lifespan") or "No disponible",
        "peso": char.get("weight") or "No disponible",
        "velocidad": char.get("top_speed") or "No disponible",
        "ubicaciones": data.get("locations") or []
    }

@router.post("/")
async def save_animal(request: Request, animal: dict, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
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
async def delete_animal(request: Request, nombre: str, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
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
    data = await fetch_animal_data(nombre)
    validar_taxonomia_fauna(data, nombre)
    
    nombre_oficial = data.get("name", nombre)
    nombre_cientifico = data.get("taxonomy", {}).get("scientific_name")
    familia = data.get("taxonomy", {}).get("family")
        
    return await fetch_wikipedia_resumen(nombre_oficial, nombre_cientifico=nombre_cientifico, familia=familia)

def _normalizar_nombre_cientifico(nombre: str) -> str:
    """Convierte 'PANTHERA TIGRIS TIGRIS' → 'Panthera tigris' (solo género y especie)."""
    partes = nombre.strip().split()
    if len(partes) >= 2:
        genus = partes[0].capitalize()
        species = partes[1].lower()
        return f"{genus} {species}"
    return nombre.strip()

@router.get("/mapa-calor/{nombre}")
async def get_heatmap_data(nombre: str):
    data = await fetch_animal_data(nombre)
    if not data:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    
    scientific_name = data.get("taxonomy", {}).get("scientific_name")
    common_name = data.get("name", nombre)
    
    search_names = []
    if scientific_name:
        normalized = _normalizar_nombre_cientifico(scientific_name)
        if normalized not in ("", "n/a", "none", "unknown"):
            search_names.append(normalized)
    if common_name and common_name.lower() not in ("", "n/a", "none", "unknown"):
        search_names.append(common_name)
    if nombre not in search_names:
        search_names.append(nombre)
    
    try:
        async with httpx.AsyncClient() as client:
            for attempt_name in search_names:
                try:
                    resp = await client.get(
                        "https://api.gbif.org/v1/species/match",
                        params={"name": attempt_name, "kingdom": "Animalia"},
                        timeout=8.0
                    )
                    if resp.status_code == 200:
                        gb = resp.json()
                        if gb.get("usageKey") and gb.get("matchType") not in ("HIGHERRANK",):
                            return {"taxon_key": gb["usageKey"], "nombre_cientifico": gb.get("scientificName", attempt_name)}
                except Exception:
                    continue
    except Exception as e:
        print(f"Error consultando GBIF: {e}")
    
    return {"taxon_key": None, "nombre_cientifico": scientific_name or common_name}