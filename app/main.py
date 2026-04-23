from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from models.database import create_db_pool, init_db
from routes import animales, perfil


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_db_pool()
    await init_db(app.state.db_pool)
    yield
    await app.state.db_pool.close()


app = FastAPI(title="WildInfo Pro", lifespan=lifespan, docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.origen_permitido],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos las rutas
app.include_router(animales.router)
app.include_router(perfil.router)


@app.get("/")
def read_root():
    return {"status": "WildInfo API está en línea", "docs": "/docs"}