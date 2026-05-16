import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME", "finance.db")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

if API_TOKEN is None:
    raise ValueError("API_TOKEN не задан")