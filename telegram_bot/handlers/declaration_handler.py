# Внешние зависимости
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
# Внутренние модули
from telegram_bot.core import config
from telegram_bot.keyboards import create_declaration_inline, create_instructions_declaration_inline


router = Router()


# Команда информации о предоставлении декларации
@router.message(F.text.in_(config.DECLARATION))
async def declaration_command(message: Message):
    await message.answer(
        "Выберите пожалуйста, в рамках чего вы хотите отправить декларацию",
        reply_markup=await create_declaration_inline()
    )


# Команда информации о предоставлении декларации на госслужбу
@router.callback_query(F.data == "gos_work")
async def gos_instructions_declaration_callback_run(callback_query: CallbackQuery):
    await callback_query.message.answer(
        text="В рамках поступления на госслужбу вам необходимо составить декларацию о доходах.\n\n"
             "Для этого вам необходимо воспользоваться программой по составлению декларации о доходах.\n\n"
             "Данную программу вы можете получить по это ссылке: http://www.kremlin.ru/structure/additional/12"
    )

    await callback_query.message.answer(
        "Также для заполнения справки, вам высылается видео инструкция по ее заполнению.",
        reply_markup=await create_instructions_declaration_inline(),

    )

    await callback_query.answer(
        text="Надеемся, данная инструкция поможет вам быстро заполнить и без проблем заполнить справку БК",
        show_alert=False
    )


# Команда информации о предоставлении декларации компании
@router.callback_query(F.data == "company")
async def company_instructions_declaration_callback_run(callback_query: CallbackQuery):
    await callback_query.answer(
        text="Нет данных",
        show_alert=False
    )