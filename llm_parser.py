import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMParser:
    
    # 使用 LLM 解析使用者的自然語言指令

    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        # System Prompt (提示詞工程)
        self.system_prompt = """你是一個專注力監控系統的指令解析助手。
你的任務是分析使用者的自然語言輸入,並提取出使用者的意圖 (intent) 與持續時間 (duration,單位:分鐘)。

規則:
1. 僅輸出標準的 JSON 格式,不要包含任何 Markdown 標記或其他文字。
2. 合法的 intent 值為: start_focus (開始專注), stop_focus (停止專注), query_status (查詢狀態)。
3. 若使用者未指定時間,預設 duration 為 3 。
4. 對於模糊的指令,優先判斷為 start_focus。

範例輸入:「設定專心念書30分鐘」
範例輸出: {"intent": "start_focus", "duration": 30}

範例輸入:「可以休息了」
範例輸出: {"intent": "stop_focus", "duration": 0}

範例輸入:「現在情況如何？」
範例輸出: {"intent": "query_status", "duration": 0}
"""
    
    def parse_intent(self, user_message):

        # 解析使用者意圖

        try:
            # 準備 Gemini API 請求
            headers = {
                'Content-Type': 'application/json',
            }
            
            # 組合完整的提示詞
            full_prompt = f"{self.system_prompt}\n\n使用者輸入: {user_message}"
            
            data = {
                'contents': [{
                    'parts': [{
                        'text': full_prompt
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.3,
                    'maxOutputTokens': 100
                }
            }
            
            response = requests.post(self.gemini_url, headers=headers, json=data)
            response_data = response.json()
            
            # 提取回應文字
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                result_text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                raise ValueError("無效的 API 回應")
            
            # 移除可能的 Markdown 標記和其他格式
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            # 嘗試提取 JSON 內容
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
            else:
                json_text = result_text
            
            # 解析 JSON
            intent_data = json.loads(json_text)
            
            # 驗證格式
            if 'intent' not in intent_data or 'duration' not in intent_data:
                raise ValueError("Invalid intent format")
            
            return intent_data
            
        except Exception as e:
            print(f"LLM 解析失敗: {e}")
            # 備用方案:簡單的關鍵字匹配
            return self._fallback_parse(user_message)
    
    def _fallback_parse(self, message):

        # 備用的關鍵字匹配解析器
        
        message_lower = message.lower()
        
        # 停止關鍵字
        if any(kw in message_lower for kw in ['停止', '結束', '休息', '不讀', '關閉']):
            return {"intent": "stop_focus", "duration": 0}
        
        # 查詢關鍵字
        if any(kw in message_lower for kw in ['狀態', '怎麼樣', '如何', '進度']):
            return {"intent": "query_status", "duration": 0}
        
        # 預設為開始專注,嘗試提取數字
        duration = 3  # 預設值
        
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            duration = int(numbers[0])
        
        return {"intent": "start_focus", "duration": duration}
    
