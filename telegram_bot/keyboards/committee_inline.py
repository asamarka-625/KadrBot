# Внешние зависимости
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создаем инлайн кнопки для комитета
async def create_committe_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔑 Авторизоваться", url="https://hr.gov.spb.ru/vakansii/?"))
    builder.row(InlineKeyboardButton(text="✅ Я авторизовался", callback_data="auth"))

    return builder.as_markup()