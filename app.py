from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from tracker import FocusTracker
from llm_service import parse_intent, generate_summary
from db_manager import DBManager
import os
from dotenv import load_dotenv  # [新增]

# 載入 .env 檔案
load_dotenv()

app = Flask(__name__)

# [修改] 從環境變數讀取
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')