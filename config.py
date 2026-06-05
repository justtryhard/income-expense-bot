import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME", "finance.db")
raw_allowed_user_id = os.getenv("ALLOWED_USER_ID")

if API_TOKEN is None:
    raise ValueError("API_TOKEN не задан")

if not raw_allowed_user_id:
    raise ValueError("ALLOWED_USER_ID не задан")

try:
    ALLOWED_USER_ID = int(raw_allowed_user_id)
except ValueError as e:
    raise ValueError("ALLOWED_USER_ID должен быть числом") from e