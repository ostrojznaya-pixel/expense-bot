"""
Скрипт для автоматического создания баз данных в Notion.
Запускать один раз перед стартом бота.

Использование:
    python setup_notion.py

Скрипт создаст две базы данных на странице-родителе и выведет их ID.
Эти ID нужно вставить в .env файл.
"""

import asyncio
import os
import sys
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
# ID страницы в Notion, где будут созданы базы данных.
# Чтобы найти: открой любую страницу в Notion → скопируй ID из URL.
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "")

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


async def create_expenses_db(notion: AsyncClient, parent_page_id: str) -> str:
    """Create Expenses database and return its ID."""
    print("📊 Создаю базу данных Expenses...")

    db = await notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "💰 Expenses"}}],
        properties={
            "Title": {"title": {}},
            "Amount": {
                "number": {"format": "number"}
            },
            "Category": {
                "select": {
                    "options": [
                        {"name": cat, "color": _category_color(cat)}
                        for cat in CATEGORIES
                    ]
                }
            },
            "Date": {"date": {}},
            "Source": {
                "select": {
                    "options": [
                        {"name": "text", "color": "blue"},
                        {"name": "photo", "color": "green"},
                    ]
                }
            },
            "Raw Text": {"rich_text": {}},
            "Items": {"rich_text": {}},
        },
    )

    db_id = db["id"]
    print(f"✅ Expenses создана! ID: {db_id}")
    return db_id


async def create_shopping_db(notion: AsyncClient, parent_page_id: str) -> str:
    """Create Shopping List database and return its ID."""
    print("🛍 Создаю базу данных Shopping List...")

    db = await notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "🛒 Shopping List"}}],
        properties={
            "Item": {"title": {}},
            "Added At": {"date": {}},
            "Status": {"checkbox": {}},
            "Source Message": {"rich_text": {}},
        },
    )

    db_id = db["id"]
    print(f"✅ Shopping List создана! ID: {db_id}")
    return db_id


async def verify_connection(notion: AsyncClient) -> bool:
    """Check that Notion token is valid."""
    try:
        await notion.users.me()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Notion: {e}")
        return False


def _category_color(category: str) -> str:
    colors = {
        "Продукты": "green",
        "Курение": "gray",
        "Животные": "yellow",
        "Одежда": "pink",
        "Посиделки": "orange",
        "Автомобиль": "blue",
        "Дом": "purple",
        "Другое": "default",
    }
    return colors.get(category, "default")


def print_env_instructions(expenses_id: str, shopping_id: str):
    print("\n" + "=" * 60)
    print("✅ Базы данных успешно созданы!")
    print("=" * 60)
    print("\nДобавь эти строки в свой .env файл:\n")
    print(f"NOTION_EXPENSES_DB_ID={expenses_id}")
    print(f"NOTION_SHOPPING_DB_ID={shopping_id}")
    print("\n" + "=" * 60)


async def main():
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN не задан в .env файле!")
        sys.exit(1)

    if not NOTION_PARENT_PAGE_ID:
        print("❌ NOTION_PARENT_PAGE_ID не задан в .env файле!")
        print("\nКак найти ID страницы:")
        print("1. Открой любую страницу в Notion в браузере")
        print("2. Скопируй ID из URL:")
        print("   https://notion.so/Моя-страница-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("3. Добавь в .env: NOTION_PARENT_PAGE_ID=XXXX...XXXX")
        sys.exit(1)

    notion = AsyncClient(auth=NOTION_TOKEN)

    print("🔌 Проверяю подключение к Notion...")
    if not await verify_connection(notion):
        sys.exit(1)
    print("✅ Подключение успешно!\n")

    expenses_id = await create_expenses_db(notion, NOTION_PARENT_PAGE_ID)
    shopping_id = await create_shopping_db(notion, NOTION_PARENT_PAGE_ID)

    print_env_instructions(expenses_id, shopping_id)


if __name__ == "__main__":
    asyncio.run(main())
