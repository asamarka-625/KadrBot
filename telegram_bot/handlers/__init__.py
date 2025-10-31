# Внешние зависимости
from aiogram import Router
# Внутренние модули
from telegram_bot.handlers.administration_handler import router as administration_router
from telegram_bot.handlers.committee_handler import router as committee_router
from telegram_bot.handlers.declaration_handler import router as declaration_router
from telegram_bot.handlers.main_handler import router as main_router


router = Router()

router.include_router(main_router)
router.include_router(administration_router)
router.include_router(committee_router)
router.include_router(declaration_router)
