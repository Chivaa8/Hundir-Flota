from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    origins = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
