# utils/llm.py
import os
import requests
from groq import Groq
import json
from typing import Dict, List

GROQ_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT = os.getenv("DEFAULT_LLM", "groq")

# Groq client (cloud)
groq_client = None
if GROQ_KEY:
    groq_client = Groq(api_key=GROQ_KEY)

def groq_chat(prompt, model="llama-3.1-8b-instant", temperature=0.7, max_tokens=2048):
    from groq import Groq
    client = Groq()

    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return res.choices[0].message.content



def ollama_chat(prompt: str, model="llama2", temperature=0.2, max_tokens=1024):
    """
    Requires Ollama running locally: https://ollama.ai
    Expects an endpoint POST /api/generate with JSON: {model, prompt, temperature}
    Adjust if your Ollama API differs.
    """
    payload = {"model": model, "prompt": prompt, "temperature": temperature, "max_tokens": max_tokens}
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        # The response format may differ across versions; adapt if needed.
        if isinstance(data, dict) and "text" in data:
            return data["text"]
        # fallback: join outputs
        return data.get("response") or json.dumps(data)
    except Exception as e:
        return f"Error calling local Ollama LLM: {e}"

def generate_summary(text: str, llm="default", model=None, temperature=0.2):
    prompt = (
        "You are an expert note-maker. Produce a structured study summary with:\n"
        "- Short introduction\n- Key points (bullet list)\n- Definitions\n- Examples (if applicable)\n- Equations/formulas (if any)\n- Short quiz (3 Q&A)\n\n"
        f"Text:\n{text}\n\nFormat clearly."
    )
    if llm == "ollama":
        return ollama_chat(prompt, model=model or "llama2", temperature=temperature, max_tokens=2048)
    else:
        return groq_chat(prompt, model=model or "llama-3.1-8b-instant", temperature=temperature, max_tokens=2048)



def answer_with_context(question: str, context_chunks: List[Dict], llm="default", model=None, temperature=0.1):
    """
    Build a prompt that includes top context chunks and asks to answer strictly from them.
    Returns {'answer': str, 'used_chunks': [...]}
    """
    context_text = "\n\n---\n\n".join([f"[score:{c['norm_score']:.2f}] {c['chunk']}" for c in context_chunks])
    prompt = (
        "Answer the question using ONLY the context provided below. If the context is insufficient, say so.\n\n"
        f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}\n\n"
        "Answer precisely, cite the chunk index numbers if helpful and include short explanation/steps."
    )
    if llm == "ollama":
        ans = ollama_chat(prompt, model=model or "llama2", temperature=temperature, max_tokens=1024)
    else:
        ans = groq_chat(prompt, model=model or "llama3-8b", temperature=temperature, max_tokens=1024)
    return {"answer": ans, "used_chunks": context_chunks}
