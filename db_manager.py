import json
import time
import os

class DBManager:
    def __init__(self, log_file="session_log.json"):
        self.log_file = log_file
        self.current_session = []

    def log_event(self, event_type, message):
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message
        }
        self.current_session.append(event)
        
        # 持久化儲存 (Append mode)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def get_session_summary(self):
        return self.current_session
        
    def clear_session(self):
        self.current_session = []
        # 可選擇是否要清空 log 檔案，此處僅清空記憶體中的 Session