# Внешние зависимости
from maxapi import Router, F
from maxapi.types import MessageCallback, InputMedia
# Внутренние модули
from max_bot.core import config
from max_bot.keyboards import create_committe_inline


router = Router()


# Колбэк кнопки комитет
@router.message_callback(F.callback.payload.lower() == config.COMMITTEE.lower())
async def committe_callback_run(event: MessageCallback):
    await event.message.answer(
        "Для создания анкеты в комитет. Нужно зарегистрироваться или авторизоваться на сайте комитета."
        "\nПройдите пожалуйста, регистрацию или авторизацию"
        "\nЕсли вы прошли авторизацию, нажмите на кнопку 'Я авторизовался'",
        attachments=[create_committe_inline()]
    )


@router.message_callback(F.callback.payload == "auth")
async def on_auth_message(event: MessageCallback):
    await event.message.answer("Спасибо что зарегистрировались на сайте. Для того, чтобы откликнуться вам необходимо заполнить анкету."
                                  "Следуйте инструкция по заполнению")

    photo = InputMedia("max_bot/docs/komitet_instruct/profile.png")
    await event.message.answer(
        text="Перейдите в свой личный кабинет выберите пункт 'Профиль'. В данном пункте, откройте графу 'Общие данные'",
        attachments=[photo]
    )

    await event.message.answer(
        text="В данном окне, вам нужно заполнить все графы выделенные в красный прямоугольник"
    )