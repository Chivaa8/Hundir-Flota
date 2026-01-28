import json
import os
import threading
from pathlib import Path


_lock = threading.Lock()
_games_in_memory: dict[str, dict] = {}


def get_backend_dir() -> Path:
    # backend/app/services/storage.py -> parents[2] = backend
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return get_backend_dir() / "data"


def games_dir() -> Path:
    return data_dir() / "games"


def stats_path() -> Path:
    return data_dir() / "stats.json"


def ensure_data_dirs():
    os.makedirs(games_dir(), exist_ok=True)
    os.makedirs(data_dir(), exist_ok=True)


def create_game(game_id: str, game_data: dict):
    with _lock:
        _games_in_memory[game_id] = game_data


def get_game(game_id: str) -> dict | None:
    with _lock:
        return _games_in_memory.get(game_id)


def update_game(game_id: str, game_data: dict):
    with _lock:
        _games_in_memory[game_id] = game_data


def delete_game(game_id: str):
    with _lock:
        if game_id in _games_in_memory:
            del _games_in_memory[game_id]


def save_game_to_file(game_id: str, game_data: dict):
    ensure_data_dirs()
    ruta = games_dir() / f"{game_id}.json"
    tmp = Path(str(ruta) + ".tmp")

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(game_data, f, indent=2, ensure_ascii=False)

    os.replace(tmp, ruta)
