from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("DATABASE_URL")
    try:
        app.state.db_pool = await asyncpg.create_pool(db_url)
        async with app.state.db_pool.acquire() as conn:
            # Tabla de Animales
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS animales_guardados (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    reino VARCHAR(50),
                    clase VARCHAR(50),
                    familia VARCHAR(50),
                    url_imagen TEXT,
                    en_peligro BOOLEAN DEFAULT FALSE
                )
            """)
            # Asegurar columna en_peligro por si la tabla ya existía
            await conn.execute("ALTER TABLE animales_guardados ADD COLUMN IF NOT EXISTS en_peligro BOOLEAN DEFAULT FALSE")
            
            # Tabla de Perfil
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS perfil_usuario (
                    id INT PRIMARY KEY,
                    puntos INT DEFAULT 0,
                    racha_maxima INT DEFAULT 0,
                    badge_oro BOOLEAN DEFAULT FALSE,
                    badge_diversidad BOOLEAN DEFAULT FALSE,
                    rango_titulo VARCHAR(100) DEFAULT 'Observador de Jardín'
                )
            """)
            await conn.execute("INSERT INTO perfil_usuario (id) VALUES (1) ON CONFLICT DO NOTHING")
    except Exception as e:
        print(f"Error BD: {e}")
    yield
    await app.state.db_pool.close()

app = FastAPI(title="WildInfo Atmosférico", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ORIGEN_PERMITIDO")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_NINJS_KEY", "")

@app.get("/buscar-sugerencias")
async def sugerencias(q: str):
    url = f"https://api.api-ninjas.com/v1/animals?name={q.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"X-Api-Key": API_KEY})
        data = res.json()
        return [a["name"] for a in data[:5]] if res.status_code == 200 else []

@app.get("/wildinfo/{nombre}")
async def get_animal(nombre: str):
    url = f"https://api.api-ninjas.com/v1/animals?name={nombre.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"X-Api-Key": API_KEY})
        data = res.json()
        if not data: raise HTTPException(status_code=404)
        char = data[0].get("characteristics", {})
        status = char.get("estimated_population_size", "").lower()
        peligro = any(x in status for x in ["threatened", "endangered", "low", "decreasing", "rare"])
        return {
            "nombre": data[0]["name"],
            "reino": data[0]["taxonomy"].get("kingdom", "Animalia"),
            "clase": data[0]["taxonomy"].get("class", "Desconocida"),
            "familia": data[0]["taxonomy"].get("family", "N/A"),
            "en_peligro": peligro
        }

@app.get("/perfil")
async def get_perfil():
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM perfil_usuario WHERE id = 1")
        return dict(row)

@app.put("/perfil/progreso")
async def update_perfil(d: dict):
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE perfil_usuario SET puntos=$1, racha_maxima=$2, 
            badge_oro=$3, badge_diversidad=$4, rango_titulo=$5 WHERE id=1
        """, d['puntos'], d['racha_maxima'], d['badge_oro'], d['badge_diversidad'], d['rango_titulo'])
        return {"status": "ok"}

@app.post("/animales")
async def save_animal(a: dict):
    async with app.state.db_pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO animales_guardados (nombre, reino, clase, familia, url_imagen, en_peligro)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, a.get('nombre'), a.get('reino'), a.get('clase'), a.get('familia'), a.get('url_imagen'), a.get('en_peligro', False))
            return {"status": "success"}
        except: raise HTTPException(status_code=400, detail="Ya existe")

@app.get("/animales")
async def list_animales():
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM animales_guardados")
        return [dict(r) for r in rows]

@app.delete("/animales/{nombre}")
async def delete_animal(nombre: str):
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM animales_guardados WHERE nombre = $1", nombre)
        return {"status": "deleted"}

@app.get("/api/animal-imagen/{n}")
async def get_img(n: str):
    key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://api.unsplash.com/search/photos?query={n}&per_page=1", 
                               headers={"Authorization": f"Client-ID {key}"})
        data = res.json()
        url = data["results"][0]["urls"]["regular"] if data["results"] else ""
        return {"url_imagen": url}

@app.get("/info-wikipedia/{n}")
async def get_wiki(n: str):
    url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{n}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"User-Agent": "WildInfo/1.0"})
        if res.status_code == 200:
            d = res.json()
            return {"resumen": d.get("extract"), "enlace_articulo": d.get("content_urls",{}).get("desktop",{}).get("page")}
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST"), 
        port=int(os.getenv("PORT"))
    )