from typing import Optional, Literal
from pydantic import BaseModel, Field


Difficulty = Literal["facil", "normal", "dificil"]


class SolicitudNuevoJuego(BaseModel):
    filas: int = Field(..., ge=7, le=20)
    columnas: int = Field(..., ge=7, le=20)
    jugador: Optional[str] = "Anónimo"
    dificultad: Optional[Difficulty] = "normal"


class SolicitudDisparo(BaseModel):
    fila: int
    columna: int


class SolicitudAbandono(BaseModel):
    razon: Optional[str] = "Partida abandonada por el usuario"
