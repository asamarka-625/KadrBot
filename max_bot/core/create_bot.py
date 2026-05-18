# Внешние зависимости
from maxapi import Bot, Dispatcher
from maxapi.enums.parse_mode import ParseMode
from maxapi.client.default import DefaultConnectionProperties
# Внутренние модули
from max_bot.core.config import get_config


config = get_config()

bot = Bot(
    token=config.MAX_BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    default_connection=DefaultConnectionProperties(
        proxy="http://host.docker.internal:15030"
    )
)

dp = Dispatcher()