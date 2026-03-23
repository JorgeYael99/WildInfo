from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import time
from dotenv import load_dotenv
import os
import asyncpg

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("DATABASE_URL")
    try:
        app.state.db_pool = await asyncpg.create_pool(db_url)
        async with app.state.db_pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS animales_guardados (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    reino VARCHAR(50),
                    clase VARCHAR(50),
                    familia VARCHAR(50),
                    url_imagen TEXT
                )
            """)
    except Exception as e:
        print(f"ERROR: {e}")
    yield
    await app.state.db_pool.close()

app = FastAPI(title="WildInfo", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_NINJA_KEY = os.getenv("API_NINJS_KEY", "")

@app.get("/buscar-sugerencias")
async def buscar_sugerencias(q: str):
    url = f"https://api.api-ninjas.com/v1/animals?name={q.lower()}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"X-Api-Key": API_NINJA_KEY})
        if response.status_code == 200:
            data = response.json()
            return [animal["name"] for animal in data[:5]]
        return []

@app.get("/wildinfo/{name_or_id}")
async def get_animal(name_or_id: str):
    url = f"https://api.api-ninjas.com/v1/animals?name={name_or_id.lower()}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"X-Api-Key": API_NINJA_KEY})
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail="Animal no encontrado")
        
        # Agregamos lógica para "En Peligro" simulada o basada en taxonomía
        # La API de Ninjas a veces trae 'conservation_status' en 'characteristics'
        charac = data[0].get("characteristics", {})
        status = charac.get("estimated_population_size", "").lower()
        en_peligro = "threatened" in status or "endangered" in status or "low" in status

        return {
            "nombre": data[0]["name"],
            "reino": data[0]["taxonomy"].get("kingdom", "N/A"),
            "clase": data[0]["taxonomy"].get("class", "N/A"),
            "familia": data[0]["taxonomy"].get("family", "N/A"),
            "en_peligro": en_peligro
        }

@app.post("/animales")
async def guardar_animal(animal: dict):
    async with app.state.db_pool.acquire() as connection:
        try:
            await connection.execute("""
                INSERT INTO animales_guardados (nombre, reino, clase, familia, url_imagen)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                animal.get("nombre"), animal.get("reino"), 
                animal.get("clase"), animal.get("familia"),
                animal.get("url_imagen")
            )
            return {"status": "success"}
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Ya está en favoritos")

@app.get("/animales")
async def listar_animales():
    async with app.state.db_pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM animales_guardados")
        return [dict(row) for row in rows]

@app.delete("/animales/{nombre}")
async def eliminar_animal(nombre: str):
    async with app.state.db_pool.acquire() as connection:
        result = await connection.execute(
            "DELETE FROM animales_guardados WHERE nombre = $1", 
            nombre
        )
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="No se encontró el favorito")
        return {"status": "success", "message": f"{nombre} eliminado."}

@app.get("/api/animal-imagen/{nombre}")
async def obtener_imagen_animal(nombre: str):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {access_key}"},
            params={"query": nombre, "per_page": 1}
        )
        if response.status_code == 200:
            datos = response.json()
            url = datos["results"][0]["urls"]["regular"] if datos["results"] else ""
            return {"url_imagen": url}
        return {"url_imagen": ""}

@app.get("/info-wikipedia/{nombre_animal}")
async def obtener_info_wikipedia(nombre_animal: str):
    url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre_animal}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"User-Agent": "WildInfoApp/1.0"})
        if response.status_code == 200:
            datos = response.json()
            return {
                "resumen": datos.get("extract"),
                "enlace_articulo": datos.get("content_urls", {}).get("desktop", {}).get("page")
            }
        return None