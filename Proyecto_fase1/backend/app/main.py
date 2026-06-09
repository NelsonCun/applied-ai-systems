from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import diagnostico_routes, historial_routes


app = FastAPI(
    title="Doctor Byte API",
    description="Backend para sistema experto de diagnóstico de fallas en computadoras",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(diagnostico_routes.router)
app.include_router(historial_routes.router)


@app.get("/")
def home():
    return {
        "mensaje": "Doctor Byte API funcionando correctamente"
    }
