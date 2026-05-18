# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton


# Создаем инлайн кнопки должностей в аппарате мировых судей
def create_administration_positions_inline(data: dict):
    builder = InlineKeyboardBuilder()
    for position in data:
        builder.row(CallbackButton(
            text=position["name"].capitalize(),
            payload=str(position["id"])
        ))

    return builder.as_markup()


# Создаем инлайн кнопки районов
def create_districts_inline(districts: dict):
    builder = InlineKeyboardBuilder()

    for district in districts:
        builder.row(CallbackButton(
            text=district["name"],
            payload=district["name"]
        ))

    builder.adjust(2)

    builder.row(CallbackButton(
        text="⬅️ Выбрать другую должность",
        payload="back-position"
    ))

    return builder.as_markup()


# Создаем инлайн кнопки участков
def create_site_inline(sites: dict):
    builder = InlineKeyboardBuilder()
    for site in sites:
        builder.row(CallbackButton(
            text=f"Участок № {site['id_judgment']}",
            payload=str(site['id_judgment'])
        ))

    builder.row(CallbackButton(text="⬅️ Выбрать другой район поиска", payload="back-district"))
    return builder.as_markup()


# Создаем инлайн кнопку подачи документов
def create_submit_documents_inline(id_site: str):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="📑 Подать документы на этот участок", payload=id_site))
    builder.row(CallbackButton(text="⬅️ Выбрать другой участок", payload="back-site"))

    return builder.as_markup()


# Создаем инлайн кнопки для работы с анкетой
def create_form_inline(id_site: str):
    builder = InlineKeyboardBuilder()
    builder.row(LinkButton(text="🔑 Авторизоваться", url="https://hr.gov.spb.ru/accounts/login/?"))
    builder.row(CallbackButton(text="✅ Я заполнил анкету на сайте", payload=id_site))
    builder.row(CallbackButton(text="⬅️ Назад", payload="back-form"))

    return builder.as_markup()


# Создаем инлайн кнопки обработки персональных данных
def create_policy_inline():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text="✅ Согласиться с обработкой персональных данных",
        payload="accept-policy"
    ))
    builder.row(CallbackButton(text="⬅️ Назад", payload="back-policy"))

    return builder.as_markup()

# Создаем инлайн кнопку отправки документов
def create_sent_documents_inline(id_judgement_place: str):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text="✅ Я отправил документы ответственному",
        payload=id_judgement_place
    ))

    return builder.as_markup()


# Создаем инлайн кнопку проверки статуса заявки
def create_check_info_request_inline():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text="💡 Информация по заявке",
        payload="request"
    ))

    return builder.as_markup()


# Создаем инлайн кнопки проверки статуса заявки
def create_info_request_inline(status: str):
    builder = InlineKeyboardBuilder()

    if status == "not_read":
        builder.row(CallbackButton(
            text="🔍 Проверить статус заявки",
            payload="request-status"
        ))

    elif status == "not_access":
        builder.row(CallbackButton(
            text="🔁 Я отправил документы повторно",
            payload="request-repeat"
        ))

    elif status == "access":
        builder.row(CallbackButton(
            text="✅ Перейти к подаче документов",
            payload="request-access"
        ))

    return builder.as_markup()


# Создаем инлайн кнопку "Я собрал(а) все документы"
def create_success_collect_inline():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(
        text="✅ Я собрал(а) все документы",
        payload="request-collect"
    ))

    return builder.as_markup()