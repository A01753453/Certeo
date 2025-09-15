from fastapi import FastAPI
from .api.ingesta import router as ingesta_router

app = FastAPI(title="Copiloto de Cumplimiento - MVP Día 1")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingesta_router)
