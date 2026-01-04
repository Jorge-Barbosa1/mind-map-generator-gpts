from openai import OpenAI, NotFoundError
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

MINDMAP_SYSTEM_PROMPT = (
    "You are a mind-map generator. Return ONLY markdown suitable for markmap. "
    "Rules: start with a single H1 title, then bullet lists for hierarchy; no code fences; no prose before or after; "
    "keep it concise (<= 120 tokens)."
)

SUMMARY_SYSTEM_PROMPT = (
    "You are a summarizer. Return a concise summary of the provided content. "
    "Rules: plain text or bullet list, <= 80 words, no preamble, no code fences."
)

def _chat(model: str, system_prompt: str, user_content: str, max_tokens: int = 400) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
            top_p=0.9,
        )
        return response.choices[0].message.content
    except NotFoundError as e:
        raise ValueError(f"Model not available: {model}") from e


def generate_mindmap(text: str, model: str) -> str:
    return _chat(model, MINDMAP_SYSTEM_PROMPT, text, max_tokens=400)


def generate_summary(text: str, model: str) -> str:
    return _chat(model, SUMMARY_SYSTEM_PROMPT, text, max_tokens=240)