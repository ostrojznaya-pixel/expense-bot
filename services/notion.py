from datetime import datetime, date, timedelta
from typing import Optional
from notion_client import AsyncClient
from loguru import logger

from config.settings import (
    NOTION_TOKEN,
    NOTION_EXPENSES_DB_ID,
    NOTION_SHOPPING_DB_ID,
    CURRENCY,
)

notion = AsyncClient(auth=NOTION_TOKEN)


# ————————————————— EXPENSES —————————————————

async def add_expense(
    amount: float,
    category: str,
    title: str,
    items: Optional[list[str]] = None,
    raw_text: Optional[str] = None,
    source: str = "text",
    expense_date: Optional[date] = None,
) -> bool:
    """Add a new expense record to Notion."""
    try:
        items_str = ", ".join(items) if items else ""
        expense_date = expense_date or date.today()

        await notion.pages.create(
            parent={"database_id": NOTION_EXPENSES_DB_ID},
            properties={
                "Title": {
                    "title": [{"text": {"content": title or "Расход"}}]
                },
                "Amount": {
                    "number": amount
                },
                "Category": {
                    "select": {"name": category}
                },
                "Date": {
                    "date": {"start": expense_date.isoformat()}
                },
                "Source": {
                    "select": {"name": source}
                },
                "Raw Text": {
                    "rich_text": [{"text": {"content": raw_text or ""}}]
                },
                "Items": {
                    "rich_text": [{"text": {"content": items_str}}]
                },
            },
        )
        logger.info(f"Expense added: {amount} {CURRENCY} → {category}")
        return True
    except Exception as e:
        logger.error(f"Error adding expense to Notion: {e}")
        return False


async def delete_last_expense() -> str:
    """Delete the most recent expense from Notion."""
    try:
        response = await notion.databases.query(
            database_id=NOTION_EXPENSES_DB_ID,
            sorts=[{"property": "Date", "direction": "descending"}],
            page_size=1,
        )
        if not response["results"]:
            return "Расходов нет"
        page = response["results"][0]
        props = page["properties"]
        title_list = props["Title"]["title"]
        title = title_list[0]["text"]["content"] if title_list else "—"
        amount = props["Amount"]["number"] or 0
        await notion.pages.update(page["id"], archived=True)
        return f"✅ Удалён последний расход: {title} — {amount} грн"
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return "Ошибка при удалении"


async def get_expenses_for_period(
    start_date: date, end_date: date
) -> list[dict]:
    """Fetch expenses from Notion for a given date range."""
    try:
        response = await notion.databases.query(
            database_id=NOTION_EXPENSES_DB_ID,
            filter={
                "and": [
                    {
                        "property": "Date",
                        "date": {"on_or_after": start_date.isoformat()},
                    },
                    {
                        "property": "Date",
                        "date": {"on_or_before": end_date.isoformat()},
                    },
                ]
            },
            sorts=[{"property": "Date", "direction": "descending"}],
        )
        expenses = []
        for page in response["results"]:
            props = page["properties"]
            amount = props["Amount"]["number"] or 0
            category = (
                props["Category"]["select"]["name"]
                if props["Category"]["select"]
                else "Другое"
            )
            title_list = props["Title"]["title"]
            title = title_list[0]["text"]["content"] if title_list else "—"
            date_str = props["Date"]["date"]["start"] if props["Date"]["date"] else ""
            expenses.append(
                {
                    "amount": amount,
                    "category": category,
                    "title": title,
                    "date": date_str,
                }
            )
        return expenses
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return []


# ————————————————— SHOPPING LIST —————————————————

async def add_shopping_item(item_name: str, source_message: str = "") -> bool:
    """Add item to shopping list in Notion."""
    try:
        await notion.pages.create(
            parent={"database_id": NOTION_SHOPPING_DB_ID},
            properties={
                "Item": {
                    "title": [{"text": {"content": item_name}}]
                },
                "Added At": {
                    "date": {"start": date.today().isoformat()}
                },
                "Status": {
                    "checkbox": False
                },
                "Source Message": {
                    "rich_text": [{"text": {"content": source_message}}]
                },
            },
        )
        logger.info(f"Shopping item added: {item_name}")
        return True
    except Exception as e:
        logger.error(f"Error adding shopping item: {e}")
        return False


async def get_shopping_list() -> list[dict]:
    """Fetch all unchecked items from shopping list."""
    try:
        response = await notion.databases.query(
            database_id=NOTION_SHOPPING_DB_ID,
            filter={
                "property": "Status",
                "checkbox": {"equals": False},
            },
            sorts=[{"property": "Added At", "direction": "ascending"}],
        )
        items = []
        for page in response["results"]:
            props = page["properties"]
            title_list = props["Item"]["title"]
            name = title_list[0]["text"]["content"] if title_list else "—"
            items.append({"id": page["id"], "name": name})
        return items
    except Exception as e:
        logger.error(f"Error fetching shopping list: {e}")
        return []


async def clear_shopping_list() -> int:
    """Mark all shopping items as done. Returns count of cleared items."""
    try:
        response = await notion.databases.query(
            database_id=NOTION_SHOPPING_DB_ID,
            filter={
                "property": "Status",
                "checkbox": {"equals": False},
            },
        )
        count = 0
        for page in response["results"]:
            await notion.pages.update(
                page_id=page["id"],
                properties={"Status": {"checkbox": True}},
            )
            count += 1
        logger.info(f"Cleared {count} shopping items")
        return count
    except Exception as e:
        logger.error(f"Error clearing shopping list: {e}")
        return 0


async def delete_shopping_item(page_id: str) -> bool:
    """Mark a shopping item as done (checked)."""
    try:
        await notion.pages.update(
            page_id=page_id,
            properties={"Status": {"checkbox": True}},
        )
        return True
    except Exception as e:
        logger.error(f"Error deleting shopping item: {e}")
        return False
