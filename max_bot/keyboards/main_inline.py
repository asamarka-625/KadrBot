# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton
# Внутренние модули
from max_bot.core import config


# Создаем инлайн кнопки выбора места вакансии
def create_vacancies_inline():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text=config.COMMITTEE, payload=config.COMMITTEE))
    builder.row(CallbackButton(text=config.ADMINISTRATION, payload=config.ADMINISTRATION))

    return builder.as_markup()


# Создаем инлайн кнопки частых вопросов
def create_faq_inline():
    builder = InlineKeyboardBuilder()
    for id_, question_answer in config.FAQ_ANSWERS.items():
        question, _ = question_answer
        builder.row(CallbackButton(text=question, payload=f"answer-{id_}"))

    return builder.as_markup()


# Создаем инлайн кнопку назад
def create_back_inline(back: str):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="⬅️ Назад", payload=f"back-{back}"))

    return builder.as_markup()