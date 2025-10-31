"""""""""""""""""""""""""""Служебные библиотеки"""""""""""""""""""""""""""
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from redis.asyncio import Redis
from redis.exceptions import ReadOnlyError
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
import pickle
import logging
import copy
from dotenv import load_dotenv
"""""""""""""""""""""Внутренние библиотеки"""""""""""""""""""""
from bot_farm_service.app.handlers import router_main
from bot_farm_service.app.middlewares import (ConfigMiddleware, ChatActionMiddleware,
                                              ThrottlingMiddleware, LoggingMiddleware) 

from bot_farm_service.app.data_base.config_sql import setup_database
from bot_farm_service.app.data_base.settings_db import sql_add_data_start, sql_main_admin, sql_add_start_wheel
from bot_farm_service.app.data_base.settings_db import sql_view_list_moder
from bot_farm_service.app.config import Config
from bot_farm_service.app.keyboards import create_close_view_inline, create_open_order_inline, create_review_or_close_inline


load_dotenv()

#Переменная для хранения соединения с redis
redis_client = None

bots = {}


async def safe_redis_write(operation, *args, **kwargs):
    retry = Retry(ExponentialBackoff(), 3)  # 3 попытки с экспоненциальной задержкой
    return await retry.call_with_retry(
        lambda: operation(*args, **kwargs),
        lambda e: isinstance(e, ReadOnlyError)
    )
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    logging.info('Connect to Redis')
    redis_client = await Redis.from_url(
        'redis://redis:6379',
        db=0,
        socket_keepalive=True,  # Поддержание соединения
        retry_on_error=[ReadOnlyError],  # Автоматический ретрай при ошибке записи
        health_check_interval=10  # Проверка здоровья соединения
    )
    
    role = (await redis_client.info('replication'))['role']
    if role != 'master':
        raise ConnectionError("Connected to replica instead of master")
        
    logging.info('setup_database') 
    await setup_database()
    yield
    
    logging.info('Disconnect to Redis')
    await redis_client.close()
    
    
app = FastAPI(lifespan=lifespan)


async def start_bot(bot, bot_config):
    try:
        logging.info('initialize tables') 
        
        await sql_add_data_start(bot_config.id, bot_config.CHANEL_REVIEWS)
        await sql_main_admin(bot_config)
        await sql_add_start_wheel(bot_config.id, bot_config.START_WHEEL)
        
    except:
        pass
        
        
#Регестрируем диспетчер
async def register_dispatcher(dp, bot_config):
    """""""""""""""""""""Добавляем мидлвари в диспетчер"""""""""""""""""""""
    
    dp.message.middleware(ConfigMiddleware(bot_config))
    dp.callback_query.middleware(ConfigMiddleware(bot_config))
    
    dp.message.middleware(LoggingMiddleware(bot_config.id))
    dp.message.middleware(ThrottlingMiddleware(bot_config.SPAM_TIME))
    dp.message.middleware(ChatActionMiddleware())
    
    """""""""""""""""""""Добавляем роутеры в диспетчер"""""""""""""""""""""
    
    dp.include_routers(copy.deepcopy(router_main))
    
    
#Берем бота, конфиг и диспетчер
async def get_bot_config_and_dispatcher(bot_id: int):
    cached_bot = await redis_client.get(f'bot_{bot_id}')
    
    if not cached_bot:
        bot_config = Config(id=bot_id, start_path='../')
        await bot_config.initialize()
        
        await safe_redis_write(redis_client.set, f'bot_{bot_id}', pickle.dumps(bot_config))
            
    else:
        bot_config = pickle.loads(cached_bot)
            
    if not bot_id in bots:
        bot = Bot(token=bot_config.TELEGRAM_BOT_TOKEN,
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        dp = Dispatcher(storage=MemoryStorage(), maintenance_mode=bot_config.MAINTENANCE_MODE,
                        disable_mode=bot_config.DISABLE_MODE)
        
        await register_dispatcher(dp, bot_config)
        
        await start_bot(bot, bot_config)
        
        bots[bot_id] = (bot, dp)
        
        return bot, dp, bot_config
        
    else:
        bot, dp = bots[bot_id]
        
        return bot, dp, bot_config
    
        
async def update_start_bot(bot_id: int):
    bot_config = Config(id=bot_id, start_path='../')
    await bot_config.initialize()
    
    await safe_redis_write(redis_client.set, f'bot_{bot_id}', pickle.dumps(bot_config))
    
    bot = Bot(token=bot_config.TELEGRAM_BOT_TOKEN,
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher(storage=MemoryStorage(), maintenance_mode=bot_config.MAINTENANCE_MODE,
                    disable_mode=bot_config.DISABLE_MODE)
    
    await register_dispatcher(dp, bot_config)
    
    await start_bot(bot, bot_config)
    
    bots[bot_id] = (bot, dp)
    
    
@app.post('/webhook')
async def webhook(request: Request) -> None:
    logging.info("Received webhook request")
    
    content = await request.json()
    
    bot_id = content['bot_id']
    data = content['data']
        
    bot, dp, bot_config = await get_bot_config_and_dispatcher(bot_id)
    
    if 'order_request' in data:
        logging.info("Received webhook order_request")
        
        try:
            await bot.send_message(data['order_request']['id'], '✅ Вы сделали свой заказ, ожидайте его подтверждения!',
                                   reply_markup=await create_open_order_inline(data['order_request']['order_id']))
        except:
            pass
            
        for moder in await sql_view_list_moder(bot_config.id, active=True):
            try:
                await bot.send_message(moder, '❗ Новый заказ ❗', reply_markup=await create_close_view_inline())
                
            except:
                pass
    
    elif 'order_buy' in data:
        logging.info("Received webhook order_buy")
        
        try:
            if data['order_buy']['add_points']:
                await bot.send_message(data['order_buy']['id'], '- Ваша покупка успешно прошла! 😋\n'
                                                               f'- Ваш кэшбэк составил +{data["order_buy"]["add_points"]} 💎\n'
                                                                '- Не забудьте оставить свой отзыв 🌟', reply_markup=await create_review_or_close_inline(bot_config.ALLOWED_REVIEW))
        except:
            pass
            
    elif 'start_bot' in data:
        logging.info("Start Bot")
        await update_start_bot(bot_id)
        
    else:
        logging.info("Update processed")
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        
    return {'status': 'success'}
    
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=False)