import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")
REDIS_URL = os.getenv("REDIS_URL_FOR_BOT", "redis://redis:6379/1")