from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Keys Externas
    api_ninjas_key: str = Field(alias="API_NINJS_KEY")
    unsplash_access_key: str = Field(alias="UNSPLASH_ACCESS_KEY")
    
    # Base de Datos
    database_url: str = Field(alias="DATABASE_URL")
    
    # Servidor
    port: int = Field(default=8000, alias="PORT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    
    # Seguridad
    origen_permitido: str = Field(alias="ORIGEN_PERMITIDO")
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # Indica que busque el archivo en la raíz del proyecto
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instancia para usar en el resto de la app
settings = Settings()