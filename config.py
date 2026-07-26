import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")
IGNORE_ADMINS = os.getenv("IGNORE_ADMINS", "True").lower() == "true"
