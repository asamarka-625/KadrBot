# Внешние зависимости
from maxapi import Router, F
from maxapi.types import MessageCallback, MessageCreated
from maxapi.context import MemoryContext
# Внутренние модули
from max_bot.core import config
from max_bot.keyboards import (create_declaration_inline, create_instructions_declaration_inline,
                               create_main_keyboard)


router = Router()


# Команда информации о предоставлении декларации
@router.message_created(F.message.body.text.in_(config.DECLARATION))
async def declaration_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    await event.message.answer(
        "Предоставление декларации о расходах и доходов ⬇️",
        attachments=[create_main_keyboard()]
    )

    await event.message.answer(
        "Выберите пожалуйста, в рамках чего вы хотите отправить декларацию",
        attachments=[create_declaration_inline()]
    )


# Команда информации о предоставлении декларации на госслужбу
@router.message_callback(F.callback.payload == "gos_work")
async def gos_instructions_declaration_callback_run(event: MessageCallback):
    await event.message.answer(
        text="В рамках поступления на госслужбу вам необходимо составить декларацию о доходах.\n\n"
             "Для этого вам необходимо воспользоваться программой по составлению декларации о доходах.\n\n"
             "Данную программу вы можете получить по это ссылке: http://www.kremlin.ru/structure/additional/12"
    )

    await event.message.answer(
        text="Также для заполнения справки, вам высылается видео инструкция по ее заполнению.",
        attachments=[create_instructions_declaration_inline()]

    )

    await event.message.answer(
        text="Надеемся, данная инструкция поможет вам быстро заполнить и без проблем заполнить справку БК"
    )


# Команда информации о предоставлении декларации компании
@router.message_callback(F.callback.payload == "company")
async def company_instructions_declaration_callback_run(event: MessageCallback):
    await event.message.answer(
        text="Нет данных"
    )