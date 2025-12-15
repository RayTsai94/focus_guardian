from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from tracker import FocusTracker
from llm_service import parse_intent, generate_summary
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_SECRET = os.getenv('LINE_CHANNEL_SECRET')

configuration = Configuration(access_token=LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

tracker = FocusTracker()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    
    # 1. Intent Parsing
    parsed = parse_intent(text)
    intent = parsed.get("intent")
    
    reply = ""
    
    if intent == "start_focus":
        mins = parsed.get("duration", 25)
        if not tracker.is_running:
            tracker.start_tracking(mins)
            reply = f"Got it! Focus mode started for {mins} mins.\nPlease place your phone in front of the camera."
        else:
            reply = "System is already running!"
            
    elif intent == "stop_focus":
        if tracker.is_running:
            tracker.stop_tracking()
            # Wait for logs
            import time
            time.sleep(1)
            summary = generate_summary(tracker.get_logs())
            reply = f"Focus ended.\n{summary}"
        else:
            reply = "No active task right now."
    else:
        reply = "Please say 'Start focus' or 'Stop'."

    with ApiClient(configuration) as api_client:
        line_messaging_api = MessagingApi(api_client)
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

