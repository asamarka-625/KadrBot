# Внешние зависимости
from typing import List, Any
from maxapi.types import Message


# Вспомогательная функция динамического изменения сообщения
async def edit_message(
    message: Message,
    text: str,
    attachments: List[Any] = None
):
    add_kwargs = {}
    
    if attachments is None:
        add_kwargs["attachments"] = message.attachments
    
    else:
        add_kwargs["attachments"] = attachments

    await message.edit(text=text, **add_kwargs)