import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.config import settings
from app.models.schemas import ErrorResponse, ProcessResponse
from app.services.file_utils import extract_text_from_pdf, transcribe_audio
from app.services.llm_client import generate_mindmap

router = APIRouter()

ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
}


async def _read_and_validate(
    upload: UploadFile, allowed_types: set[str], kind: str
) -> bytes:
    if upload.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported {kind} type: {upload.content_type}",
        )
    data = await upload.read()
    if len(data) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{kind} exceeds {settings.max_file_size_mb} MB limit",
        )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Empty {kind} upload",
        )
    return data


@router.post(
    "/process-file",
    response_model=ProcessResponse,
    summary="Generate a Markdown mind map from a PDF, audio file, or prompt",
    responses={
        400: {"model": ErrorResponse, "description": "No input / empty prompt / prompt too long"},
        413: {"model": ErrorResponse, "description": "File exceeds size limit"},
        415: {"model": ErrorResponse, "description": "Unsupported file MIME type"},
        422: {"model": ErrorResponse, "description": "Could not extract any text"},
        500: {"model": ErrorResponse, "description": "Upstream LLM or processing error"},
    },
)
async def process_file(
    model: str = Form("mistralai/mistral-7b-instruct:free"),
    pdf_file: UploadFile | None = File(None),
    audio_file: UploadFile | None = File(None),
    prompt: str | None = Form(None),
) -> ProcessResponse:
    """Accepts exactly one of `pdf_file`, `audio_file`, or `prompt`.

    Extracts or transcribes the text, forwards it to the chosen OpenRouter model,
    and returns the generated Markdown mind map.
    """
    if pdf_file:
        pdf_bytes = await _read_and_validate(pdf_file, ALLOWED_PDF_TYPES, "PDF")
        text = extract_text_from_pdf(pdf_bytes)
    elif audio_file:
        audio_bytes = await _read_and_validate(
            audio_file, ALLOWED_AUDIO_TYPES, "audio"
        )
        suffix = os.path.splitext(audio_file.filename or "")[1] or ".wav"
        text = transcribe_audio(audio_bytes, suffix=suffix)
    elif prompt:
        if len(prompt) > settings.max_prompt_chars:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prompt exceeds {settings.max_prompt_chars} characters",
            )
        text = prompt
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input provided",
        )

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract any text from the input",
        )

    markdown = generate_mindmap(text, model=model)
    return ProcessResponse(markdown=markdown)
