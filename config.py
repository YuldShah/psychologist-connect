import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PSYCHOLOGIST_ID = int(os.getenv("PSYCHOLOGIST_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not PSYCHOLOGIST_ID:
    raise ValueError("PSYCHOLOGIST_ID is not set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")
