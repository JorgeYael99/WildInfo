from fastapi import APIRouter, HTTPException, Request, Response
import bcrypt
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class UserAuth(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    user_id: int
    username: str
    token: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_from_token(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    if not user_id or not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    return {"user_id": int(user_id), "username": username, "token": token}

@router.post("/registro")
async def registro(request: Request, user: UserAuth):
    pool = request.app.state.db_pool
    hashed_password = hash_password(user.password)
    
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM usuarios WHERE nombre_usuario = $1", user.username)
        if existing:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
        user_id = await conn.fetchval("""
            INSERT INTO usuarios (nombre_usuario, password_hashed) 
            VALUES ($1, $2) RETURNING id
        """, user.username, hashed_password)
        
        await conn.execute("INSERT INTO perfil_usuario (usuario_id) VALUES ($1)", user_id)
        
        token = f"token_{user_id}_{user.username}"
        
        return {"user_id": user_id, "username": user.username, "token": token}

@router.post("/login")
async def login(request: Request, user: UserAuth):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, nombre_usuario, password_hashed FROM usuarios WHERE nombre_usuario = $1", user.username)
        
        if not row or not verify_password(user.password, row['password_hashed']):
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        
        token = f"token_{row['id']}_{row['nombre_usuario']}"
            
        return {"user_id": row['id'], "username": row['nombre_usuario'], "token": token}

@router.post("/logout")
async def logout():
    return {"status": "success"}