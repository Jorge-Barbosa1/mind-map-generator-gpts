# Mind Map Generator

Generates interactive mind maps from **PDFs**, **audio**, or **text prompts**, using open-source LLMs served via [OpenRouter](https://openrouter.ai/).

The text is extracted or transcribed on the backend, sent to the selected model, and returned as **hierarchical Markdown**, which is then rendered on the frontend as a navigable mind map via [Markmap](https://markmap.js.org/).

---

## Stack

| Layer | Technology |
| --- | --- |
| Backend | Python · FastAPI · Uvicorn · OpenAI SDK (via OpenRouter) · PyMuPDF · SpeechRecognition + pydub |
| Frontend | React 18 (CRA) · Material-UI v6 · Markmap · @react-pdf-viewer · axios · html2canvas |
| LLM provider | OpenRouter (free-tier models: Grok, DeepSeek, LLaMA, Mistral, GPT-OSS) |

---

## Architecture

```
┌────────────────┐     multipart/form-data     ┌────────────────────┐
│                │ ─────────────────────────▶ │                    │
│  Frontend      │  POST /process-file         │  Backend (FastAPI) │
│  (React, CRA)  │  { pdf | audio | prompt,    │                    │
│                │    model }                  │  ┌──────────────┐  │
│                │ ◀───── { markdown } ─────── │  │ file_utils   │  │
└────────────────┘                             │  │  · PDF → txt │  │
         │                                     │  │  · audio→ txt│  │
         │ renders                             │  └──────┬───────┘  │
         ▼                                     │         │          │
   Markmap SVG                                 │  ┌──────▼───────┐  │
   (+ PNG download)                            │  │ llm_client   │──┼──▶ OpenRouter API
                                               │  └──────────────┘  │
                                               └────────────────────┘
```

---

## Local setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- [FFmpeg](https://ffmpeg.org/) on your `PATH` (required by `pydub` for non-WAV audio)
- OpenRouter API key — [get one at openrouter.ai/keys](https://openrouter.ai/keys)

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENROUTER_API_KEY

uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000`. Auto-generated docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm start
```

App: `http://localhost:3000`.

---

## Environment variables (backend)

See [`backend/.env.example`](backend/.env.example). Summary:

| Variable | Default | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | — (required) | OpenRouter API key |
| `FRONTEND_ORIGINS` | `http://localhost:3000` | Comma-separated list of CORS-allowed origins |
| `MAX_FILE_SIZE_MB` | `20` | Upload size cap (PDF/audio) |
| `MAX_PROMPT_CHARS` | `10000` | Prompt length cap |
| `LLM_TIMEOUT_SECONDS` | `60` | Timeout for OpenRouter calls |

---

## Common scripts

| Directory | Command | Effect |
| --- | --- | --- |
| `backend/` | `uvicorn app.main:app --reload` | Dev server with auto-reload |
| `frontend/` | `npm start` | Dev server (port 3000) |
| `frontend/` | `npm run build` | Production build in `frontend/build/` |
| `frontend/` | `npm test` | CRA test runner |

---

## Further docs

- [`backend/README.md`](backend/README.md) — API contract, supported models, how to add a provider.
- [`frontend/README.md`](frontend/README.md) — UI structure, API configuration, build.
- [`TODO.md`](TODO.md) — phased roadmap and task status.

---

## Security

- **Never** commit `backend/.env` or the OpenRouter key. `.gitignore` covers `.env*` except `.env.example`.
- `FRONTEND_ORIGINS` is a whitelist — set real production domains, not `*`.
- Uploads are validated by MIME type and size in the `/process-file` endpoint.

---

## License

TBD.
