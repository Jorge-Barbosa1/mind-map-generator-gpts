import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.file_utils import extract_text_from_pdf, transcribe_audio
from app.services.llm_client import generate_mindmap, generate_summary

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process-file")
async def process_file(
    model: str = Form("nvidia/nemotron-3-nano-30b-a3b:free"),
    pdf_file: UploadFile = File(None),
    audio_file: UploadFile = File(None),
    prompt: str = Form(None),
):
    try:
        text = ""
        if pdf_file:
            text = extract_text_from_pdf(pdf_file)
        elif audio_file:
            text = transcribe_audio(audio_file)
        elif prompt:
            text = prompt
        else:
            raise HTTPException(status_code=400, detail="No input provided")

        markdown = generate_mindmap(text, model=model)
        summary = generate_summary(text, model=model)
        return {"markdown": markdown, "model_summary": summary}

    except Exception as e:
        # Log full traceback server-side for easier debugging
        logger.exception("process_file failed")
        raise HTTPException(status_code=500, detail=str(e))
