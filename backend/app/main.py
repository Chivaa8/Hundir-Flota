from fastapi import FastAPI

from .core.cors import setup_cors
from .api.routes.game import router as game_router
from .api.routes.stats import router as stats_router

app = FastAPI(
    title="Hundir la Flota API",
    description="API para el juego de hundir la flota",
    version="1.0.0",
    contact={
        "name": "Oriol Chiva",
        "url": "https://github.com/...",
        "email": "oriolchiva8@gmail.com",
    },
)

setup_cors(app)

app.include_router(game_router)
app.include_router(stats_router)
