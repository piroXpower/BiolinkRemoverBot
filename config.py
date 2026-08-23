import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Support links
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/YourSupportGroup")
SUPPORT_USER = os.getenv("SUPPORT_USER", "https://t.me/YourSupportUsername")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in your environment or .env file.")
  
