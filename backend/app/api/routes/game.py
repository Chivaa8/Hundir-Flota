import datetime
import uuid

from fastapi import APIRouter, HTTPException

from ...schemas.requests import SolicitudNuevoJuego, SolicitudDisparo, SolicitudAbandono
from ...services.board import generar_barcos_clasicos
from ...services.scoring import calcular_puntuacion
from ...services.storage import (
    create_game,
    get_game,
    update_game,
    delete_game,
    save_game_to_file,
)
from ...services.stats_service import actualizar_estadisticas

router = APIRouter(tags=["Partida"])


@router.get("/")
def leer_raiz():
    return {"mensaje": "Bienvenido a Hundir la Flota", "estado": "funcionando"}


@router.post("/partida/nueva")
def crear_nueva_partida(solicitud: SolicitudNuevoJuego):
    id_juego = str(uuid.uuid4())
    datos_barcos = generar_barcos_clasicos(solicitud.filas, solicitud.columnas)

    datos_juego = {
        "id_juego": id_juego,
        "filas": solicitud.filas,
        "columnas": solicitud.columnas,
        "jugador": solicitud.jugador,
        "modo": (solicitud.dificultad or "normal").lower(),
        "tablero": datos_barcos["tablero"],
        "barcos": datos_barcos["barcos"],
        "casillas_ocupadas": datos_barcos["casillas_ocupadas"],
        "porcentaje_ocupacion": datos_barcos["porcentaje_ocupacion"],
        "disparos": [],
        "juego_terminado": False,
        "barcos_totales": len(datos_barcos["barcos"]),
        "barcos_hundidos": 0,
        "puntuacion": 0,
        "fecha_inicio": datetime.datetime.now().isoformat(),
        "estado_partida": "en_curso",
    }

    create_game(id_juego, datos_juego)

    return {
        "id_juego": id_juego,
        "filas": solicitud.filas,
        "columnas": solicitud.columnas,
        "barcos_totales": len(datos_barcos["barcos"]),
        "porcentaje_ocupacion": datos_barcos["porcentaje_ocupacion"],
        "casillas_ocupadas": datos_barcos["casillas_ocupadas"],
        "jugador": solicitud.jugador,
        "tablero_creado": True,
    }


def _tablero_visible(juego: dict):
    filas = juego["filas"]
    columnas = juego["columnas"]
    visible = [[{"fila": f, "columna": c, "disparado": False, "resultado": "desconocido"} for c in range(columnas)] for f in range(filas)]

    for d in juego.get("disparos", []):
        f = d["fila"]
        c = d["columna"]
        visible[f][c]["disparado"] = True
        visible[f][c]["resultado"] = d["resultado"]

    return visible


@router.post("/partida/{id_juego}/disparar")
def realizar_disparo(id_juego: str, disparo: SolicitudDisparo):
    juego = get_game(id_juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    if juego.get("juego_terminado", False):
        raise HTTPException(status_code=400, detail="La partida ya ha terminado")

    if not (0 <= disparo.fila < juego["filas"]):
        raise HTTPException(status_code=400, detail="Fila fuera de rango")

    if not (0 <= disparo.columna < juego["columnas"]):
        raise HTTPException(status_code=400, detail="Columna fuera de rango")

    disparos = juego.get("disparos", [])
    if any(d["fila"] == disparo.fila and d["columna"] == disparo.columna for d in disparos):
        raise HTTPException(status_code=400, detail="Ya has disparado a esta posición")

    tablero = juego["tablero"]
    id_barco_en_posicion = tablero[disparo.fila][disparo.columna]

    if id_barco_en_posicion > 0:
        valor_posicion = "barco"
        barco_tocado = next((b for b in juego["barcos"] if b["id"] == id_barco_en_posicion), None)

        if barco_tocado:
            for i, pos in enumerate(barco_tocado["posiciones"]):
                if pos["fila"] == disparo.fila and pos["columna"] == disparo.columna:
                    barco_tocado["tocado"][i] = True
                    break

            if all(barco_tocado["tocado"]) and not barco_tocado["hundido"]:
                barco_tocado["hundido"] = True
                resultado = "hundido"
                juego["barcos_hundidos"] += 1
            elif barco_tocado["hundido"]:
         # Ya estaba hundido (por si se dispara a una parte del barco)
                resultado = "hundido"
            else:
                resultado = "tocado"

        else:
            resultado = "tocado"
    else:
        valor_posicion = "agua"
        resultado = "agua"

    disparos.append(
        {
            "fila": disparo.fila,
            "columna": disparo.columna,
            "resultado": resultado,
            "valor_posicion": valor_posicion,
        }
    )
    juego["disparos"] = disparos

    # puntuación
    juego["puntuacion"] = calcular_puntuacion(juego)

    barcos_hundidos = juego["barcos_hundidos"]
    total_disparos = len(disparos)

    # reglas del profe (las mantenemos)
    estado_partida = "en_curso"
    total_barcos = len(juego["barcos"])
    if barcos_hundidos >= total_barcos:
        estado_partida = "ganada"
        juego["juego_terminado"] = True
    elif total_disparos >= (juego["filas"] * juego["columnas"]) // 2:
        estado_partida = "perdida"
        juego["juego_terminado"] = True

    juego["estado_partida"] = estado_partida

    update_game(id_juego, juego)

    return {
        "valor_posicion": valor_posicion,
        "resultado": resultado,
        "barcos_hundidos": barcos_hundidos,
        "total_disparos": total_disparos,
        "estado_partida": estado_partida,
        "puntuacion_parcial": juego["puntuacion"],
        "modo": juego.get("modo", "normal"),
        # ✅ NO devolvemos tablero real (anti-trampas)
        "tablero": _tablero_visible(juego),
    }


@router.get("/partida/{id_juego}/tablero")
def obtener_tablero(id_juego: str):
    juego = get_game(id_juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    return {
        "id_juego": id_juego,
        "tablero": _tablero_visible(juego),
        "filas": juego["filas"],
        "columnas": juego["columnas"],
    }


@router.post("/partida/{id_juego}/reiniciar")
def reiniciar_partida(id_juego: str):
    juego = get_game(id_juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    datos_barcos = generar_barcos_clasicos(juego["filas"], juego["columnas"])
    juego["tablero"] = datos_barcos["tablero"]
    juego["barcos"] = datos_barcos["barcos"]
    juego["casillas_ocupadas"] = datos_barcos["casillas_ocupadas"]
    juego["porcentaje_ocupacion"] = datos_barcos["porcentaje_ocupacion"]

    juego["disparos"] = []
    juego["barcos_hundidos"] = 0
    juego["juego_terminado"] = False
    juego["puntuacion"] = 0
    juego["estado_partida"] = "en_curso"
    juego["fecha_inicio"] = datetime.datetime.now().isoformat()

    update_game(id_juego, juego)

    return {
        "mensaje": "Partida reiniciada correctamente",
        "id_juego": id_juego,
        "filas": juego["filas"],
        "columnas": juego["columnas"],
        "barcos_totales": len(juego["barcos"]),
        "porcentaje_ocupacion": juego["porcentaje_ocupacion"],
        "jugador": juego["jugador"],
    }


@router.post("/partida/{id_juego}/finalizar")
def finalizar_partida(id_juego: str):
    juego = get_game(id_juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    if not juego.get("juego_terminado", False):
        juego["juego_terminado"] = True
        juego["fecha_fin"] = datetime.datetime.now().isoformat()
        juego["estado_partida"] = juego.get("estado_partida", "finalizada")

    save_game_to_file(id_juego, juego)
    actualizar_estadisticas(juego)
    delete_game(id_juego)

    return {"message": "Partida finalizada y estadísticas actualizadas"}


@router.post("/partida/{id_juego}/abandonar")
def abandonar_partida(id_juego: str, solicitud: SolicitudAbandono):
    juego = get_game(id_juego)
    if not juego:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    if juego.get("juego_terminado", False):
        raise HTTPException(status_code=400, detail="La partida ya ha terminado")

    # regla: abandonar = 0
    juego["juego_terminado"] = True
    juego["estado_partida"] = "abandonada"
    juego["puntuacion"] = 0
    juego["razon_abandono"] = solicitud.razon
    juego["timestamp_abandono"] = datetime.datetime.now().isoformat()
    juego["fecha_fin"] = datetime.datetime.now().isoformat()

    actualizar_estadisticas(juego)
    save_game_to_file(id_juego, juego)

    # (opcional) mantener en memoria o borrar
    delete_game(id_juego)

    return {
        "message": "Partida abandonada exitosamente",
        "id_juego": id_juego,
        "puntuacion_final": 0,
        "estado": "abandonada",
        "razon": solicitud.razon,
    }
