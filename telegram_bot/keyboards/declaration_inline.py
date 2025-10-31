# Внешние зависимости
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
# Внутренние модули
from telegram_bot.core import config


# Создаем инлайн кнопки для предоставления декларации
async def create_declaration_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="В рамках декларации компании", callback_data="company"))
    builder.row(InlineKeyboardButton(text="В рамках поступлении на госслужбу", callback_data="gos_work"))

    return builder.as_markup()


# Создаем инлайн инструкции для заполнения декларации
async def create_instructions_declaration_inline():
    builder = InlineKeyboardBuilder()

    for text, url in config.DECLARATION_INSTRUCTIONS.items():
        builder.row(InlineKeyboardButton(text=text, url=url))

    return builder.as_markup()