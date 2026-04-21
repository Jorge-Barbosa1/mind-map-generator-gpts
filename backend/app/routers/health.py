from fastapi import APIRouter

from app.config import APP_VERSION
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness check",
    tags=["health"],
)
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok", version=APP_VERSION)
