import bcrypt
from fastapi import APIRouter, HTTPException, Request, Header
from app.core.config import settings

router = APIRouter(prefix="/perfil", tags=["Perfil"])

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key is not None and x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Firma digital no válida")

def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not user_id or not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"user_id": int(user_id), "username": username}

@router.get("/{user_id}")
async def get_perfil_publico(user_id: int, request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow("SELECT id, nombre_usuario, fecha_registro FROM usuarios WHERE id = $1", user_id)
        if not user_row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        perfil_row = await conn.fetchrow(
            "SELECT puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo FROM perfil_usuario WHERE usuario_id = $1", user_id
        )
        if not perfil_row:
            await conn.execute("""
                INSERT INTO perfil_usuario (usuario_id, puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo)
                VALUES ($1, 0, 0, FALSE, FALSE, 'Observador')
            """, user_id)
            perfil_row = await conn.fetchrow(
                "SELECT puntos, racha_maxima, badge_oro, badge_diversidad, rango_titulo FROM perfil_usuario WHERE usuario_id = $1", user_id
            )
        
        total_especies = await conn.fetchval(
            "SELECT COUNT(*) FROM animales_guardados WHERE usuario_id = $1", user_id
        )
        
        return {
            "username": user_row["nombre_usuario"],
            "fecha_creacion": user_row["fecha_registro"].isoformat() if user_row["fecha_registro"] else None,
            "puntos": perfil_row["puntos"],
            "racha_maxima": perfil_row["racha_maxima"],
            "badge_oro": perfil_row["badge_oro"],
            "badge_diversidad": perfil_row["badge_diversidad"],
            "rango_titulo": perfil_row["rango_titulo"],
            "total_especies": total_especies,
        }

@router.get("/")
async def get_perfil(request: Request):
    user_data = get_current_user(request)
    user_id = user_data["user_id"]
    return await get_perfil_publico(user_id, request)

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
        """, d.get('puntos', 0), d.get('racha_maxima', 0), d.get('badge_oro', False), d.get('badge_diversidad', False), d.get('rango_titulo', 'Observador'), user_id)
        return {"status": "actualizado"}

@router.put("/{user_id}/username")
async def update_username(user_id: int, request: Request, d: dict, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    user_data = get_current_user(request)
    if user_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No puedes modificar otro usuario")
    
    new_username = d.get("username", "").strip()
    if not new_username or len(new_username) < 3:
        raise HTTPException(status_code=400, detail="El nombre debe tener al menos 3 caracteres")
    
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM usuarios WHERE nombre_usuario = $1 AND id != $2", new_username, user_id)
        if existing:
            raise HTTPException(status_code=400, detail="Ese nombre de usuario ya está en uso")
        
        await conn.execute("UPDATE usuarios SET nombre_usuario = $1 WHERE id = $2", new_username, user_id)
        return {"status": "actualizado", "username": new_username}

@router.put("/{user_id}/password")
async def update_password(user_id: int, request: Request, d: dict, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    user_data = get_current_user(request)
    if user_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No puedes modificar otro usuario")
    
    current_password = d.get("current_password", "")
    new_password = d.get("new_password", "")
    if len(new_password) < 4:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 4 caracteres")
    
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT password_hashed FROM usuarios WHERE id = $1", user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), row['password_hashed'].encode('utf-8')):
            raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
        
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await conn.execute("UPDATE usuarios SET password_hashed = $1 WHERE id = $2", hashed, user_id)
        return {"status": "actualizado"}