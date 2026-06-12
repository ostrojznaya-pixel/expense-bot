from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from loguru import logger
from config.settings import TELEGRAM_ALLOWED_USER_IDS


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            if TELEGRAM_ALLOWED_USER_IDS and user_id not in TELEGRAM_ALLOWED_USER_IDS:
                logger.warning(f"Unauthorized access attempt from user_id={user_id}")
                await event.answer("⛔ Доступ запрещён.")
                return
        return await handler(event, data)
