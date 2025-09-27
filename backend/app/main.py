from fastapi import FastAPI
from app.routers import process

app= FastAPI()
app.include_router(process.router)

