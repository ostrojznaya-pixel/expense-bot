from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from loguru import logger
from services import (
    get_shopping_list,
    clear_shopping_list,
    get_expenses_for_period,
    format_shopping_list,
    format_expenses_report,
    delete_last_expense,
)
from services.notion import delete_shopping_item

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
        "Я умею:\n"
        "• 🧾 Распознавать фото чеков\n"
        "• 💸 Записывать расходы: «Купила кофе за 75 грн»\n"
        "• 📝 Добавлять в список: «Нужно купить шампунь»\n\n"
        "Команды: /shopping /month /week",
        parse_mode="HTML",
        reply_markup=MAIN_KB,
    )

@router.message(lambda m: m.text == "📊 Расходы за неделю")
@router.message(Command("week"))
async def cmd_week(message: Message):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    expenses = await get_expenses_for_period(start, today)
    report = format_expenses_report(expenses, f"неделю ({start.strftime('%d.%m')} – {today.strftime('%d.%m')})")
    await message.answer(report, reply_markup=MAIN_KB)

@router.message(lambda m: m.text == "📅 Расходы за месяц")
@router.message(Command("month"))
async def cmd_month(message: Message):
    today = date.today()
    start = today.replace(day=1)
    expenses = await get_expenses_for_period(start, today)
    report = format_expenses_report(expenses, f"месяц ({start.strftime('%d.%m')} – {today.strftime('%d.%m')})")
    await message.answer(report, reply_markup=MAIN_KB)

@router.message(lambda m: m.text == "🛒 Список покупок")
@router.message(Command("shopping"))
async def cmd_shopping(message: Message):
    items = await get_shopping_list()
    if not items:
        await message.answer("🎉 Список покупок пуст!", reply_markup=MAIN_KB)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ {item['name']}", callback_data=f"del_{item['id']}")]
        for item in items
    ])
    await message.answer("🛒 <b>Список покупок:</b>\nНажми на пункт чтобы удалить!", parse_mode="HTML", reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("del_"))
async def callback_delete_item(callback: CallbackQuery):
    page_id = callback.data[4:]
    success = await delete_shopping_item(page_id)
    if success:
        await callback.answer("✅ Куплено!")
        items = await get_shopping_list()
        if not items:
            await callback.message.edit_text("🎉 Список покупок пуст!")
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"✅ {item['name']}", callback_data=f"del_{item['id']}")]
                for item in items
            ])
            await callback.message.edit_reply_markup(reply_markup=kb)
    else:
        await callback.answer("Ошибка!")

@router.message(lambda m: m.text == "🗑 Очистить список")
@router.message(Command("clear_shopping"))
async def cmd_clear_shopping(message: Message):
    await clear_shopping_list()
    await message.answer("🧹 Список покупок очищен!", reply_markup=MAIN_KB)


@router.message(lambda m: m.text and "Отменить последний расход" in m.text)
async def cmd_cancel_last(message: Message):
    result = await delete_last_expense()
    await message.answer(result, reply_markup=MAIN_KB)
