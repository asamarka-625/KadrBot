# Внешние зависимости
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
# Внутренние модули
from telegram_bot.core import config


# Создаем инлайн кнопки выбора места вакансии
async def create_vacancies_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=config.COMMITTEE, callback_data=config.COMMITTEE))
    builder.row(InlineKeyboardButton(text=config.ADMINISTRATION, callback_data=config.ADMINISTRATION))

    return builder.as_markup()


# Создаем инлайн кнопки частых вопросов
async def create_faq_inline():
    builder = InlineKeyboardBuilder()
    for id_, question_answer in config.FAQ_ANSWERS.items():
        question, _ = question_answer
        builder.row(InlineKeyboardButton(text=question, callback_data=f"answer-{id_}"))

    return builder.as_markup()


# Создаем инлайн кнопку назад
async def create_back_inline(back: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад", callback_data=f"back-{back}"))

    return builder.as_markup()