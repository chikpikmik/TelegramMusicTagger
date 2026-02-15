import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

# Local Bot API Server (снимает лимит 20 МБ на загрузку файлов)
# См. docs/LOCAL_BOT_API_SERVER.md
USE_LOCAL_BOT_API = os.getenv("USE_LOCAL_BOT_API", "false").lower() == "true"
LOCAL_BOT_API_BASE = os.getenv("LOCAL_BOT_API_BASE", "http://localhost:8081")



PUBLIC_SERVER_DOMAIN = "telegrammusictagger.onrender.com"

PRIVATE_SERVER_HOST = "0.0.0.0"
PRIVATE_SERVER_PORT = 10000 


#WEB_SERVER_HOST = "35.160.120.126"
#WEB_SERVER_PORT = 443


WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "i-love-boobs" #os.getenv("WEBHOOK_SECRET")

BASE_WEBHOOK_URL = f"https://{PUBLIC_SERVER_DOMAIN}{WEBHOOK_PATH}" # webhook url

USE_WEBHOOK = True #os.getenv("USE_WEBHOOK") == "True"
