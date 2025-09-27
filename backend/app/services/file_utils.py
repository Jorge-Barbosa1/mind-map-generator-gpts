import fitz  # PyMuPDF
import tempfile
import os
from pydub import AudioSegment
import speech_recognition as sr

def extract_text_from_pdf(pdf_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.file.read())
        tmp_path = tmp.name

    text = ""
    doc = fitz.open(tmp_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    os.remove(tmp_path)

    return text.strip()

def transcribe_audio(audio_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.file.read())
        tmp_path = tmp.name

    audio = AudioSegment.from_file(tmp_path)
    wav_path = tmp_path.replace(".wav", "_converted.wav")
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-US")

    os.remove(tmp_path)
    os.remove(wav_path)

    return text.strip()
