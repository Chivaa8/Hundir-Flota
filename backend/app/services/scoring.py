import datetime


MODO_FACIL = {
    "puntuacion_base": 1200,
    "disparar": -5,
    "acertar_barco": 25,
    "hundir_barco": 60,
    "penalizacion_tiempo": -0.5,
}

MODO_NORMAL = {
    "puntuacion_base": 1000,
    "disparar": -10,
    "acertar_barco": 20,
    "hundir_barco": 50,
    "penalizacion_tiempo": -1,
}

MODO_DIFICIL = {
    "puntuacion_base": 800,
    "disparar": -15,
    "acertar_barco": 15,
    "hundir_barco": 40,
    "penalizacion_tiempo": -2,
}


def get_config(modo: str):
    modo = (modo or "normal").lower()
    if modo == "facil":
        return MODO_FACIL
    if modo == "dificil":
        return MODO_DIFICIL
    return MODO_NORMAL


def calcular_puntuacion(juego: dict) -> int:
    config = get_config(juego.get("modo", "normal"))

    disparos = juego.get("disparos", [])
    barcos_hundidos = juego.get("barcos_hundidos", 0)
    total_disparos = len(disparos)
    total_aciertos = sum(1 for d in disparos if d["resultado"] in ["tocado", "hundido"])

    tiempo_transcurrido = 0.0
    if juego.get("fecha_inicio"):
        inicio = datetime.datetime.fromisoformat(juego["fecha_inicio"])
        ahora = datetime.datetime.now()
        tiempo_transcurrido = (ahora - inicio).total_seconds()

    puntuacion = (
        config["puntuacion_base"]
        + (config["disparar"] * total_disparos)
        + (config["acertar_barco"] * total_aciertos)
        + (config["hundir_barco"] * barcos_hundidos)
        + (config["penalizacion_tiempo"] * (tiempo_transcurrido / 60))
    )

    return max(0, int(puntuacion))
