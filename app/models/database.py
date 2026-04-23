import asyncpg
from core.config import settings

async def create_db_pool():
    return await asyncpg.create_pool(settings.database_url)

async def init_db(pool):
    async with pool.acquire() as conn:
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
        print("DB: Tablas verificadas/creadas con éxito.")