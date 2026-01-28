# 🚢 Hundir la Flota

Implementación del juego clásico **Hundir la Flota** con arquitectura cliente-servidor.

El proyecto está desarrollado con un **backend en FastAPI (Python)** y un **frontend web en HTML, CSS y JavaScript**, permitiendo jugar partidas completas desde el navegador.

---

## 🧩 Características

- 🎯 Juego completo de Hundir la Flota
- 📐 Tablero configurable (entre 7x7 y 20x20)
- ⚙️ Niveles de dificultad: fácil, normal y difícil
- 🚢 Colocación automática de barcos con separación clásica (sin barcos adyacentes)
- ⏱️ Temporizador de partida
- 🧮 Sistema de puntuación basado en:
  - número de disparos
  - aciertos
  - barcos hundidos
  - tiempo de partida
- 📊 Estadísticas globales y ranking Top 5
- 🔄 Reinicio y abandono de partida
- 🌐 API REST documentada con Swagger

---

## 🛠️ Tecnologías utilizadas

### Backend
- Python 3
- FastAPI
- Uvicorn
- Pydantic

### Frontend
- HTML5
- CSS3
- JavaScript (vanilla)
- Bootstrap 5

---

## 📁 Estructura del proyecto

Hundir-Flota/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ ├── core/
│ │ ├── schemas/
│ │ ├── services/
│ │ └── main.py
│ ├── data/
│ └── requirements.txt
├── frontend/
│ ├── index.html
│ ├── styles.css
│ └── main.js
└── README.md


---

## ▶️ Cómo ejecutar el proyecto

### 1️⃣ Backend

Desde la carpeta `backend`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

```

📍 El backend estará disponible en:
[[http://localhost:5173](http://127.0.0.1:8000)](http://127.0.0.1:8000)

📍 La documentación Swagger se puede consultar en:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2️⃣ Frontend

Abrir el archivo:

```frontend/index.html
```

Directamente en el navegador (no requiere servidor adicional).


### 👤 Autor

Desarrollado por **Oriol Chiva Hidalgo**
### 📧 Contacto: oriolchiva8@gmail.com / oriol.chiva.hidalgo@gmail.com

© 2026 – Proyecto educativo desarrollado bajo licencia MIT.

