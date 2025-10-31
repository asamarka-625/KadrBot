# Внешние зависимости
from aiogram.types import Message


async def edit_message(message: Message, text: str, keyboard=None):
    add_kwargs = {}
    
    if keyboard is None:
        add_kwargs['reply_markup'] = message.reply_markup
    
    else:
        add_kwargs['reply_markup'] = keyboard

    await message.edit_text(text=text, **add_kwargs)