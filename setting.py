import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


# -----------------------------------
# 35.160.120.126
# 44.233.151.27
# 34.211.200.85
# https://telegrammusictagger.onrender.com


PUBLIC_SERVER_DOMAIN = "telegrammusictagger.onrender.com"
PRIVATE_SERVER_HOST = "0.0.0.0"
PRIVATE_SERVER_PORT = 80


#WEB_SERVER_HOST = "35.160.120.126"
WEB_SERVER_PORT = 80


WEBHOOK_PATH = "/webhook" # may be api to secure and multi bot handling
WEBHOOK_SECRET = "i-love-boobs"

BASE_WEBHOOK_URL = f"https://{PUBLIC_SERVER_DOMAIN}{WEBHOOK_PATH}" # webhook url