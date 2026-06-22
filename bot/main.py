import asyncio
import sys
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import TELEGRAM_BOT_TOKEN
from bot.middlewares.auth import AuthMiddleware
from bot.handlers import commands, photo, text


async def main():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO",
    )
    logger.add("logs/bot.log", rotation="10 MB", retention="7 days", level="DEBUG")

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        sys.exit(1)

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register auth middleware
    dp.message.middleware(AuthMiddleware())

    # Register routers (order matters: commands first, then photo, then text)
    dp.include_router(commands.router)
    dp.include_router(photo.router)
    dp.include_router(text.router)

    logger.info("🤖 Bot started. Polling...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    

if __name__ == "__main__":
    asyncio.run(main())
