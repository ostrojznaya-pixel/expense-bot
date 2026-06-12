import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Поддержка нескольких пользователей — через запятую: "500635662,1662643304"
_raw_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS", os.getenv("TELEGRAM_ALLOWED_USER_ID", ""))
TELEGRAM_ALLOWED_USER_IDS: set[int] = {
    int(uid.strip()) for uid in _raw_ids.split(",") if uid.strip().isdigit()
}

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

# Notion
NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
NOTION_EXPENSES_DB_ID: str = os.getenv("NOTION_EXPENSES_DB_ID", "")
NOTION_SHOPPING_DB_ID: str = os.getenv("NOTION_SHOPPING_DB_ID", "")

# Categories
CATEGORIES = [
    "Продукты",
    "Курение",
    "Животные",
    "Одежда",
    "Посиделки",
    "Автомобиль",
    "Дом",
    "Другое",
]

CURRENCY = "грн"
