import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PUBLIC_SERVER_DOMAIN = "telegrammusictagger.onrender.com"
PRIVATE_SERVER_HOST = "10.131.0.35"
PRIVATE_SERVER_PORT = 8080
