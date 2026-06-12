import aiohttp
from aiogram import Router
from aiogram.types import Message
from loguru import logger

from services import (
    analyze_receipt_image,
    add_expense,
    format_expense_saved,
)

router = Router()


@router.message(lambda m: m.photo is not None)
async def handle_photo(message: Message):
    """Handle receipt photo: OCR via GPT-4o Vision → save to Notion."""
    status_msg = await message.answer("🔍 Читаю чек...")

    try:
        # Get highest quality photo
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

        # Download image bytes
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                image_bytes = await resp.read()

        await status_msg.edit_text("🤖 Анализирую чек...")

        result = await analyze_receipt_image(image_bytes)

        if result.intent == "EXPENSE" and result.amount:
            category = result.category or "Другое"
            title = result.title or "Покупка по чеку"

            saved = await add_expense(
                amount=result.amount,
                category=category,
                title=title,
                items=result.items,
                raw_text=message.caption or "фото чека",
                source="photo",
            )

            if saved:
                reply = format_expense_saved(result.amount, category, title, result.items)
            else:
                reply = "⚠️ Чек распознан, но не удалось сохранить в Notion. Проверь настройки."
        else:
            reply = (
                "😕 Не удалось распознать сумму на чеке.\n"
                "Попробуй написать вручную: <i>«Купила продукты за 350 грн»</i>"
            )

        await status_msg.edit_text(reply, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await status_msg.edit_text("❌ Ошибка при обработке фото. Попробуй ещё раз.")
