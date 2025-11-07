# Внешние зависимости
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# Внутренние модули
from telegram_bot.core import config
from telegram_bot.keyboards import (create_main_keyboard, create_vacancies_inline, create_faq_inline)
from telegram_bot.utils import edit_message, PostAnketaStates
from telegram_bot.keyboards import (create_back_inline, create_form_inline, create_administration_positions_inline,
                                    create_districts_inline, create_site_inline, create_submit_documents_inline,
                                    create_info_request_inline)
from telegram_bot.services import (fetch_available_posts, fetch_persons_info, fetch_judgment_places,
                                   fetch_judgement_place_byid, fetch_candidate_status, resend_document_status)


router = Router()


# Стартовая команда
@router.message(StateFilter('*'), Command('start'))
async def start_command(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Здравствуйте, это бот по помощи подбору вакансии мировых судей администрации Санкт-Петербург",
        reply_markup=await create_main_keyboard()
    )


# Команда выбора места трудоустройства
@router.message(StateFilter('*'), F.text.in_(config.VACANCIES))
async def vacancies_command(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Вакансии организаций ⬇️",
        reply_markup=await create_main_keyboard()
    )

    await message.answer(
        "Выберите пожалуйста, в какое место вы хотите трудоустроиться",
        reply_markup=await create_vacancies_inline()
    )


# Команда частых вопросов
@router.message(StateFilter('*'), F.text.in_(config.FAQ))
async def faq_command(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Ответы на самые частые вопросы по трудоустройству ⬇️",
        reply_markup=await create_main_keyboard()
    )

    await message.answer(
        text="Часто задаваемые вопросы",
        reply_markup=await create_faq_inline()
    )


# Колбэк вопроса FAQ
@router.callback_query(StateFilter('*'), F.data.startswith("answer"))
async def answer_for_faq_callback_run(callback_query: CallbackQuery):
    answer_index = int(callback_query.data.split("-")[1])

    question, answer = config.FAQ_ANSWERS[answer_index]
    await edit_message(
        callback_query.message,
        text=answer,
        keyboard=await create_back_inline(back="faq")
    )
    await callback_query.answer(text=question, show_alert=False)


# Команда для просмотра активной заявке
@router.message(StateFilter('*'), Command("status"))
@router.message(StateFilter('*'), F.text.in_(config.STATUS))
async def request_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id

    data = fetch_candidate_status(user_id)
    status = data["status"]

    if status is None:
        await message.answer("У вас пока нет активной заявке")
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
        await message.answer(text="Ошибка", show_alert=False)
        return

    await message.answer(
        text,
        reply_markup=await create_info_request_inline(status)
    )


# Колбэк кнопки назад
@router.callback_query(StateFilter('*'), F.data.startswith("back"))
async def back_callback_run(callback_query: CallbackQuery, state: FSMContext):
    back = callback_query.data.split("-")[1]

    if back == "faq":
        text = "Часто задаваемые вопросы"
        keyboard = await create_faq_inline()

    elif back == "position":
        data = fetch_available_posts()
        text = "Пожалуйста, выберите интересующую вас должность из списка ниже"
        keyboard = await create_administration_positions_inline(data)

        await state.set_state(PostAnketaStates.position)

    elif back == "district":
        search = await state.get_data()
        post = search["post"]

        if post is None:
            await callback_query.answer(text="Ошибка", show_alert=False)
            return

        districts = fetch_persons_info(post)
        text = "Пожалуйста, выберите в каком районе вы хотели бы рассмотреть работу?"
        keyboard = await create_districts_inline(districts)

        await state.set_state(PostAnketaStates.district)

    elif back == "site":
        await state.set_state(PostAnketaStates.site)

        search = await state.get_data()
        post = search["post"]
        district = search["district"]

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

        text = "Пожалуйста, выберите в какой участок вы хотите отправить данные"
        keyboard = await create_site_inline(sites)

    elif back == "form":
        search = await state.get_data()
        id_site = search["site"]

        if id_site is None:
            await callback_query.answer(text="Ошибка", show_alert=False)
            return

        data = fetch_judgement_place_byid(id_site)

        text = (f"<b>Информация по участку №{id_site}\n\n</b>"
                f"<b>ФИО мирового судьи:</b> \n{data['fio_judgment']}"
                f"<b>\nТелефон:</b>{data['phone']}"
                f"<b>\nРайон:</b><i>{data['district']}</i>"
                f"<b>\nИнформация об участке:</b>\n{data['description']}")

        keyboard = await create_submit_documents_inline(id_site=id_site)

        await state.set_state(PostAnketaStates.submit_documents)

    elif back == "policy":
        search = await state.get_data()
        id_site = search["site"]

        if id_site is None:
            await callback_query.answer(text="Ошибка", show_alert=False)
            return

        text = ("Для создания анкеты в Комитет. Нужно зарегистрироваться или авторизоваться на сайте Комитета."
                "\nПройдите пожалуйста, регистрацию или авторизацию. И затем заполните анкету для конкурса.\n"
                "\nЕсли вы прошли авторизацию и заполнили анкету, нажмите на кнопку "
                "'<b>Я заполнил анкету на сайте</b>'")
        keyboard = await create_form_inline(id_site=id_site)

        await state.set_state(PostAnketaStates.policy)

    else:
        await callback_query.answer()
        return

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=keyboard
    )
    await callback_query.answer(text="Назад", show_alert=False)