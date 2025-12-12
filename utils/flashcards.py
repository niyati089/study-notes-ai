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
        
        prompt = f"""You are a professional educator. Create {max_cards} study flashcards from the text below.

        CRITICAL RULES:
        1. Questions MUST be complete, clear, and grammatically correct
        2. Questions MUST end with a question mark (?)
        3. Answers MUST be complete sentences (minimum 5 words)
        4. NO bullet points, NO markdown, NO formatting symbols (**, •, -, *)
        5. NO example prompts or demonstrations in questions
        6. Each card tests ONE concept clearly

        WRONG - DO NOT DO THIS:
        {{"front": "What are • No examples?", "back": "provided in the prompt"}}
        {{"front": "Define: • Example", "back": "o Prompt: something"}}

        CORRECT FORMAT:
        {{"front": "What is photosynthesis?", "back": "Photosynthesis is the process by which plants convert light energy into chemical energy."}}
        {{"front": "Who invented the telephone?", "back": "Alexander Graham Bell invented the telephone in 1876."}}

        Text to study:
        {text[:6000]}

        Return ONLY a JSON array of flashcard objects. No explanations, no markdown:"""

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
                
                # ENHANCED VALIDATION:
                if not front or not back:
                    continue
                if len(front) < 10 or len(back) < 10:  # Too short
                    continue
                
                # Skip if contains markdown or bullet formatting
                if any(marker in front for marker in ['**', '•', '- ', '* ', 'o ', '○']):
                    continue
                if any(marker in back for marker in ['**', '•', '- ', '* ', 'o Prompt:', 'o Output:']):
                    continue
                
                # Skip malformed questions
                if front.startswith("Define: •") or front.startswith("What are •"):
                    continue
                if "No examples" in front or "demonstrations" in front:
                    continue
                
                # Question should end with ?
                if not front.endswith("?") and not front.startswith("Define:"):
                    continue
                
                # Answer shouldn't be just a fragment
                if back.count(' ') < 3:  # Less than 3 words
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
        
        # VALIDATION: Skip invalid patterns
        # Skip multiple choice, questions, and fragments
        if any(pattern in sent.lower() for pattern in ['a)', 'b)', 'c)', 'd)', 'answer:', '?', 'i.', 'ii.', 'iii.', 'iv.']):
            continue
        
        # Skip sentences with too few words (likely fragments)
        if len(sent.split()) < 5:
            continue
        
        # Skip sentences that are mostly numbers or special characters
        if sum(c.isalpha() for c in sent) < len(sent) * 0.5:
            continue
        
        # Look for definition patterns
        if ' is ' in sent.lower():
            parts = sent.split(' is ', 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                definition = parts[1].strip()
                
                # Additional validation: subject should be reasonable
                if len(subject.split()) > 10 or len(subject) < 3:
                    continue
                
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
                
                # Additional validation
                if len(subject.split()) > 10 or len(subject) < 3:
                    continue
                
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
                
                if len(term.split()) > 8 or len(term) < 3:
                    continue
                
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
                
                # Skip if term is too long or too short
                if len(term.split()) > 8 or len(term) < 3:
                    continue
                
                front = f"Define: {term}"
                back = definition
                cards.append((front, back))
                save_flashcard(front, back)
                continue
    
    return cards