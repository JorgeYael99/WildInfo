from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import time

app = FastAPI(title="WildInfo")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permitimos que cualquier frontend se conecte
    allow_credentials=True,
    allow_methods=["*"],        # Permitimos todos los verbos (GET, POST, etc.)
    allow_headers=["*"],
)

@app.middleware("http")
async def long_request (request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    print(
        f"DEBUG: {request.method} {request.url.path}"
        f"- Status: {response.status_code}"
        f"- {process_time:.2f}ms"
    )

    return response

@app.get("/")
async def root():
    return {"message": "Servidor WildInfo Arriba", "status": 200}



# --------------------------------------------------
# 5. CONSUMO DE SERVICIO WEB EXTERNO (PokéAPI)
# --------------------------------------------------
@app.get("/wildinfo/{name}")
async def get_animal(name: str):
    external_url = f"https://api.api-ninjas.com/v1/animals?name={name.lower()}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_url)

            print(f"DEBUG EXTERNO: PokéAPI respondió con {response.status_code}")

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="animal no encontrado"
                )

            data = response.json()

            # Transformación / mapeo de datos
            animal_data = {
                "nombre": data["name"],
                "Reino": [t["type"]["name"] for t in data["types"]],
                "altura": data["height"],
                "peso": data["weight"],
                "imagen": data["sprites"]["other"]["official-artwork"]["front_default"]
            }

            return animal_data

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Servicio externo no disponible"
            )



# --- MONITOR DE CONSOLA (Middleware para ver estados HTTP) ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Imprime en consola: MÉTODO | RUTA | ESTADO | TIEMPO
    print(f"DEBUG: {request.method} {request.url.path} - Status: {response.status_code} - {process_time:.2f}ms")
    return response

# --- 2.2 MÉTODOS DEL SERVICIO WEB ---

# Punto de entrada para el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)