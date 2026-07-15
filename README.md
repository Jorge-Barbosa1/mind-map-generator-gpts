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

## Deploying to Render

Use manual service creation in the Render dashboard (works on free tier, no Blueprint required).

### Required environment variables

- Backend: `OPENROUTER_API_KEY` (required)
- Backend: `FRONTEND_ORIGINS` (your deployed frontend URL)
- Frontend: `REACT_APP_API_URL` (your deployed backend URL)

### Step by step (no Blueprint)

1. Push this repository to GitHub.
2. In Render, click **New +** → **Web Service**.
3. Connect the repo and set:
      - Name: `mind-map-generator-backend`
      - Root Directory: `backend`
      - Runtime: `Python`
      - Build Command: `pip install -r requirements.txt`
      - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add backend environment variables:
      - `OPENROUTER_API_KEY` = your key
      - `FRONTEND_ORIGINS` = temporary value (you will update after frontend deploy)
      - `MAX_FILE_SIZE_MB` = `20`
      - `MAX_PROMPT_CHARS` = `10000`
      - `LLM_TIMEOUT_SECONDS` = `60`
5. Deploy backend and copy its public URL.
6. In Render, click **New +** → **Static Site**.
7. Connect the same repo and set:
      - Name: `mind-map-generator-frontend`
      - Root Directory: `frontend`
      - Build Command: `npm install && npm run build`
      - Publish Directory: `build`
8. Add frontend environment variable:
      - `REACT_APP_API_URL` = backend URL from step 5
9. Deploy frontend and copy its public URL.
10. Go back to backend service, set `FRONTEND_ORIGINS` to the frontend URL from step 9, and redeploy backend.

### Service settings summary

- Backend build command: `pip install -r requirements.txt`
- Backend start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Frontend build command: `npm install && npm run build`
- Frontend publish directory: `build`

### Important note

The backend uses audio transcription through `pydub`, so Render must have `ffmpeg` available if you want audio uploads to work.

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
