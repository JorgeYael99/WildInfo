import asyncpg
from core.config import settings

async def create_db_pool():
    return await asyncpg.create_pool(settings.database_url)

async def init_db(pool):
    async with pool.acquire() as conn:
        # 1. Tabla de Usuarios
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
                password_hashed TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Tabla de Perfil (vinculada al usuario)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS perfil_usuario (
                usuario_id INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
                puntos INT DEFAULT 0,
                racha_maxima INT DEFAULT 0,
                badge_oro BOOLEAN DEFAULT FALSE,
                badge_diversidad BOOLEAN DEFAULT FALSE,
                rango_titulo VARCHAR(100) DEFAULT 'Observador de Jardín'
            )
        """)
        
        # 3. Tabla de Animales (vinculada al usuario)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS animales_guardados (
                id SERIAL PRIMARY KEY,
                usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
                nombre VARCHAR(100) NOT NULL,
                reino VARCHAR(50),
                clase VARCHAR(50),
                familia VARCHAR(50),
                url_imagen TEXT,
                en_peligro BOOLEAN DEFAULT FALSE,
                UNIQUE(usuario_id, nombre)
            )
        """)
        print("DB: Sistema multiusuario inicializado correctamente.")