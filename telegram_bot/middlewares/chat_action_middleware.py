# Внешние зависимости
from aiogram.dispatcher.flags import get_flag
from aiogram.utils.chat_action import ChatActionSender
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
            
        if not isinstance(event, Message):
            return await handler(event, data)

        bot = data["bot"]
        
        chat_action = get_flag(data, "chat_action") or "typing"

        # Если флаг есть
        async with ChatActionSender(
                bot=bot,
                action=chat_action, 
                chat_id=event.chat.id
        ):
            return await handler(event, data)
