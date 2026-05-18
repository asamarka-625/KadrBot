# Внешние зависимости
from maxapi import Router, F
from maxapi.types import BotStarted, Command, MessageCreated, MessageCallback
from maxapi.context import MemoryContext
# Внутренние модули
from max_bot.core import config
from max_bot.keyboards import (create_main_keyboard, create_vacancies_inline, create_faq_inline)
from max_bot.utils import edit_message, PostAnketaStates
from max_bot.keyboards import (create_back_inline, create_form_inline, create_administration_positions_inline,
                               create_districts_inline, create_site_inline, create_submit_documents_inline,
                               create_info_request_inline)
from max_bot.services import (fetch_available_posts, fetch_persons_info, fetch_judgment_places,
                              fetch_judgement_place_byid, fetch_candidate_status, resend_document_status)


router = Router()


# Стартовая команда
@router.bot_started()
async def bot_started(event: BotStarted):

    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Здравствуйте, это бот по помощи подбору вакансии мировых судей администрации Санкт-Петербург",
        attachments=[create_main_keyboard()]
    )


# Команда start
@router.message_created(Command("start"))
async def start_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    await event.message.answer(
        text="Здравствуйте, это бот по помощи подбору вакансии мировых судей администрации Санкт-Петербург",
        attachments=[create_main_keyboard()]
    )


# Команда выбора места трудоустройства
@router.message_created(F.message.body.text.in_(config.VACANCIES))
async def vacancies_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    await event.message.answer(
        text="Выберите пожалуйста, в какое место вы хотите трудоустроиться",
        attachments=[create_vacancies_inline()]
    )


# Команда частых вопросов
@router.message_created(F.message.body.text.in_(config.FAQ))
async def faq_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    await event.message.answer(
        text="Ответы на самые частые вопросы по трудоустройству ⬇️",
        attachments=[create_main_keyboard()]
    )

    await event.message.answer(
        text="Часто задаваемые вопросы",
        attachments=[create_faq_inline()]
    )


# Колбэк вопроса FAQ
@router.message_callback(F.callback.payload.startswith("answer"))
async def answer_for_faq_callback_run(event: MessageCallback):
    answer_index = int(event.callback.payload.split("-")[1])

    question, answer = config.FAQ_ANSWERS[answer_index]
    await edit_message(
        event.message,
        text=answer,
        attachments=[create_back_inline(back="faq")]
    )


# Команда для просмотра активной заявке
@router.message_created(Command("status"))
@router.message_created(F.message.body.text.in_(config.STATUS))
async def request_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    user_id = event.message.sender.user_id

    data = fetch_candidate_status(user_id)
    status = data["status"]

    if status is None:
        await event.message.answer(text="У вас пока нет активной заявке")
        return

    message_to_candidate = data['message_to_candidate']

    text_to_send = ("Документы не были получены инспектором. "
                    "Проверьте, отправляли ли вы письмо с документами с указанной выше почты?\n\n "
                    "Попробуйте отправить документы еще раз и нажмите кнопку 'Я отправил документы повторно'"),

    if message_to_candidate:
        text_to_send = "Сообщение от проверяющего инспектора:\n\n" \
                       f"💬 {str(message_to_candidate)}"

    if status == "not_read":
        text = ("Статус вашей заявки:\n🔃 На рассмотрении. 🔃\n"
                "Ваши документы будут проверены инспектором в ближайшее время.\n"
                "Важно, проверяйте статус ваших документов нажав на кнопку:\n\n"
                "'Проверить статус заявки'")

    elif status == "not_access":
        text = ("Статус вашей заявки: \n❌ Документы не поступили ❌\n"
                f"{text_to_send}",)
        resend_document_status(user_id)

    elif status == "access":
        text = ("Статус вашей заявки: \n✅ Принято в работу ✅\n"
                "Теперь вы можете начать процесс поступления на гос. службу.")

    else:
        await event.message.answer(text="Ошибка")
        return

    await event.message.answer(
        text=text,
        attachments=[create_info_request_inline(status)]
    )


# Колбэк кнопки назад
@router.message_callback(F.callback.payload.startswith("back"))
async def back_callback_run(event: MessageCallback, context: MemoryContext):
    back = event.callback.payload.split("-")[1]

    if back == "faq":
        text = "Часто задаваемые вопросы"
        attachments = [create_faq_inline()]

    elif back == "position":
        data = fetch_available_posts()
        text = "Пожалуйста, выберите интересующую вас должность из списка ниже"
        attachments = [create_administration_positions_inline(data)]

        await context.set_state(PostAnketaStates.position)

    elif back == "district":
        search = await context.get_data()
        post = search["post"]

        if post is None:
            return

        districts = fetch_persons_info(post)
        text = "Пожалуйста, выберите в каком районе вы хотели бы рассмотреть работу?"
        attachments = [create_districts_inline(districts)]

        await context.set_state(PostAnketaStates.district)

    elif back == "site":
        await context.set_state(PostAnketaStates.site)

        search = await context.get_data()
        post = search["post"]
        district = search["district"]

        if post is None or district is None:
            return

        sites = fetch_judgment_places(district, int(post))

        if not sites:
            await edit_message(
                event.message,
                text="Извините, в выбранной области нет доступных участков.",
                attachments=[create_back_inline(back="district")]
            )
            return

        text = "Пожалуйста, выберите в какой участок вы хотите отправить данные"
        attachments = [create_site_inline(sites)]

    elif back == "form":
        search = await context.get_data()
        id_site = search["site"]

        if id_site is None:
            return

        data = fetch_judgement_place_byid(id_site)

        text = (f"<b>Информация по участку №{id_site}\n\n</b>"
                f"<b>ФИО мирового судьи:</b> \n{data['fio_judgment']}"
                f"<b>\nТелефон:</b>{data['phone']}"
                f"<b>\nРайон:</b><i>{data['district']}</i>"
                f"<b>\nИнформация об участке:</b>\n{data['description']}")

        attachments = [create_submit_documents_inline(id_site=id_site)]

        await context.set_state(PostAnketaStates.submit_documents)

    elif back == "policy":
        search = await context.get_data()
        id_site = search["site"]

        if id_site is None:
            return

        text = ("Для создания анкеты в Комитет. Нужно зарегистрироваться или авторизоваться на сайте Комитета."
                "\nПройдите пожалуйста, регистрацию или авторизацию. И затем заполните анкету для конкурса.\n"
                "\nЕсли вы прошли авторизацию и заполнили анкету, нажмите на кнопку "
                "'<b>Я заполнил анкету на сайте</b>'")
        attachments = [create_form_inline(id_site=id_site)]

        await context.set_state(PostAnketaStates.policy)

    else:
        return

    await edit_message(
        event.message,
        text=text,
        attachments=attachments
    )