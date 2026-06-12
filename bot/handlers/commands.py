from datetime import date, timedelta
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger

from services import (
    get_shopping_list,
    clear_shopping_list,
    get_expenses_for_period,
    format_shopping_list,
    format_expenses_report,
)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я твой личный ассистент для учёта расходов.\n\n"
        "Что я умею:\n"
        "📸 <b>Фото чека</b> — распознаю и сохраню расход\n"
        "💬 <b>Текст</b> — <i>«Купила кофе за 75 грн»</i>\n"
        "📝 <b>Список</b> — <i>«Закончилось молоко»</i>\n\n"
        "<b>Команды:</b>\n"
        "/shopping — список покупок\n"
        "/clear_shopping — очистить список\n"
        "/month — расходы за месяц\n"
        "/week — расходы за неделю",
        parse_mode="HTML",
    )


@router.message(Command("shopping"))
async def cmd_shopping(message: Message):
    """Show current shopping list."""
    msg = await message.answer("⏳ Загружаю список...")
    try:
        items = await get_shopping_list()
        reply = format_shopping_list(items)
        await msg.edit_text(reply, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /shopping: {e}")
        await msg.edit_text("❌ Не удалось загрузить список покупок.")


@router.message(Command("clear_shopping"))
async def cmd_clear_shopping(message: Message):
    """Mark all shopping items as purchased."""
    msg = await message.answer("⏳ Очищаю список...")
    try:
        count = await clear_shopping_list()
        if count > 0:
            await msg.edit_text(f"✅ Список покупок очищен! Отмечено {count} товаров.")
        else:
            await msg.edit_text("📭 Список уже пуст.")
    except Exception as e:
        logger.error(f"Error in /clear_shopping: {e}")
        await msg.edit_text("❌ Не удалось очистить список.")


@router.message(Command("month"))
async def cmd_month(message: Message):
    """Show expenses for the current month."""
    msg = await message.answer("⏳ Считаю расходы за месяц...")
    try:
        today = date.today()
        start = today.replace(day=1)
        expenses = await get_expenses_for_period(start, today)
        month_name = today.strftime("%B %Y")
        reply = format_expenses_report(expenses, month_name)
        await msg.edit_text(reply, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /month: {e}")
        await msg.edit_text("❌ Не удалось загрузить расходы.")


@router.message(Command("week"))
async def cmd_week(message: Message):
    """Show expenses for the last 7 days."""
    msg = await message.answer("⏳ Считаю расходы за неделю...")
    try:
        today = date.today()
        start = today - timedelta(days=6)
        expenses = await get_expenses_for_period(start, today)
        reply = format_expenses_report(expenses, "неделю")
        await msg.edit_text(reply, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /week: {e}")
        await msg.edit_text("❌ Не удалось загрузить расходы.")
