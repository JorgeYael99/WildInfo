from fastapi import FastAPI, HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="WildInfo API", description="API para obtener datos e imágenes de animales")

ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
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