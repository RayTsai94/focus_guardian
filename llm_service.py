import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("Error: GEMINI_API_KEY not set")
    model = None

def parse_intent(user_text):
    if not model: return {"intent": "unknown"}
    
    print(f"Analyzing: {user_text}")
    prompt = f"""
    Parse user input into JSON.
    Commands:
    1. Focus/Start: {{"intent": "start_focus", "duration": <minutes_int>}} (default 30)
    2. Stop/Rest: {{"intent": "stop_focus", "duration": 0}}
    
    Input: "{user_text}"
    Output (JSON only):
    """
    try:
        response = model.generate_content(prompt)
        # Clean up markdown code blocks if present
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback rules (English keywords)
        user_text_lower = user_text.lower()
        if "focus" in user_text_lower or "start" in user_text_lower: 
            return {"intent": "start_focus", "duration": 25}
        if "stop" in user_text_lower or "rest" in user_text_lower: 
            return {"intent": "stop_focus", "duration": 0}
        return {"intent": "unknown"}

def generate_summary(events_log):
    if not model: return "Task ended."
    
    violation_count = len([e for e in events_log if e.get('type') == 'violation'])
    prompt = f"""
    Give a short, warm encouragement in English.
    Status: Focus session ended.
    Distractions: {violation_count}.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Task ended. Distracted {violation_count} times."
