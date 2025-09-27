from openai import OpenAI
from app.config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

def generate_mindmap(text: str, model: str):
    reponse = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You create mind map markdown structures."},
            {"role": "user", "content": text},
        ],
    )
    return reponse.choices[0].message.content