# Внешние зависимости
import asyncio
import logging
# Внутренние модули
from telegram_bot.core import dp, bot
from telegram_bot.middlewares import LoggingMiddleware, ChatActionMiddleware
from telegram_bot.handlers import router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(ChatActionMiddleware())
    dp.callback_query.middleware(ChatActionMiddleware())

    dp.include_router(router)

    await dp.start_polling(bot)


def main_run():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
