from fastapi import APIRouter, HTTPException, Request, Header
from app.core.config import settings

router = APIRouter(prefix="/perfil", tags=["Perfil"])

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Firma digital no válida o ausente")

def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not user_id or not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"user_id": int(user_id), "username": username}

@router.get("/")
async def get_perfil(request: Request):
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo FROM perfil_usuario WHERE usuario_id = $1", user_id)
        if not row:
            # Forzamos la inserción con los campos base correctos si el perfil no existe
            await conn.execute("""
                INSERT INTO perfil_usuario (usuario_id, puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo)
                VALUES ($1, 0, 0, FALSE, FALSE, 'Observador de Jardín')
            """, user_id)
            row = await conn.fetchrow("SELECT puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo FROM perfil_usuario WHERE usuario_id = $1", user_id)
        return dict(row)

@router.put("/progreso")
async def update_perfil(request: Request, d: dict, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE perfil_usuario 
            SET puntos = $1, racha_maxima = $2, badge_oro = $3, badge_diversidad = $4, rango_titulo = $5 
            WHERE usuario_id = $6
        """, d.get('puntos', 0), d.get('racha_maxima', 0), d.get('badge_oro', False), d.get('badge_diversidad', False), d.get('rango_titulo', 'Observador de Jardín'), user_id)
        return {"status": "actualizado"}