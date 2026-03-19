# Importaciones de librerías necesarias
from fastapi import FastAPI, Request, HTTPException  # FastAPI para crear el servidor, Request para manejar peticiones, HTTPException para errores HTTP
from fastapi.middleware.cors import CORSMiddleware  # Middleware para configurar CORS (Cross-Origin Resource Sharing)
import httpx  # Cliente HTTP asíncrono para hacer peticiones a APIs externas
import time  # Módulo para medir tiempo de ejecución
from dotenv import load_dotenv  # Función para cargar variables de entorno desde archivo .env
import os  # Módulo para acceder a variables de entorno del sistema

# Carga las variables definidas en el archivo .env (como API_NINJS_KEY)
load_dotenv()

# Crea la instancia de la aplicación FastAPI con un título
app = FastAPI(title="WildInfo")

# --- CONFIGURACIÓN DE CORS ---
# Añade el middleware de CORS para permitir conexiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,  # Clase del middleware de CORS de FastAPI
    allow_origins=["*"],        # Permitimos que cualquier frontend se conecte (sin restricciones de dominio)
    allow_credentials=True,     # Permitimos el envío de cookies/credenciales en las peticiones
    allow_methods=["*"],        # Permitimos todos los verbos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],        # Permitimos todos los encabezados en las peticiones
)

# Define una ruta GET en la raíz ("/") que responde con un mensaje de estado
@app.get("/")
async def root():
    return {"message": "Servidor WildInfo Arriba", "status": 200}



# --------------------------------------------------
# CONSUMO DE SERVICIO WEB EXTERNO (Ninjas API)
# --------------------------------------------------
# Endpoint GET que recibe un nombre o ID de animal y consulta la API externa de Ninjas
@app.get("/wildinfo/{name_or_id}")  # Ruta dinámica: {name_or_id} captura el valor de la URL
async def get_animal(name_or_id: str):  # Función asíncrona que recibe el nombre del animal como parámetro
    # Construye la URL completa para la API externa, convirtiendo el nombre a minúsculas
    external_url = f"https://api.api-ninjas.com/v1/animals?name={name_or_id.lower()}"
    # Obtiene la clave de API desde las variables de entorno, usa cadena vacía si no existe
    api_key = os.getenv("API_NINJS_KEY", "")

    # Crea un cliente HTTP asíncrono para hacer la petición
    async with httpx.AsyncClient() as client:
        try:
            # Realiza la petición GET a la API externa, incluyendo la cabecera de autenticación
            response = await client.get(external_url, headers={"X-Api-Key": api_key})

            # Imprime en consola el código de estado recibido de la API externa (para depuración)
            print(f"DEBUG EXTERNO: Ninjas API respondió con {response.status_code}")

            # Si la API responde con 404, el animal no fue encontrado - lanzamos excepción
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,  # Código de error HTTP 404 (No encontrado)
                    detail="animal no encontrado"  # Mensaje de error personalizado
                )

            # Convierte la respuesta JSON a un diccionario de Python
            data = response.json()

            # Extrae solo los campos relevantes del animal y los guarda en un diccionario
            animal_data = {
                "nombre": data[0]["name"],           # Nombre común del animal
                "reino": data[0]["taxonomy"]["kingdom"],  # Reino (ej: Animalia)
                "clase": data[0]["taxonomy"]["class"],     # Clase (ej: Mammalia)
                "familia": data[0]["taxonomy"]["family"]  # Familia (ej: Felidae)
            }

            # Retorna los datos del animal como respuesta JSON
            return animal_data

        # Si ocurre un error de conexión con la API externa, capturamos la excepción
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,  # Código de error 503 (Servicio no disponible)
                detail="Servicio externo no disponible"  # Mensaje de error
            )



@app.middleware("/http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    print(f"DEBUG: {request.method} {request.url.path} - Status: {response.status_code} - {process_time:.2f}ms")
    
    return response

# --- PUNTO DE ENTRADA DEL SERVIDOR ---
# Este bloque solo se ejecuta cuando el archivo se corre directamente (no cuando se importa)
if __name__ == "__main__":
    import uvicorn  # Servidor ASGI de alto rendimiento para FastAPI
    # Inicia el servidor uvicorn escuchando en todas las interfaces (0.0.0.0) en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)