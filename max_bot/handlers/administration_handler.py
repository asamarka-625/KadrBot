# Внешние зависимости
import re
from maxapi import Router, F
from maxapi.types import MessageCallback, MessageCreated, InputMedia
from maxapi.context import MemoryContext
# Внутренние модули
from max_bot.core import config
from max_bot.keyboards import (create_back_inline, create_administration_positions_inline,
                               create_districts_inline, create_site_inline,
                               create_submit_documents_inline, create_form_inline, create_policy_inline,
                               create_sent_documents_inline, create_check_info_request_inline,
                               create_info_request_inline, create_success_collect_inline)
from max_bot.utils import edit_message, PostAnketaStates
from max_bot.services import (fetch_available_posts, fetch_persons_info, fetch_judgment_places,
                              fetch_judgement_place_byid, post_candidate, fetch_candidate_status,
                              resend_document_status)


router = Router()


# Колбэк кнопки аппарата мировых судей
@router.message_callback(F.callback.payload.lower() == config.ADMINISTRATION.lower())
async def administration_callback_run(event: MessageCallback, context: MemoryContext):
    post = fetch_available_posts()

    await edit_message(
        message=event.message,
        text="Пожалуйста, выберите интересующую вас должность из списка ниже",
        attachments=[create_administration_positions_inline(post)]
    )

    await context.set_state(PostAnketaStates.position)

# Колбэк информации по заявке
@router.message_callback(F.callback.payload == "request") # StateFilter('*')
async def info_request_callback_run(event: MessageCallback):
    user_id = event.callback.user.user_id

    data = fetch_candidate_status(user_id)
    status = data["status"]
    message_to_candidate = data['message_to_candidate']

    text_to_send =  ("Документы не были получены инспектором. "
                     "Проверьте, отправляли ли вы письмо с документами с указанной выше почты?\n\n "
                     "Попробуйте отправить документы еще раз и нажмите кнопку 'Я отправил документы повторно'"),

    if message_to_candidate:
        text_to_send =  "Сообщение от проверяющего инспектора:\n\n" \
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
        return

    await edit_message(
        event.message,
        text=text,
        attachments=[create_info_request_inline(status)]
    )


# Колбэк статуса заявки
@router.message_callback(F.callback.payload == "request-status")
async def status_request_callback_run(event: MessageCallback):
    user_id = event.callback.user.user_id

    data = fetch_candidate_status(user_id)
    status = data["status"]

    message_to_candidate = data['message_to_candidate']

    text_to_send =  ("Документы не были получены инспектором. "
                     "Проверьте, отправляли ли вы письмо с документами с указанной выше почты?\n\n "
                     "Попробуйте отправить документы еще раз и нажмите кнопку 'Я отправил документы повторно'"),

    if message_to_candidate:
        text_to_send =  "Сообщение от проверяющего инспектора:\n\n" \
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
        return

    await event.message.answer(
        text,
        attachments=[create_info_request_inline(status)]
    )


# Колбэк подачи документов
@router.message_callback(F.callback.payload == "request-repeat")
async def collect_documents_callback_run(event: MessageCallback):
    await event.message.answer(
        text="Наши поздравления!\n"
             "Для поступления на государственную гражданскую службу необходимо предоставить следующие документы."
    )

    await event.message.answer(
        text="Заявление на прием",
        attachments=[InputMedia("max_bot/docs/hiring_docs/Заявление на прием.pdf"),]
    )

    await event.message.answer(
        text="Список док-ов на прием",
        attachments=[InputMedia("max_bot/docs/hiring_docs/Список док-ов на прием.doc"), ]
    )

    await event.message.answer(
        "Также обращаем ваше внимание на заполнение справки о доходах и расходах. Перед заполнением ознакомьтесь с инструкцией,"
        "которая доступна по ссылке: https://disk.yandex.ru/d/HRKduVqyksUlvg",
        attachments=[create_success_collect_inline()]
    )


# Колбэк связи со специалистом
@router.message_callback(F.callback.payload == "request-collect")
async def connect_specialist_callback_run(event: MessageCallback):
    await event.message.answer(
        "Отлично. \nТеперь вам необходимо позвонить специалисту по заполнению справки БК "
        "и направить вашу справку на проверку."
        "\n\nКонтакты специалиста для связи:"
        "\n🧑‍💼 ФИО: Старинская Анна Сергеевна"
        "\n📞 Телефон: 8 (812) 576-60-98"
        "\n📧 Почта: a.starinskaya@zakon.gov.spb.ru"
    )


# Колбэк выбора должности
@router.message_callback(PostAnketaStates.position)
async def positions_callback_run(event: MessageCallback, context: MemoryContext):
    await context.update_data(post=event.callback.payload)

    districts = fetch_persons_info(event.callback.payload)

    await edit_message(
        event.message,
        text="Пожалуйста, выберите в каком районе вы хотели бы рассмотреть работу?",
        attachments=[create_districts_inline(districts)]
    )

    await context.set_state(PostAnketaStates.district)


# Колбэк выбора района
@router.message_callback(PostAnketaStates.district)
async def district_callback_run(event: MessageCallback, context: MemoryContext):
    await context.update_data(district=event.callback.payload)

    search = await context.get_data()
    post = search.get("post")
    district = search.get("district")

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

    await edit_message(
        event.message,
        text="Пожалуйста, выберите в какой участок вы хотите отправить данные",
        attachments=[create_site_inline(sites)]
    )
    await context.set_state(PostAnketaStates.site)


# Колбэк выбора участка
@router.message_callback(PostAnketaStates.site)
async def site_callback_run(event: MessageCallback, context: MemoryContext):
    if not event.callback.payload.isdigit():
        return

    id_site = event.callback.payload
    await context.update_data(site=id_site)

    data = fetch_judgement_place_byid(id_site)

    text = (f"<b>Информация по участку №{id_site}\n\n</b>"
            f"<b>ФИО мирового судьи:</b> \n{data['fio_judgment']}"
            f"<b>\nТелефон:</b> {data['phone']}"
            f"<b>\nРайон:</b><i> {data['district']}</i>"
            f"<b>\nИнформация об участке:</b>\n{data['description']}")

    await edit_message(
        event.message,
        text=text,
        attachments=[create_submit_documents_inline(id_site=id_site)]
    )
    await context.set_state(PostAnketaStates.submit_documents)


# Колбэк подачи документов
@router.message_callback(PostAnketaStates.submit_documents)
async def submit_documents_callback_run(event: MessageCallback, context: MemoryContext):
    if not event.callback.payload.isdigit():
        return

    id_site = event.callback.payload

    text = ("Для создания анкеты в Комитет. Нужно зарегистрироваться или авторизоваться на сайте Комитета."
            "\nПройдите пожалуйста, регистрацию или авторизацию. И затем заполните анкету для конкурса.\n"
            "\nЕсли вы прошли авторизацию и заполнили анкету, нажмите на кнопку '<b>Я заполнил анкету на сайте</b>'")

    await edit_message(
        event.message,
        text=text,
        attachments=[create_form_inline(id_site=id_site)]
    )
    await context.set_state(PostAnketaStates.policy)


# Колбэк персональных данных
@router.message_callback(PostAnketaStates.policy)
async def submit_documents_callback_run(event: MessageCallback, context: MemoryContext):
    if not event.callback.payload.isdigit():
        return

    id_judgement_place = event.callback.payload

    text = ("Важно, вводя ваши персональные данные, вы соглашаетесь с политикой обработки "
            "персональных данных расположенные по адресу:\n"
            "https://disk.yandex.ru/d/n85ncXQJ_Dq7Gw")

    await context.update_data(id_judgement_place=id_judgement_place)

    await edit_message(
        event.message,
        text=text,
        attachments=[create_policy_inline()]
    )
    await context.set_state(PostAnketaStates.accept_policy)


# Колбэк ФИО
@router.message_callback(PostAnketaStates.accept_policy, F.callback.payload == "accept-policy")
async def fio_callback_run(event: MessageCallback, context: MemoryContext):
    text = ("Отлично!\n"
            "Теперь вам нужно заполнить документы и отправить ответственному на проверку\n"
            "Но для начала введите свое ФИО")

    await edit_message(
        event.message,
        text=text,
        attachments=[create_back_inline(back="policy")]
    )
    await context.set_state(PostAnketaStates.fio)


# Читаем ФИО
@router.message_created(PostAnketaStates.fio)
async def read_fio(event: MessageCreated, context: MemoryContext, *args, **kwargs):
    fio_person = event.message.body.text.split(" ")
    if not (2 <= len(fio_person) <= 3):
        await event.message.answer(
            "Неккоректный ввод имени и фамилии. Введите имя, фамилию и отчество полностью через пробел"
        )
        return

    await context.update_data(fio_person=event.message.body.text)
    await event.message.answer("Отлично. Теперь вам нужно ввести свой email. На основе вашего email мы найдем документы.")
    await context.set_state(PostAnketaStates.email)


# Читаем Email
@router.message_created(PostAnketaStates.email)
async def read_email(event: MessageCreated, context: MemoryContext):
    email_person = event.message.body.text
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email_person) == None:
         await event.message.answer("Неккоректный ввод почты. Введите почту в формате user@example.com")
         return

    await context.update_data(email_person=email_person)

    data = await context.get_data()
    id_judgement_place = data.get("id_judgement_place")

    if id_judgement_place is None:
        await event.message.answer("Ошибка")
        return

    for file_name in (
            "Анкета.docx", "Заявка на секретаря суда.doc",
            "Заявка на секретаря суд. заседания.doc", "Список документов на конкурс.doc"
    ):
        await event.message.answer(
            text="".join(file_name.split(".")[:-1]),
            attachments=[InputMedia(f"max_bot/docs/pattern_documents/{file_name}"),]
        )

    await event.message.answer(
        text="Спасибо! После заполнения анкеты, вам необходимо заполнить следующие документы:"
    )
    
    judgment_place = fetch_judgement_place_byid(filters=id_judgement_place)
    inspector_fio = judgment_place.get("inspector").get("first_name")
    inspector_email = judgment_place.get("inspector").get("email")

    await event.message.answer(
        text="После заполнение документов, вам необходимо отправить их на почту ответственного:"
            f"\n<b>🧑‍💼 ФИО ответственного:</b> {inspector_fio}"
            f"\n<b>📧 Почта ответственного:</b> {inspector_email}"
            "\n\nА также копию руководителю:"
            f"\n<b>🧑‍💼 ФИО руководителя:</b> Дупленский Роман Сергеевич"
            f"\n<b>📧 Почта руководителя:</b> duplenskiy@zakon.gov.spb.ru",
        attachments=[create_sent_documents_inline(id_judgement_place=id_judgement_place)]
    )

    await context.set_state(PostAnketaStates.user_send_docs)


# Колбэк подтверждение заявки
@router.message_callback(PostAnketaStates.user_send_docs)
async def accept_request_callback_run(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()
    user_id = str(event.callback.user.user_id)
    fio = data["fio_person"]

    if fio is None:
        return

    fio = fio.split(" ")
    surname = fio[0]
    name = fio[1]
    last_name = fio[2] if len(fio) > 2 else None


    post_candidate(name, surname, last_name, data["email_person"], user_id, data['id_judgement_place'])

    text = ("Отлично!\n"
            "Ваша заявка будет рассмотрена в течении трех рабочих дней.\n\n"
            "Для проверки статуса заявки, нажмите на 'Информация по заявке'")

    await edit_message(
        event.message,
        text=text,
        attachments=[create_check_info_request_inline()]
    )

