# utils/flashcards.py
from utils.notes_db import save_flashcard
import re
import json

def generate_flashcards_from_text(text, max_cards=30, llm="groq", model="llama-3.1-70b-versatile", temperature=0.3):
    """
    Generate high-quality flashcards using LLM.
    Creates proper question-answer pairs from the text.
    """
    
    # Use LLM to generate flashcards
    if llm == "groq":
        from groq import Groq
        import os
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""You are a professional educator creating study flashcards.

        STRICT REQUIREMENTS:
        1. Each flashcard must be COMPLETE and make sense on its own
        2. Question must be a full, grammatically correct question
        3. Answer must be a complete sentence or clear explanation
        4. Keep questions under 15 words
        5. Keep answers under 50 words
        6. NO partial sentences, NO "Define: Answer", NO "What is What?"

        GOOD EXAMPLES:
        {{"front": "What is photosynthesis?", "back": "The process by which plants convert light energy into chemical energy stored in glucose."}}
        {{"front": "Who wrote Romeo and Juliet?", "back": "William Shakespeare wrote Romeo and Juliet in the 1590s."}}
        {{"front": "What is the capital of France?", "back": "Paris is the capital and largest city of France."}}

        BAD EXAMPLES (DO NOT DO THIS):
        {{"front": "What is What?", "back": "the advantage"}}
        {{"front": "Define: Answer", "back": "a) something"}}

        Create {max_cards} flashcards from this text. Return ONLY valid JSON with complete questions and answers:

        {text[:6000]}

        JSON OUTPUT:"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            flashcards_data = json.loads(result)
            
            # Validate and save to database
            cards = []
            for card in flashcards_data[:max_cards]:
                front = card.get("front", "").strip()
                back = card.get("back", "").strip()
                
                # VALIDATION: Skip invalid cards
                if not front or not back:
                    continue
                if len(front) < 10 or len(back) < 10:  # Too short
                    continue
                if "What is What" in front or "Define: Answer" in front:  # Broken cards
                    continue
                if front == back:  # Duplicate
                    continue
                
                save_flashcard(front, back)
                cards.append((front, back))
            
            return cards
            
        except Exception as e:
            print(f"Error generating flashcards with LLM: {e}")
            # Fallback to simple method
            return generate_flashcards_simple(text, max_cards)
    
    elif llm == "ollama":
        import requests
        import os
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        prompt = f"""You are a professional educator creating study flashcards.

        STRICT REQUIREMENTS:
        1. Each flashcard must be COMPLETE and make sense on its own
        2. Question must be a full, grammatically correct question
        3. Answer must be a complete sentence or clear explanation
        4. Keep questions under 15 words
        5. Keep answers under 50 words
        6. NO partial sentences, NO "Define: Answer", NO "What is What?"

        GOOD EXAMPLES:
        {{"front": "What is photosynthesis?", "back": "The process by which plants convert light energy into chemical energy stored in glucose."}}
        {{"front": "Who wrote Romeo and Juliet?", "back": "William Shakespeare wrote Romeo and Juliet in the 1590s."}}
        {{"front": "What is the capital of France?", "back": "Paris is the capital and largest city of France."}}

        BAD EXAMPLES (DO NOT DO THIS):
        {{"front": "What is What?", "back": "the advantage"}}
        {{"front": "Define: Answer", "back": "a) something"}}

        Create {max_cards} flashcards from this text. Return ONLY valid JSON with complete questions and answers:

        {text[:6000]}

        JSON OUTPUT:"""
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature
                }
            )
            
            result = response.json()["response"].strip()
            
            # Extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            flashcards_data = json.loads(result)
            
            cards = []
            for card in flashcards_data[:max_cards]:
                front = card.get("front", "").strip()
                back = card.get("back", "").strip()
                
                if front and back:
                    save_flashcard(front, back)
                    cards.append((front, back))
            
            return cards
            
        except Exception as e:
            print(f"Error generating flashcards with Ollama: {e}")
            return generate_flashcards_simple(text, max_cards)
    
    else:
        return generate_flashcards_simple(text, max_cards)


def generate_flashcards_simple(text, max_cards=30):
    """
    Fallback method: Simple flashcard generation using heuristics.
    Converts statements into questions.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cards = []
    
    for sent in sentences:
        if len(cards) >= max_cards:
            break
        
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 300:
            continue
        
        # Look for definition patterns
        if ' is ' in sent.lower():
            parts = sent.split(' is ', 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                definition = parts[1].strip()
                front = f"What is {subject}?"
                back = definition
                cards.append((front, back))
                save_flashcard(front, back)
                continue
        
        if ' are ' in sent.lower():
            parts = sent.split(' are ', 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                definition = parts[1].strip()
                front = f"What are {subject}?"
                back = definition
                cards.append((front, back))
                save_flashcard(front, back)
                continue
        
        # Look for "X means Y" patterns
        if ' means ' in sent.lower():
            parts = sent.split(' means ', 1)
            if len(parts) == 2:
                term = parts[0].strip()
                meaning = parts[1].strip()
                front = f"What does {term} mean?"
                back = meaning
                cards.append((front, back))
                save_flashcard(front, back)
                continue
        
        # Look for colon definitions
        if ':' in sent:
            parts = sent.split(':', 1)
            if len(parts) == 2:
                term = parts[0].strip()
                definition = parts[1].strip()
                front = f"Define: {term}"
                back = definition
                cards.append((front, back))
                save_flashcard(front, back)
                continue
    
    return cards