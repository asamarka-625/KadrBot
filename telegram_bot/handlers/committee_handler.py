# Внешние зависимости
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
# Внутренние модули
from telegram_bot.core import config
from telegram_bot.keyboards import create_committe_inline


router = Router()


# Колбэк кнопки комитет
@router.callback_query(F.data.lower() == config.COMMITTEE.lower())
async def committe_callback_run(callback: CallbackQuery):
    await callback.message.answer(
        "Для создания анкеты в комитет. Нужно зарегистрироваться или авторизоваться на сайте комитета."
        "\nПройдите пожалуйста, регистрацию или авторизацию"
        "\nЕсли вы прошли авторизацию, нажмите на кнопку 'Я авторизовался'",
        reply_markup=await create_committe_inline()
    )

    await callback.answer()


@router.callback_query(F.data == 'auth')
async def on_auth_message(callback: CallbackQuery):
    await callback.message.answer("Спасибо что зарегистрировались на сайте. Для того, чтобы откликнуться вам необходимо заполнить анкету."
                                  "Следуйте инструкция по заполнению")

    photo = FSInputFile("telegram_bot/docs/komitet_instruct/profile.png")
    await callback.message.answer_photo(
        caption="Перейдите в свой личный кабинет выберите пункт 'Профиль'. В данном пункте, откройте графу 'Общие данные'",
        photo=photo
    )
    await callback.message.answer(
        text="В данном окне, вам нужно заполнить все графы выделенные в красный прямоугольник"
    )

    await callback.answer()