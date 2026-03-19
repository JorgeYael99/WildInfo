from fastapi import FastAPI, HTTPException
import httpx

# Inicializamos la aplicación FastAPI
app = FastAPI(title="WildInfo API", description="API para obtener datos e imágenes de animales")

# Configuración de Unsplash
# Pega aquí tu Clave de Acceso (Access Key) que empieza con 51FeTP...
ACCESS_KEY = "51FeTP2HTk4BZt5zse9gdOkDovfyrY2BG9qxBbiBRR8" 
BASE_URL = "https://api.unsplash.com"

@app.get("/")
def inicio():
    return {"mensaje": "¡Bienvenido al backend de WildInfo!"}

@app.get("/api/animal-aleatorio")
async def obtener_imagen_animal():
    """
    Se conecta a Unsplash y devuelve una imagen aleatoria de un animal.
    """
    endpoint = f"{BASE_URL}/photos/random"
    
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {ACCESS_KEY}"
    }
    
    # Filtramos la búsqueda aleatoria para que solo traiga animales
    params = {
        "query": "animal, wildlife"
    }

    # Usamos httpx.AsyncClient para hacer la petición de forma asíncrona
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers, params=params)
        
        # Si Unsplash responde con éxito (código 200)
        if response.status_code == 200:
            datos = response.json()
            
            # Filtramos solo la información que nos interesa enviar a nuestro frontend
            return {
                "id": datos["id"],
                "descripcion": datos["alt_description"] or "Sin descripción",
                "url_imagen": datos["urls"]["regular"],
                "fotografo": datos["user"]["name"],
                "enlace_fotografo": datos["user"]["links"]["html"]
            }
        else:
            # Si hay un error (ej. clave inválida), le avisamos a FastAPI para que muestre el error
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Error al obtener imagen de Unsplash: {response.text}"
            )