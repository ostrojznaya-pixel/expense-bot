import base64
import json
from typing import Optional
from openai import AsyncOpenAI
from loguru import logger

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, CATEGORIES, CURRENCY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class ExpenseResult:
    def __init__(self, intent="UNKNOWN", amount=None, category=None, title=None, items=None, shopping_item=None):
        self.intent = intent
        self.amount = amount
        self.category = category
        self.title = title
        self.items = items
        self.shopping_item = shopping_item

SYSTEM_PROMPT = f"""Ты — ассистент для учёта расходов и списка покупок.
Валюта: грн.
Доступные категории расходов: {", ".join(CATEGORIES)}.
Верни ТОЛЬКО JSON без пояснений:
{{
  "intent": "EXPENSE" | "SHOPPING_NEED" | "UNKNOWN",
  "amount": число или null,
  "category": "категория или null",
  "title": "краткое описание или null",
  "items": ["товар1"] или null,
  "shopping_item": "название товара или null"
}}"""

RECEIPT_PROMPT = f"""Проанализируй чек. Категории: {", ".join(CATEGORIES)}. Верни ТОЛЬКО JSON:
{{
  "amount": итоговая сумма числом,
  "category": "категория",
  "title": "название магазина",
  "items": ["товар1", "товар2"]
}}"""

async def analyze_text(text: str) -> ExpenseResult:
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
       raw = response.choices[0].message.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return ExpenseResult(
            intent=data.get("intent", "UNKNOWN"),
            amount=data.get("amount"),
            category=data.get("category"),
            title=data.get("title"),
            items=data.get("items"),
            shopping_item=data.get("shopping_item"),
        )
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return ExpenseResult(intent="UNKNOWN")

async def analyze_receipt_image(image_bytes: bytes) -> ExpenseResult:
    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": RECEIPT_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}", "detail": "high"}},
                ],
            }],
            temperature=0,
            max_tokens=500,
        )
       raw = response.choices[0].message.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        return ExpenseResult(
            intent="EXPENSE",
            amount=data.get("amount"),
            category=data.get("category"),
            title=data.get("title"),
            items=data.get("items"),
        )
    except Exception as e:
        logger.error(f"Error analyzing receipt: {e}")
        return ExpenseResult(intent="UNKNOWN")
