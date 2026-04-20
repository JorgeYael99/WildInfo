from fastapi import APIRouter, Request, HTTPException, Header, Depends
from app.core.config import settings

router = APIRouter(prefix="/perfil", tags=["Perfil"])

def verificar_firma(x_api_key: str = Header(None)):
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Firma digital no válida o ausente")

@router.get("/")
async def get_perfil(request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM perfil_usuario WHERE id = 1")
        return dict(row)

@router.put("/progreso", dependencies=[Depends(verificar_firma)])
async def update_perfil(request: Request, d: dict):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE perfil_usuario SET puntos=$1, racha_maxima=$2, 
            badge_oro=$3, badge_diversidad=$4, rango_titulo=$5 WHERE id=1
        """, d['puntos'], d['racha_maxima'], d['badge_oro'], d['badge_diversidad'], d['rango_titulo'])
        return {"status": "actualizado"}