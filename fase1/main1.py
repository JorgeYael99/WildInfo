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
        print("DEBUG: Base de datos PostgreSQL lista y conectada.")
    except Exception as e:
        print(f"ERROR conectando a PostgreSQL: {e}")
        
    yield
    
    await app.state.db_pool.close()
    print("DEBUG: Conexión a PostgreSQL cerrada.")

app = FastAPI(title="WildInfo", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Servidor WildInfo Arriba", "status": 200}

@app.get("/wildinfo/{name_or_id}")
async def get_animal(name_or_id: str):
    external_url = f"https://api.api-ninjas.com/v1/animals?name={name_or_id.lower()}"
    api_key = os.getenv("API_NINJS_KEY", "")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_url, headers={"X-Api-Key": api_key})

            print(f"DEBUG EXTERNO: Ninjas API respondió con {response.status_code}")

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="animal no encontrado"
                )

            data = response.json()

            animal_data = {
                "nombre": data[0]["name"],
                "reino": data[0]["taxonomy"]["kingdom"],
                "clase": data[0]["taxonomy"]["class"],
                "familia": data[0]["taxonomy"]["family"]
            }

            return animal_data

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Servicio externo no disponible"
                )

@app.post("/animales")
async def guardar_animal(animal: dict):
    async with app.state.db_pool.acquire() as connection:
        try:
            await connection.execute("""
                INSERT INTO animales_guardados (nombre, reino, clase, familia, url_imagen)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                animal.get("nombre"), 
                animal.get("reino"), 
                animal.get("clase"), 
                animal.get("familia"),
                animal.get("url_imagen")
            )
            return {"status": "success", "message": f"{animal.get('nombre')} guardado en la BD."}
            
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Este animal ya está guardado.")

@app.get("/animales")
async def listar_animales():
    async with app.state.db_pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM animales_guardados")
        
        animales = [dict(row) for row in rows]
        return animales

@app.get("/api/animal-imagen/{nombre}")
async def obtener_imagen_animal(nombre: str):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    base_url = "https://api.unsplash.com"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/search/photos",
            headers={
                "Accept-Version": "v1",
                "Authorization": f"Client-ID {access_key}"
            },
            params={"query": nombre}
        )
        
        if response.status_code == 200:
            datos = response.json()
            if datos["results"]:
                return {
                    "url_imagen": datos["results"][0]["urls"]["regular"],
                    "descripcion": datos["results"][0]["alt_description"] or "Sin descripción"
                }
            else:
                raise HTTPException(status_code=404, detail="No se encontraron imágenes")
        else:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Error al obtener imagen de Unsplash: {response.text}"
            )

@app.get("/info-wikipedia/{nombre_animal}")
async def obtener_info_wikipedia(nombre_animal: str):
    url_wikipedia = f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre_animal}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url_wikipedia,
            headers={"User-Agent": "WildInfoApp/1.0 (jorg.yael99@gmail.com)"}
        )
        
        if response.status_code == 200:
            datos = response.json()
            return {
                "nombre_oficial": datos.get("title"),
                "resumen": datos.get("extract"),
                "enlace_articulo": datos.get("content_urls", {}).get("desktop", {}).get("page")
            }
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"No se encontró: {nombre_animal}")
        else:
            raise HTTPException(status_code=502, detail="Error con Wikipedia")

@app.middleware("/http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    print(f"DEBUG: {request.method} {request.url.path} - Status: {response.status_code} - {process_time:.2f}ms")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
