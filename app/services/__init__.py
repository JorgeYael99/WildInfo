from services.api_ninjas import fetch_animal_data, fetch_sugerencias
from services.unsplash import fetch_unsplash_image
from services.wikipedia import fetch_wikipedia_resumen# --- EN app/services/__init__.py ---

# Cambia las líneas 1, 2 y 3 por estas:
from services.api_ninjas import fetch_animal_data, fetch_sugerencias
from services.unsplash import fetch_unsplash_image
from services.wikipedia import fetch_wikipedia_resumen

__all__ = [
    "fetch_animal_data", 
    "fetch_sugerencias", 
    "fetch_unsplash_image",
    "fetch_wikipedia_resumen"
]