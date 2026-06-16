from datetime import date, timedelta
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
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

MAIN_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Расходы за неделю"), KeyboardButton(text="📅 Расходы за месяц")],
    [KeyboardButton(text="🛒 Список покупок"), KeyboardButton(text="🗑 Очистить список")],
    [KeyboardButton(text="↩️ Отменить последний расход")],
], resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я твой личный ассистент для учёта расходов.\n\n"
        "Просто напиши мне:\n"
        "🧾 <b>Фото чека</b> — распознаю и сохраню расход\n"
        "💬 <b>Текст</b> — «Купила кофе за 75 грн»\n"
        "📝 <b>Список</b> — «Закончилось молоко»\n",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )


@router.message(lambda m: m.text == "🛒 Список покупок")
@router.message(Command("shopping"))
async def cmd_shopping(message: Message):
    items = await get_shopping_list()
    await message.answer(format_shopping_list(items), parse_mode="HTML", reply_markup=MAIN_KB)


@router.message(lambda m: m.text == "🗑 Очистить список")
@router.message(Command("clear_shopping"))
async def cmd_clear_shopping(message: Message):
    await clear_shopping_list()
    await message.answer("🗑 Список покупок очищен!", reply_markup=MAIN_KB)


@router.message(lambda m: m.text == "📊 Расходы за неделю")
@router.message(Command("week"))
async def cmd_week(message: Message):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    expenses = await get_expenses_for_period(start, today)
    await message.answer(format_expenses_report(expenses, "неделю"), parse_mode="HTML", reply_markup=MAIN_KB)


@router.message(lambda m: m.text == "📅 Расходы за месяц")
@router.message(Command("month"))
async def cmd_month(message: Message):
    today = date.today()
    start = today.replace(day=1)
    expenses = await get_expenses_for_period(start, today)
    await message.answer(format_expenses_report(expenses, f"{today.strftime('%B %Y')}"), parse_mode="HTML", reply_markup=MAIN_KB)


@router.message(lambda m: m.text == "↩️ Отменить последний расход")
async def cmd_undo(message: Message):
    from services.notion import delete_last_expense
    result = await delete_last_expense()
    await message.answer(result, reply_markup=MAIN_KB)
