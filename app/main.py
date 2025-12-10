from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import create_tables
from app.routes import products, customers, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for an online store",
    lifespan=lifespan
)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to the online store API",
        "version": settings.app_version,
        "docs": "/docs",
        "database": "PostgreSQL"
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "database": "connected"}