#!/usr/bin/env python3
"""
測試 Focus Guardian 串流功能
"""

import time
import threading
import requests

def test_streaming():
    print("🎥 測試串流功能...")
    
    try:
        # 測試主頁面
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ 主頁面可訪問")
        else:
            print(f"❌ 主頁面錯誤: {response.status_code}")
            
        # 測試狀態 API
        response = requests.get('http://localhost:5000/status', timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ 狀態 API: {status_data}")
        else:
            print(f"❌ 狀態 API 錯誤: {response.status_code}")
            
        # 測試串流端點（只檢查是否可訪問）
        response = requests.get('http://localhost:5000/video_feed', 
                              timeout=5, stream=True)
        if response.status_code == 200:
            print("✅ 串流端點可訪問")
            
            # 讀取幾個幀來測試
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    chunk_count += 1
                    if chunk_count > 10:  # 讀取 10 個 chunk 後停止
                        break
            
            print(f"✅ 成功讀取 {chunk_count} 個數據塊")
        else:
            print(f"❌ 串流端點錯誤: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到伺服器 - 請確保 Flask 應用正在運行")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    print("🚀 Focus Guardian 串流測試")
    print("=" * 50)
    print("請確保 Flask 應用已啟動 (python app.py)")
    print("測試將在 3 秒後開始...")
    
    time.sleep(3)
    test_streaming()
    
    print("\n" + "=" * 50)
    print("📱 測試完成！")
    print("如果測試通過，您可以在瀏覽器中訪問:")
    print("• 主頁面: http://localhost:5000/")
    print("• 狀態 API: http://localhost:5000/status")
    print("• 直接串流: http://localhost:5000/video_feed")