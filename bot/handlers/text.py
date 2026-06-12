from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger

from services import (
    analyze_text,
    add_expense,
    add_shopping_item,
    format_expense_saved,
    format_shopping_added,
    format_unknown,
)

router = Router()

# Exclude command messages
def is_plain_text(message: Message) -> bool:
    return (
        message.text is not None
        and not message.text.startswith("/")
    )


@router.message(is_plain_text)
async def handle_text(message: Message):
    """Analyze text message: expense or shopping need."""
    text = message.text.strip()
    status_msg = await message.answer("🤔 Думаю...")

    try:
        result = await analyze_text(text)

        if result.intent == "EXPENSE" and result.amount:
            category = result.category or "Другое"
            title = result.title or text[:50]

            saved = await add_expense(
                amount=result.amount,
                category=category,
                title=title,
                items=result.items,
                raw_text=text,
                source="text",
            )

            if saved:
                reply = format_expense_saved(result.amount, category, title, result.items)
            else:
                reply = "⚠️ Распознала расход, но не удалось сохранить в Notion."

        elif result.intent == "SHOPPING_NEED" and result.shopping_item:
            saved = await add_shopping_item(
                item_name=result.shopping_item,
                source_message=text,
            )
            if saved:
                reply = format_shopping_added(result.shopping_item)
            else:
                reply = "⚠️ Не удалось добавить в список покупок."

        else:
            reply = format_unknown()

        await status_msg.edit_text(reply, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error handling text: {e}")
        await status_msg.edit_text("❌ Что-то пошло не так. Попробуй ещё раз.")
