from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_VERSION, settings
from app.routers import health, process

app = FastAPI(title="Mind Map Generator API", version=APP_VERSION)
app.include_router(process.router)
app.include_router(health.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
