# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton


# Создаем инлайн кнопки для комитета
def create_committe_inline():
    builder = InlineKeyboardBuilder()
    builder.row(LinkButton(text="🔑 Авторизоваться", url="https://hr.gov.spb.ru/vakansii/?"))
    builder.row(CallbackButton(text="✅ Я авторизовался", payload="auth"))

    return builder.as_markup()