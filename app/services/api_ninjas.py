import httpx
from app.core.config import settings

async def traducir_a_ingles(termino: str) -> str:
    """
    Traduce un término de búsqueda de Español a Inglés usando la API libre MyMemory.
    Si la traducción falla o el término ya está en inglés, devuelve el string original.
    """
    url = f"https://api.mymemory.translated.net/get?q={httpx.URL(termino).path}&langpair=es|en"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                translated_text = data.get("responseData", {}).get("translatedText", "")
                if translated_text:
                    return translated_text.strip()
    except Exception:
        # Si la API de traducción falla por timeout, usamos el término original como respaldo
        pass
    return termino

async def fetch_animal_data(nombre: str) -> dict:
    """
    Obtiene los datos científicos de API Ninjas traduciendo primero el término si viene en español.
    """
    # 1. TRADUCCIÓN AUTOMÁTICA EN SEGUNDO PLANO
    nombre_en_ingles = await traducir_a_ingles(nombre)
    
    # 2. CONSULTA A API NINJAS CON EL NOMBRE EN INGLÉS
    url = f"https://api.api-ninjas.com/v1/animals?name={httpx.URL(nombre_en_ingles).path}"
    headers = {"X-Api-Key": settings.api_ninjas_key} # Asegúrate de que coincida con tu setting de llave
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                resultados = response.json()
                # API Ninjas devuelve una lista; si tiene elementos, regresamos el primero
                if resultados and len(resultados) > 0:
                    return resultados[0]
    except Exception:
        pass
    return None

async def fetch_sugerencias(q: str) -> list:
    """
    Devuelve sugerencias básicas. Si prefieres traducir el query de autocompletado también,
    puedes aplicar la traducción aquí.
    """
    q_en = await traducir_a_ingles(q)
    url = f"https://api.api-ninjas.com/v1/animals?name={httpx.URL(q_en).path}"
    headers = {"X-Api-Key": settings.api_ninjas_key}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=4.0)
            if response.status_code == 200:
                resultados = response.json()
                # Retornamos los nombres mapeados de las coincidencias
                return [animal["name"] for animal in resultados][:5]
    except Exception:
        pass
    return []