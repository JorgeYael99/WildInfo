from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.database import create_db_pool, init_db
from app.routes import animales, perfil, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_db_pool()
    await init_db(app.state.db_pool)
    yield
    await app.state.db_pool.close()

app = FastAPI(
    title="WildInfo Pro",
    lifespan=lifespan,
    debug=(settings.environment == "development")
)

origins = [o.strip() for o in settings.origen_permitido.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.environment == "development":
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

app.include_router(auth.router)
app.include_router(animales.router)
app.include_router(perfil.router)

@app.get("/")
def read_root():
    return {"status": "WildInfo API Online"}