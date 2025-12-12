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



def answer_with_context(question, context_chunks, llm="groq", model="llama-3.1-70b-versatile", temperature=0.3):
    """
    Answer questions using retrieved context
    """
    
    # Build context from chunks
    context = "\n\n".join([f"Passage {i+1}: {chunk}" for i, chunk in enumerate(context_chunks)])
    
    prompt = f"""You are a helpful study assistant. Answer the question based on the provided context.

RULES:
1. Answer naturally in complete sentences
2. DO NOT mention chunk numbers, passage numbers, or citations
3. DO NOT say "According to the context" or "Based on the passages"
4. Write as if you naturally know this information
5. If the context doesn't contain the answer, say "I don't have enough information to answer that."
6. Keep answers clear, concise, and well-organized
7. Use bullet points or numbering only when listing multiple items

CONTEXT:
{context}

QUESTION: {question}

ANSWER (respond naturally without references):"""

    if llm == "groq":
        from groq import Groq
        import os
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a knowledgeable study assistant. Answer questions naturally without citing sources or mentioning chunks."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1000
        )
        answer = response.choices[0].message.content.strip()
    
    elif llm == "ollama":
        import requests
        import os
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "system": "You are a knowledgeable study assistant. Answer questions naturally without citing sources or mentioning chunks."
            }
        )
        answer = response.json()["response"].strip()
    
    # Return answer and the chunks used (for optional "show sources" feature)
    used_chunks = [
        {
            "index": i,
            "chunk": chunk,
            "norm_score": 0.8  # You can calculate actual scores if available
        }
        for i, chunk in enumerate(context_chunks[:3])  # Show top 3
    ]
    
    return {
        "answer": answer,
        "used_chunks": used_chunks
    }