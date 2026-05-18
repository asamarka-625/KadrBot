# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import MessageButton
# Внутренние модули
from max_bot.core import config


# Создаем кнопки меню
def create_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(MessageButton(text=config.VACANCIES[1]))
    builder.row(MessageButton(text=config.FAQ[1]))
    builder.row(MessageButton(text=config.DECLARATION[1]))
    builder.row(MessageButton(text=config.STATUS[1]))

    return builder.as_markup()