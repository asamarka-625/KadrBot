# Внешние зависимости
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

    
class LoggingMiddleware(BaseMiddleware):
    
    def __init__(self):
        super().__init__()
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            if isinstance(handler, (logging.FileHandler, logging.handlers.RotatingFileHandler)):
                logger.removeHandler(handler)

        file_handler = RotatingFileHandler(
            filename='/telegram_bot/logs/bot_log.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # храним 5 backup файлов
            encoding='utf-8'
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        logger.addHandler(file_handler)
    
    
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
         
        user = event.from_user
        
        if isinstance(event, Message):
            if event.text:
                text = event.text.split(' ')
                if len(text) > 1:
                    text = ' '.join(text[1:])
                else:
                    text = text[0]
            else:
                text = 'отправлен объект'

            logging.info(f'Received MESSAGE from [{user.id}]: [{text}]')

        # Обработка callback-запросов
        elif isinstance(event, CallbackQuery):
            callback_data = event.data
            logging.info(f'Received CALLBACK from [{user.id}]: [{callback_data}]')

        # Обработка других типов событий
        else:
            event_type = type(event).__name__
            logging.info(f'Received {event_type} from [{user.id}]')
        
        return await handler(event, data)
