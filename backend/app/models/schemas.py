from pydantic import BaseModel, ConfigDict, Field


class ProcessResponse(BaseModel):
    # `model_summary` starts with "model_" — Pydantic v2 reserves that prefix.
    model_config = ConfigDict(protected_namespaces=())

    markdown: str = Field(
        ...,
        description="Hierarchical Markdown ready to be rendered as a mind map.",
        examples=["# Root\n- Item 1\n- Item 2\n  - Sub-item"],
    )
    model_summary: str | None = Field(
        default=None,
        description="Optional short description of the model used. Not populated yet.",
    )


class ErrorResponse(BaseModel):
    """Standard error payload used by FastAPI's default HTTPException."""

    detail: str = Field(..., description="Human-readable error message.")


class HealthResponse(BaseModel):
    """Liveness response returned by GET /healthz."""

    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.1.0"])
