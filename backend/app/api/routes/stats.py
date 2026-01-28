from fastapi import APIRouter, HTTPException
from ...services import stats_service

router = APIRouter(tags=["Estadísticas"])


@router.get("/historial/")
def obtener_historial():
    try:
        return stats_service.obtener_historial()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estadisticas/reiniciar")
def reiniciar_estadisticas():
    return stats_service.reiniciar_estadisticas()
