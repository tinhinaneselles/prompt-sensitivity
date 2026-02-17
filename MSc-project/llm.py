import json
import time
from openai import OpenAI


def get_openai_client() -> OpenAI:
    return OpenAI()


def call_llm_openai(prompt_text: str, model_name: str, temperature: float, top_p: float, max_tokens: int):
    client = get_openai_client()
    t0 = time.time()
    resp = client.responses.create(
        model=model_name,
        input=prompt_text,
        max_output_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    latency_ms = int((time.time() - t0) * 1000)
    return resp.output_text, latency_ms


def try_parse_json(text: str):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text), True
    except Exception:
        return None, False
