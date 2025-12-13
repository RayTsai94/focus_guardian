import requests
import json
import re
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

def call_gemini_api(prompt: str) -> Optional[str]:
    """
    使用 REST API 呼叫 Gemini，相容 Python 3.7
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get('candidates', [])[0].get('content', {}).get('parts', [])[0].get('text', '')
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def parse_intent(user_text: str) -> Dict[str, Any]:
    """
    Step 1: 將自然語言指令解析為 JSON
    """
    print(f"Analyzing Intent for: {user_text}")
    
    prompt = f"""
    你是專注力守門員的意圖分析器。請將使用者輸入轉換為純 JSON。
    
    規則：
    1. intent: "start_focus" (開始), "stop_focus" (停止), "unknown" (未知)
    2. duration: 提取分鐘數 (整數)，預設 25。若為停止指令則為 0。
    
    範例：
    User: "我要專心30分鐘" -> Output: {{"intent": "start_focus", "duration": 30}}
    User: "不讀了" -> Output: {{"intent": "stop_focus", "duration": 0}}
    
    Input: "{user_text}"
    Output:
    """
    
    json_str = call_gemini_api(prompt)
    
    if json_str:
        try:
            # 清理 Markdown 標記
            clean_json = json_str.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except json.JSONDecodeError:
            print("JSON Decode Failed, using fallback rules.")
            
    # Fallback 規則 (若 API 失敗)
    if "專心" in user_text or "開始" in user_text:
        return {"intent": "start_focus", "duration": 25}
    elif "停止" in user_text or "結束" in user_text:
        return {"intent": "stop_focus", "duration": 0}
    
    return {"intent": "unknown", "duration": 0}

def generate_summary(events_log: list) -> str:
    """
    Step 3: 生成總結報告
    """
    violation_count = len([e for e in events_log if e.get('type') == 'violation'])
    
    prompt = f"""
    你是專注力教練。請根據數據給出一句溫暖的中文評語。
    數據：分心次數 {violation_count} 次。
    日誌：{json.dumps(events_log[-5:], ensure_ascii=False)} (僅顯示最後5筆)
    """
    
    summary = call_gemini_api(prompt)
    return summary if summary else f"任務結束。共分心 {violation_count} 次，下次繼續加油！"