from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="WildInfo")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permitimos que cualquier frontend se conecte
    allow_methods=["*"],        # Permitimos todos los verbos (GET, POST, etc.)
    allow_headers=["*"],
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
@app.get("/")
async def root():
    return {"message": "Servidor WildInfo Arriba", "status": 200}

# Punto de entrada para el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)