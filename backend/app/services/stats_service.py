import json
import os
import datetime
from .storage import ensure_data_dirs, stats_path


def obtener_historial():
    ensure_data_dirs()
    ruta = stats_path()

    if not os.path.exists(ruta):
        stats = {
            "total_partidas": 0,
            "mejor_puntuacion": 0,
            "mejor_jugador": "anónimo",
            "fecha_mejor": datetime.datetime.now().isoformat(),
            "ranking_top5": [],
        }
        _write_stats(stats)
        return stats

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def reiniciar_estadisticas():
    ensure_data_dirs()
    stats = {
        "total_partidas": 0,
        "mejor_puntuacion": 0,
        "mejor_jugador": "anónimo",
        "fecha_mejor": None,
        "ranking_top5": [],
    }
    _write_stats(stats)
    return {"mensaje": "Estadísticas reiniciadas correctamente."}


def actualizar_estadisticas(juego: dict):
    ensure_data_dirs()
    ruta = stats_path()

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        stats = {
            "total_partidas": 0,
            "mejor_puntuacion": 0,
            "mejor_jugador": "anónimo",
            "fecha_mejor": None,
            "ranking_top5": [],
        }

    stats["total_partidas"] += 1

    jugador = juego.get("jugador", "anónimo")
    puntuacion = juego.get("puntuacion", 0)
    filas = juego.get("filas", 0)
    columnas = juego.get("columnas", 0)
    fecha_fin = juego.get("fecha_fin", datetime.datetime.now().isoformat())

    duracion_ms = 0
    if juego.get("fecha_inicio") and juego.get("fecha_fin"):
        try:
            inicio = datetime.datetime.fromisoformat(juego["fecha_inicio"].replace("Z", ""))
            fin = datetime.datetime.fromisoformat(juego["fecha_fin"].replace("Z", ""))
            duracion_ms = int((fin - inicio).total_seconds() * 1000)
        except Exception:
            pass

    if puntuacion > stats.get("mejor_puntuacion", 0):
        stats["mejor_puntuacion"] = puntuacion
        stats["mejor_jugador"] = jugador
        stats["fecha_mejor"] = fecha_fin

    entry = {
        "jugador": jugador,
        "puntuacion": puntuacion,
        "filas": filas,
        "columnas": columnas,
        "fecha": fecha_fin,
        "duracion_ms": duracion_ms,
    }

    stats["ranking_top5"].append(entry)
    stats["ranking_top5"].sort(key=lambda x: x["puntuacion"], reverse=True)
    stats["ranking_top5"] = stats["ranking_top5"][:5]

    _write_stats(stats)


def _write_stats(stats: dict):
    ruta = stats_path()
    tmp = str(ruta) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ruta)
