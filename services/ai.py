import base64
import json
from typing import Optional
import aiohttp
from openai import AsyncOpenAI
from pydantic import BaseModel
from loguru import logger

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, CATEGORIES, CURRENCY


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class ExpenseResult(BaseModel):
    intent: str  # "EXPENSE" | "SHOPPING_NEED" | "UNKNOWN"
    amount: Optional[float] = None
    category: Optional[str] = None
    title: Optional[str] = None
    items: Optional[list[str]] = None
    shopping_item: Optional[str] = None


SYSTEM_PROMPT = f"""Ты — ассистент для учёта расходов и списка покупок.
Валюта: {CURRENCY}.
Доступные категории расходов: {", ".join(CATEGORIES)}.

Твоя задача — проанализировать сообщение пользователя и вернуть JSON.

Правила определения интента:
- EXPENSE: есть факт покупки/трат + сумма (например: "купила", "заплатила", "потратила", "стоит X грн")
- SHOPPING_NEED: потребность в покупке без суммы (например: "закончилось", "нужно купить", "купить X")
- UNKNOWN: непонятно

Формат ответа — ТОЛЬКО JSON, без пояснений:
{{
  "intent": "EXPENSE" | "SHOPPING_NEED" | "UNKNOWN",
  "amount": <число или null>,
  "category": "<категория из списка или null>",
  "title": "<краткое описание расхода или null>",
  "items": ["товар1", "товар2"] или null,
  "shopping_item": "<название товара для списка покупок или null>"
}}

Примеры:
- "Купила корм Томе за 850 грн" → {{"intent":"EXPENSE","amount":850,"category":"Животные","title":"Корм для кота","items":["корм для кота"],"shopping_item":null}}
- "Закончилась туалетная бумага" → {{"intent":"SHOPPING_NEED","amount":null,"category":null,"title":null,"items":null,"shopping_item":"туалетная бумага"}}
- "Нужно купить шампунь" → {{"intent":"SHOPPING_NEED","amount":null,"category":null,"title":null,"items":null,"shopping_item":"шампунь"}}
- "Потратила 200 грн на кофе с подругой" → {{"intent":"EXPENSE","amount":200,"category":"Посиделки","title":"Кофе с подругой","items":["кофе"],"shopping_item":null}}
"""

RECEIPT_PROMPT = f"""Ты — ассистент для учёта расходов. Проанализируй текст чека или изображение чека.
Валюта: {CURRENCY}.
Доступные категории: {", ".join(CATEGORIES)}.

Извлеки итоговую сумму, список товаров и определи категорию расходов.
Верни ТОЛЬКО JSON без пояснений:
{{
  "amount": <итоговая сумма числом>,
  "category": "<категория>",
  "title": "<краткое название магазина или тип покупки>",
  "items": ["товар1", "товар2", "..."]
}}

Если на чеке несколько категорий — выбери основную (по сумме товаров).
Если сумму определить невозможно — верни amount: null.
"""


async def analyze_text(text: str) -> ExpenseResult:
    """Analyze text message to determine intent, amount, category."""
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        logger.debug(f"AI text response: {raw}")
        data = json.loads(raw)
        return ExpenseResult(**data)
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return ExpenseResult(intent="UNKNOWN")


async def analyze_receipt_image(image_bytes: bytes) -> ExpenseResult:
    """Send receipt image to GPT-4o Vision and extract expense data."""
    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": RECEIPT_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            temperature=0,
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()
        logger.debug(f"AI receipt response: {raw}")
        data = json.loads(raw)
        return ExpenseResult(
            intent="EXPENSE",
            amount=data.get("amount"),
            category=data.get("category"),
            title=data.get("title"),
            items=data.get("items"),
        )
    except Exception as e:
        logger.error(f"Error analyzing receipt image: {e}")
        return ExpenseResult(intent="UNKNOWN")
