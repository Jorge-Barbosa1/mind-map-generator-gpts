# Backend — Mind Map Generator API

FastAPI service that accepts a PDF, audio file, or text prompt, turns it into plain text, and asks an OpenRouter-hosted LLM to produce a Markdown mind map.

---

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── config.py            # Settings (pydantic-settings)
│   ├── routers/
│   │   └── process.py       # POST /process-file
│   └── services/
│       ├── file_utils.py    # PDF → text, audio → text
│       ├── llm_client.py    # OpenRouter client (OpenAI SDK)
│       └── mindmap.py       # (reserved for post-processing)
├── requirements.txt
└── .env.example
```

---

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # set OPENROUTER_API_KEY
uvicorn app.main:app --reload --port 8000
```

Interactive docs: `http://localhost:8000/docs` (Swagger UI) · `http://localhost:8000/redoc`.

---

## API

### `GET /healthz`

Liveness check. Returns `{ "status": "ok", "version": "<APP_VERSION>" }`. No auth, no external calls.

### `POST /process-file`

Accepts **exactly one** of three input sources (`pdf_file`, `audio_file`, `prompt`). If none is provided, returns 400.

**Content-Type:** `multipart/form-data`

**Form fields:**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `pdf_file` | File | optional* | MIME: `application/pdf`. Max `MAX_FILE_SIZE_MB`. |
| `audio_file` | File | optional* | MIME: `audio/wav`, `audio/mp3`, `audio/mp4`, `audio/webm`, `audio/ogg` and variants. Max `MAX_FILE_SIZE_MB`. |
| `prompt` | string | optional* | Free text. Max `MAX_PROMPT_CHARS`. |
| `model` | string | no | OpenRouter model id. Default: `mistralai/mistral-7b-instruct:free`. |

&#42; At least one of the three is required.

**Response (200):**
```json
{ "markdown": "# Root\n- item 1\n- item 2\n  - sub-item" }
```

**Errors:**

| Code | When |
| --- | --- |
| 400 | no input · empty prompt · prompt exceeds `MAX_PROMPT_CHARS` |
| 413 | file exceeds `MAX_FILE_SIZE_MB` |
| 415 | file MIME type not supported |
| 422 | could not extract any text from the input |
| 500 | upstream OpenRouter error or transcription/parse failure |

**Example (curl — PDF):**
```bash
curl -X POST http://localhost:8000/process-file \
  -F "pdf_file=@document.pdf" \
  -F "model=x-ai/grok-4-fast:free"
```

**Example (curl — prompt):**
```bash
curl -X POST http://localhost:8000/process-file \
  -F "prompt=Generate a mind map about the Industrial Revolution" \
  -F "model=deepseek/deepseek-chat-v3.1:free"
```

---

## Supported models (OpenRouter free tier)

Any id accepted by OpenRouter works. The ones currently hard-coded in the frontend:

- `x-ai/grok-4-fast:free`
- `deepseek/deepseek-chat-v3.1:free`
- `meta-llama/llama-3.3-70b-instruct:free`
- `mistralai/mistral-small-3.2-24b-instruct:free`
- `openai/gpt-oss-20b:free`

To add a new model: edit the `MODELS` list in `frontend/src/App.js`.

---

## Add a new LLM provider

1. Create a module under `app/services/` exporting `generate_mindmap(text: str, model: str) -> str`.
2. Wire it through `config.py` (new env var for the provider's API key).
3. In `app/routers/process.py`, select the client based on the `model` prefix (e.g. `openrouter/`, `anthropic/`, `openai/`).
4. Update `.env.example` and this README.

> The OpenAI SDK accepts alternative base URLs. For compatible providers (Anthropic via Bedrock, Groq, etc.), just instantiate another `OpenAI(base_url=..., api_key=...)` inside `llm_client.py`.

---

## Environment variables

See `.env.example` in this directory.

| Variable | Default | Notes |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | — | Required. |
| `FRONTEND_ORIGINS` | `http://localhost:3000` | Comma-separated list of CORS-allowed origins. |
| `MAX_FILE_SIZE_MB` | `20` | |
| `MAX_PROMPT_CHARS` | `10000` | |
| `LLM_TIMEOUT_SECONDS` | `60` | Applied to the OpenRouter client. |

---

## System dependencies

- **FFmpeg** — required for `pydub` to open audio formats other than WAV.
  - Windows: `winget install ffmpeg` or a binary from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/).
  - macOS: `brew install ffmpeg`.
  - Linux: `apt install ffmpeg` / `dnf install ffmpeg`.
- **Internet access** — transcription uses Google Speech Recognition (free, no API key, but rate-limited).

---

## Known limitations

- Transcription language hard-coded to `en-US` (`file_utils.transcribe_audio`).
- No retry/backoff on OpenRouter calls (timeout is applied — see `TODO.md` Phase 2 for retry).
- No structured logging.
- No automated tests.
