# Внешние зависимости
import re
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaDocument
from aiogram.fsm.context import FSMContext
# Внутренние модули
from telegram_bot.core import config
from telegram_bot.keyboards import (create_back_inline, create_administration_positions_inline,
                                    create_districts_inline, create_site_inline,
                                    create_submit_documents_inline, create_form_inline, create_policy_inline,
                                    create_sent_documents_inline, create_check_info_request_inline,
                                    create_info_request_inline, create_success_collect_inline)
from telegram_bot.utils import edit_message, PostAnketaStates
from telegram_bot.services import (fetch_available_posts, fetch_persons_info, fetch_judgment_places,
                                   fetch_judgement_place_byid, post_candidate, fetch_candidate_status,
                                   resend_document_status)


router = Router()


# Колбэк кнопки аппарата мировых судей
@router.callback_query(F.data.lower() == config.ADMINISTRATION.lower())
async def administration_callback_run(callback_query: CallbackQuery, state: FSMContext):
    post = fetch_available_posts()

    await edit_message(
        callback_query.message,
        text="Пожалуйста, выберите интересующую вас должность из списка ниже",
        keyboard=await create_administration_positions_inline(post)
    )

    await state.set_state(PostAnketaStates.position)
    await callback_query.answer(text="Пожалуйста, выберите интересующую вас должность", show_alert=False)


# Колбэк выбора должности
@router.callback_query(PostAnketaStates.position)
async def positions_callback_run(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(post=callback_query.data)

    districts = fetch_persons_info(callback_query.data)

    await edit_message(
        callback_query.message,
        text="Пожалуйста, выберите в каком районе вы хотели бы рассмотреть работу?",
        keyboard=await create_districts_inline(districts)
    )

    await state.set_state(PostAnketaStates.district)
    await callback_query.answer(text="Пожалуйста, выберите район", show_alert=False)


# Колбэк выбора района
@router.callback_query(PostAnketaStates.district)
async def district_callback_run(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(district=callback_query.data)

    search = await state.get_data()
    post = search.get("post")
    district = search.get("district")

    if post is None or district is None:
        await callback_query.answer(text="Ошибка", show_alert=False)
        return

    sites = fetch_judgment_places(district, int(post))

    if not sites:
        await edit_message(
            callback_query.message,
            text="Извините, в выбранной области нет доступных участков.",
            keyboard=await create_back_inline(back="district")
        )
        await callback_query.answer(text="Извините, в выбранной области нет доступных участков", show_alert=False)
        return

    await edit_message(
        callback_query.message,
        text="Пожалуйста, выберите в какой участок вы хотите отправить данные",
        keyboard=await create_site_inline(sites)
    )
    await state.set_state(PostAnketaStates.site)
    await callback_query.answer(text="Пожалуйста, выберите участок", show_alert=False)


# Колбэк выбора участка
@router.callback_query(PostAnketaStates.site)
async def site_callback_run(callback_query: CallbackQuery, state: FSMContext):
    if not callback_query.data.isdigit():
        await callback_query.answer()
        return

    id_site = callback_query.data
    await state.update_data(site=id_site)

    data = fetch_judgement_place_byid(id_site)

    text = (f"<b>Информация по участку №{id_site}\n\n</b>"
            f"<b>ФИО мирового судьи:</b> \n{data['fio_judgment']}"
            f"<b>\nТелефон:</b>{data['phone']}"
            f"<b>\nРайон:</b><i>{data['district']}</i>"
            f"<b>\nИнформация об участке:</b>\n{data['description']}")

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=await create_submit_documents_inline(id_site=id_site)
    )
    await state.set_state(PostAnketaStates.submit_documents)
    await callback_query.answer(text="Информация по участку", show_alert=False)


# Колбэк подачи документов
@router.callback_query(PostAnketaStates.submit_documents)
async def submit_documents_callback_run(callback_query: CallbackQuery, state: FSMContext):
    if not callback_query.data.isdigit():
        await callback_query.answer()
        return

    id_site = callback_query.data

    text = ("Для создания анкеты в Комитет. Нужно зарегистрироваться или авторизоваться на сайте Комитета."
            "\nПройдите пожалуйста, регистрацию или авторизацию. И затем заполните анкету для конкурса.\n"
            "\nЕсли вы прошли авторизацию и заполнили анкету, нажмите на кнопку '<b>Я заполнил анкету на сайте</b>'")

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=await create_form_inline(id_site=id_site)
    )
    await state.set_state(PostAnketaStates.policy)
    await callback_query.answer(text="Создание анкеты", show_alert=False)


# Колбэк персональных данных
@router.callback_query(PostAnketaStates.policy)
async def submit_documents_callback_run(callback_query: CallbackQuery, state: FSMContext):
    if not callback_query.data.isdigit():
        await callback_query.answer()
        return

    id_judgement_place = callback_query.data

    text = ("Важно, вводя ваши персональные данные, вы соглашаетесь с политикой обработки "
            "персональных данных расположенные по адресу:\n"
            "https://disk.yandex.ru/d/n85ncXQJ_Dq7Gw")

    await state.update_data(id_judgement_place=id_judgement_place)

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=await create_policy_inline()
    )
    await state.set_state(PostAnketaStates.accept_policy)
    await callback_query.answer(text="Обработка персональных данных", show_alert=False)


# Колбэк ФИО
@router.callback_query(PostAnketaStates.accept_policy, F.data == "accept-policy")
async def fio_callback_run(callback_query: CallbackQuery, state: FSMContext):
    text = ("Отлично!\n"
            "Теперь вам нужно заполнить документы и отправить ответственному на проверку\n"
            "Но для начала введите свое ФИО")

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=await create_back_inline(back="policy")
    )
    await state.set_state(PostAnketaStates.fio)
    await callback_query.answer(text="Введите свое ФИО", show_alert=False)


# Читаем ФИО
@router.message(PostAnketaStates.fio)
async def read_fio(message: Message, state: FSMContext, *args, **kwargs):
    fio_person = message.text.split(" ")
    if not (2 <= len(fio_person) <= 3):
        await message.answer(
            "Неккоректный ввод имени и фамилии. Введите имя, фамилию и отчество полностью через пробел"
        )
        return

    await state.update_data(fio_person=message.text)
    await message.answer("Отлично. Теперь вам нужно ввести свой email. На основе вашего email мы найдем документы.")
    await state.set_state(PostAnketaStates.email)


# Читаем Email
@router.message(PostAnketaStates.email)
async def read_email(message: Message, state: FSMContext):
    email_person = message.text
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email_person) == None:
         await  message.answer("Неккоректный ввод почты. Введите почту в формате user@example.com")
         return

    await state.update_data(email_person=email_person)

    data = await state.get_data()
    id_judgement_place = data.get("id_judgement_place")

    if id_judgement_place is None:
        await message.answer("Ошибка")
        return

    await message.answer(
        text="Спасибо! После заполнения анкеты, вам необходимо заполнить следующие документы:"
    )

    media_docs = [
        InputMediaDocument(media=FSInputFile("telegram_bot/docs/pattern_documents/Анкета.docx")),
        InputMediaDocument(media=FSInputFile("telegram_bot/docs/pattern_documents/Заявка на секретаря суда.doc")),
        InputMediaDocument(
            media=FSInputFile("telegram_bot/docs/pattern_documents/Заявка на секретаря суд. заседания.doc")
        ),
        InputMediaDocument(media=FSInputFile("telegram_bot/docs/pattern_documents/Список документов на конкурс.doc"))
    ]

    await message.answer_media_group(media=media_docs)

    judgment_place = fetch_judgement_place_byid(filters=id_judgement_place)
    inspector_fio = judgment_place.get("inspector").get("first_name")
    inspector_email = judgment_place.get("inspector").get("email")

    await message.answer(
        text="После заполнение документов, вам необходимо отправить их на почту ответственного:"
            f"\n<b>🧑‍💼 ФИО ответственного:</b> {inspector_fio}"
            f"\n<b>📧 Почта ответственного:</b> {inspector_email}"
            "\n\nА также копию руководителю:"
            f"\n<b>🧑‍💼 ФИО руководителя:</b> Дупленский Роман Сергеевич"
            f"\n<b>📧 Почта руководителя:</b> duplenskiy@zakon.gov.spb.ru",
        reply_markup=await create_sent_documents_inline(id_judgement_place=id_judgement_place)
    )

    await state.set_state(PostAnketaStates.user_send_docs)


# Колбэк подтверждение заявки
@router.callback_query(PostAnketaStates.user_send_docs)
async def accept_request_callback_run(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = str(callback_query.from_user.id)
    fio = data["fio_person"]

    if fio is None:
        await callback_query.answer(text="Ошибка", show_alert=False)
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
        callback_query.message,
        text=text,
        keyboard=await create_check_info_request_inline()
    )

    await callback_query.answer(text="Ваша заявка будет рассмотрена в течении трех рабочих дней", show_alert=False)


# Колбэк информации по заявке
@router.callback_query(F.data == "request")
async def info_request_callback_run(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

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
        await callback_query.answer(text="Ошибка", show_alert=False)
        return

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=await create_info_request_inline(status)
    )
    await callback_query.answer(text="Информация", show_alert=False)


# Колбэк статуса заявки
@router.callback_query(F.data == "request-status")
async def status_request_callback_run(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

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
        await state.set_state(PostAnketaStates.user_collected_all_docs)

    else:
        await callback_query.answer(text="Ошибка", show_alert=False)
        return

    await callback_query.message.answer(
        text,
        reply_markup=await create_info_request_inline(status)
    )
    await callback_query.answer(text="Информация", show_alert=False)


# Команда для просмотра активной заявке
@router.message(StateFilter('*'), Command("status"))
@router.message(StateFilter('*'), F.text.in_(config.STATUS))
async def request_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    data = fetch_candidate_status(user_id)
    status = data["status"]
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
        await state.set_state(PostAnketaStates.user_collected_all_docs)

    else:
        await message.answer(text="Ошибка", show_alert=False)
        return

    await message.answer(
        text,
        reply_markup=await create_info_request_inline(status)
    )


# Колбэк подачи документов
@router.callback_query(F.data == "request-repeat")
async def collect_documents_callback_run(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text="Наши поздравления!\n"
             "Для поступления на государственную гражданскую службу необходимо предоставить следующие документы.")

    media_docs = [
        InputMediaDocument(media=FSInputFile("telegram_bot/docs/hiring_docs/Заявление на прием.pdf")),
        InputMediaDocument(media=FSInputFile("telegram_bot/docs/hiring_docs/Список док-ов на прием.doc"))
    ]

    await callback_query.message.answer(
        text="Документы, которые нужно заполнить для трудоустройства",
    )
    await callback_query.message.answer_media_group(media=media_docs)

    await callback_query.message.answer(
        "Также обращаем ваше внимание на заполнение справки о доходах и расходах. Перед заполнением ознакомьтесь с инструкцией,"
        "которая доступна по ссылке: https://disk.yandex.ru/d/HRKduVqyksUlvg",
        reply_markup=await create_success_collect_inline()
    )

    await callback_query.answer(text="необходимо предоставить следующие документы", show_alert=False)


# Колбэк связи со специалистом
@router.callback_query(F.data == "request-collect")
async def connect_specialist_callback_run(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Отлично. \nТеперь вам необходимо позвонить специалисту по заполнению справки БК "
        "и направить вашу справку на проверку."
        "\n\nКонтакты специалиста для связи:"
        "\n🧑‍💼 ФИО: Старинская Анна Сергеевна"
        "\n📞 Телефон: 8 (812) 576-60-98"
        "\n📧 Почта: a.starinskaya@zakon.gov.spb.ru"
    )
    await callback_query.answer(text="Необходимо позвонить специалисту по заполнению справки БК", show_alert=False)

