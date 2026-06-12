from datetime import date
from collections import defaultdict
from config.settings import CURRENCY

CATEGORY_EMOJI = {
    "Продукты": "🛒",
    "Курение": "🚬",
    "Животные": "🐾",
    "Одежда": "👗",
    "Посиделки": "☕",
    "Автомобиль": "🚗",
    "Дом": "🏠",
    "Другое": "📦",
}


def format_expense_saved(amount: float, category: str, title: str, items: list[str] | None = None) -> str:
    emoji = CATEGORY_EMOJI.get(category, "📦")
    lines = [
        f"✅ <b>Расход записан!</b>",
        f"{emoji} <b>{category}</b> — <b>{amount:,.0f} {CURRENCY}</b>",
        f"📝 {title}",
    ]
    if items:
        lines.append(f"🧾 Товары: {', '.join(items[:5])}")
    return "\n".join(lines)


def format_shopping_added(item: str) -> str:
    return f"📝 Добавила в список покупок:\n<b>{item}</b>"


def format_shopping_list(items: list[dict]) -> str:
    if not items:
        return "🎉 Список покупок пуст!"
    lines = ["🛍 <b>Список покупок:</b>\n"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['name']}")
    return "\n".join(lines)


def format_expenses_report(expenses: list[dict], period_label: str) -> str:
    if not expenses:
        return f"📊 За {period_label} расходов не найдено."

    by_category: dict[str, float] = defaultdict(float)
    for e in expenses:
        by_category[e["category"]] += e["amount"]

    total = sum(by_category.values())
    lines = [f"📊 <b>Расходы за {period_label}:</b>\n"]

    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    for category, amount in sorted_cats:
        emoji = CATEGORY_EMOJI.get(category, "📦")
        percent = (amount / total * 100) if total > 0 else 0
        bar = _progress_bar(percent)
        lines.append(f"{emoji} <b>{category}</b>")
        lines.append(f"   {bar} {amount:,.0f} {CURRENCY} ({percent:.0f}%)\n")

    lines.append(f"💰 <b>Итого: {total:,.0f} {CURRENCY}</b>")
    return "\n".join(lines)


def _progress_bar(percent: float, length: int = 8) -> str:
    filled = round(percent / 100 * length)
    return "█" * filled + "░" * (length - filled)


def format_unknown() -> str:
    return (
        "🤔 Не совсем понял.\n\n"
        "Я умею:\n"
        "• 📸 Распознавать фото чеков\n"
        "• 💸 Записывать расходы: <i>«Купила кофе за 75 грн»</i>\n"
        "• 📝 Добавлять в список: <i>«Нужно купить шампунь»</i>\n\n"
        "Команды: /shopping /month /week"
    )
