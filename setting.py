import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


PUBLIC_SERVER_DOMAIN = "telegrammusictagger.onrender.com"

PRIVATE_SERVER_HOST = "0.0.0.0"
PRIVATE_SERVER_PORT = 10000 


#WEB_SERVER_HOST = "35.160.120.126"
#WEB_SERVER_PORT = 443


WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "i-love-boobs"

BASE_WEBHOOK_URL = f"https://{PUBLIC_SERVER_DOMAIN}{WEBHOOK_PATH}" # webhook url