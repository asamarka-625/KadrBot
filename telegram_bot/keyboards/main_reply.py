# Внешние зависимости
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# Внутренние модули
from telegram_bot.core import config


# Создаем кнопки меню
async def create_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=config.VACANCIES[1]))
    builder.row(KeyboardButton(text=config.FAQ[1]))
    builder.row(KeyboardButton(text=config.DECLARATION[1]))
    builder.row(KeyboardButton(text=config.STATUS[1]))

    return builder.as_markup(resize_keyboard=True)