from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.config import settings
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
