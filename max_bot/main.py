# Внешние зависимости
import asyncio
import logging
# Внутренние модули
from max_bot.core import dp, bot
from max_bot.middlewares import LoggingMiddleware
from max_bot.handlers import (main_router, administration_router, committee_router, declaration_router)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    dp.outer_middleware(LoggingMiddleware())
    dp.include_routers(
        main_router, administration_router,
        committee_router, declaration_router
    )
    await dp.start_polling(bot)


def main_run():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
