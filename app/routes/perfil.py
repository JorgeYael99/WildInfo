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
        row = await conn.fetchrow("SELECT * FROM perfil_usuario WHERE usuario_id = $1", user_id)
        if not row:
            await conn.execute("INSERT INTO perfil_usuario (usuario_id) VALUES ($1)", user_id)
            row = await conn.fetchrow("SELECT * FROM perfil_usuario WHERE usuario_id = $1", user_id)
        return dict(row)

@router.put("/progreso")
async def update_perfil(request: Request, d: dict, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    pool = request.app.state.db_pool
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE perfil_usuario SET puntos=$1, racha_maxima=$2, 
            badge_oro=$3, badge_diversidad=$4, rango_titulo=$5 WHERE usuario_id=$6
        """, d['puntos'], d['racha_maxima'], d['badge_oro'], d['badge_diversidad'], d['rango_titulo'], user_id)
        return {"status": "actualizado"}