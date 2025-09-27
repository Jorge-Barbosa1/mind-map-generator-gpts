from fastapi import FastAPI
from app.routers import process
from fastapi.middleware.cors import CORSMiddleware

app= FastAPI()
app.include_router(process.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)