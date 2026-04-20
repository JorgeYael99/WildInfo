from .api_ninjas import fetch_animal_data, fetch_sugerencias
from .unsplash import fetch_unsplash_image
from .wikipedia import fetch_wikipedia_resumen

__all__ = [
    "fetch_animal_data", 
    "fetch_sugerencias", 
    "fetch_unsplash_image",
    "fetch_wikipedia_resumen"
]