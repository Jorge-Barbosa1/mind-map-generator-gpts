# 🧠 Mind Map Generator GPTs

A full-stack application that generates **mind maps** and **summaries** from **PDFs or audio files**, powered by **LLMs via OpenRouter**.  
This project was built as part of a curricular unit (Project 3).

---

## ✨ Features
- 📂 Upload a **PDF** or **audio file**
- 🤖 Generate a **mind map** using free LLMs from OpenRouter:
  - [xAI Grok 4 Fast (free)](https://openrouter.ai/x-ai/grok-4-fast:free)
  - [DeepSeek Chat v3.1 (free)](https://openrouter.ai/deepseek/deepseek-chat-v3.1:free)
  - [Meta LLaMA 3.3 70B Instruct (free)](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free)
  - [Mistral Small 24B Instruct (free)](https://openrouter.ai/mistralai/mistral-small-3.2-24b-instruct:free)
  - [OpenAI GPT-OSS 20B (free)](https://openrouter.ai/openai/gpt-oss-20b:free)
- 📝 Get a **text summary** alongside the mind map
- 🔍 Built-in **PDF viewer** with search, thumbnails, and zoom
- 🎨 Export the **mind map as an image**

---

## 🛠️ Tech Stack
### Backend
- [FastAPI](https://fastapi.tiangolo.com/) (Python)
- [Uvicorn](https://www.uvicorn.org/) ASGI server
- [OpenRouter API](https://openrouter.ai/) for LLM access
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) + [pydub](https://pypi.org/project/pydub/) for audio

### Frontend
- [React](https://react.dev/)
- [markmap-lib](https://github.com/markmap/markmap) for interactive mind maps
- [@react-pdf-viewer](https://react-pdf-viewer.dev/) for PDF preview
- [Material-UI](https://mui.com/) components

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Jorge-Barbosa1/mind-map-generator-gpts.git
cd mind-map-generator-gpts
