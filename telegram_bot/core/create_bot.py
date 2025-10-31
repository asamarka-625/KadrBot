# Внешние зависимости
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# Внутренние модули
from telegram_bot.core.config import get_config


config = get_config()


bot = Bot(token=config.TELEGRAM_BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()