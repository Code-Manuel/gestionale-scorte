import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import alerts, home, movements, products

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Powered by Manuel Cabras",
    description="Sistema per la gestione di magazzino, movimenti e riordino automatico.",
    version="0.1.0",
)

app.include_router(home.router)
app.include_router(products.router)
app.include_router(movements.router)
app.include_router(alerts.router)

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
