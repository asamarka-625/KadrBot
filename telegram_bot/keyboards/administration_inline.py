# Внешние зависимости
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создаем инлайн кнопки должностей в аппарате мировых судей
async def create_administration_positions_inline(data: dict):
    builder = InlineKeyboardBuilder()
    for position in data:
        builder.row(InlineKeyboardButton(
            text=position["name"].capitalize(),
            callback_data=str(position["id"])
        ))

    return builder.as_markup()


# Создаем инлайн кнопки районов
async def create_districts_inline(districts: dict):
    builder = InlineKeyboardBuilder()

    for district in districts:
        print(district)
        builder.button(
            text=district["name"],
            callback_data=district["name"]
        )

    builder.adjust(2)

    builder.row(InlineKeyboardButton(
        text="⬅️ Выбрать другую должность",
        callback_data="back-position"
    ))

    return builder.as_markup()


# Создаем инлайн кнопки участков
async def create_site_inline(sites: dict):
    builder = InlineKeyboardBuilder()
    for site in sites:
        builder.row(InlineKeyboardButton(
            text=f"Участок № {site['id_judgment']}",
            callback_data=str(site['id_judgment'])
        ))

    builder.row(InlineKeyboardButton(text="⬅️ Выбрать другой район поиска", callback_data="back-district"))
    return builder.as_markup()


# Создаем инлайн кнопку подачи документов
async def create_submit_documents_inline(id_site: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📑 Подать документы на этот участок", callback_data=id_site))
    builder.row(InlineKeyboardButton(text="⬅️ Выбрать другой участок", callback_data="back-site"))

    return builder.as_markup()


# Создаем инлайн кнопки для работы с анкетой
async def create_form_inline(id_site: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔑 Авторизоваться", url="https://hr.gov.spb.ru/accounts/login/?"))
    builder.row(InlineKeyboardButton(text="✅ Я заполнил анкету на сайте", callback_data=id_site))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back-form"))

    return builder.as_markup()


# Создаем инлайн кнопки обработки персональных данных
async def create_policy_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✅ Согласиться с обработкой персональных данных",
        callback_data="accept-policy"
    ))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back-policy"))

    return builder.as_markup()

# Создаем инлайн кнопку отправки документов
async def create_sent_documents_inline(id_judgement_place: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✅ Я отправил документы ответственному",
        callback_data=id_judgement_place
    ))

    return builder.as_markup()


# Создаем инлайн кнопку проверки статуса заявки
async def create_check_info_request_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="💡 Информация по заявке",
        callback_data="request"
    ))

    return builder.as_markup()


# Создаем инлайн кнопки проверки статуса заявки
async def create_info_request_inline(status: str):
    builder = InlineKeyboardBuilder()

    if status == "not_read":
        builder.row(InlineKeyboardButton(
            text="🔍 Проверить статус заявки",
            callback_data="request-status"
        ))

    elif status == "not_access":
        builder.row(InlineKeyboardButton(
            text="🔁 Я отправил документы повторно",
            callback_data="request-repeat"
        ))

    elif status == "access":
        builder.row(InlineKeyboardButton(
            text="✅ Перейти к подаче документов",
            callback_data="request-access"
        ))

    return builder.as_markup()


# Создаем инлайн кнопку "Я собрал(а) все документы"
async def create_success_collect_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✅ Я собрал(а) все документы",
        callback_data="request-collect"
    ))

    return builder.as_markup()