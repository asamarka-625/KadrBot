# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton
# Внутренние модули
from max_bot.core import config


# Создаем инлайн кнопки для предоставления декларации
def create_declaration_inline():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="В рамках декларации компании", payload="company"))
    builder.row(CallbackButton(text="В рамках поступлении на госслужбу", payload="gos_work"))

    return builder.as_markup()


# Создаем инлайн инструкции для заполнения декларации
def create_instructions_declaration_inline():
    builder = InlineKeyboardBuilder()

    for text, url in config.DECLARATION_INSTRUCTIONS.items():
        builder.row(LinkButton(text=text, url=url))

    return builder.as_markup()