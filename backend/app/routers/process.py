from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.file_utils import extract_text_from_pdf, transcribe_audio
from app.services.llm_client import generate_mindmap

router = APIRouter()

@router.post("/process-file")
async def process_file(
    model: str = Form("mistralai/mistral-7b-instruct:free"),
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
        return {"markdown": markdown}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
