import os
import tempfile

import fitz  # PyMuPDF
import speech_recognition as sr
from pydub import AudioSegment


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        text_parts: list[str] = []
        with fitz.open(tmp_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "".join(text_parts).strip()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def transcribe_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    tmp_path = None
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        wav_path = tmp_path + "_converted.wav"
        AudioSegment.from_file(tmp_path).export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language="en-US").strip()
    finally:
        for path in (tmp_path, wav_path):
            if path and os.path.exists(path):
                os.remove(path)
