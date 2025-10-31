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
                                    create_districts_inline, create_site_inline, create_submit_documents_inline)
from telegram_bot.services import (fetch_available_posts, fetch_persons_info, fetch_judgment_places,
                                   fetch_judgement_place_byid)


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
        "Выберите пожалуйста, в какое место вы хотите трудоустроиться",
        reply_markup=await create_vacancies_inline()
    )


# Команда частых вопросов
@router.message(StateFilter('*'), F.text.in_(config.FAQ))
async def faq_command(message: Message, state: FSMContext):
    await state.clear()

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

    else:
        await callback_query.answer()
        return

    await edit_message(
        callback_query.message,
        text=text,
        keyboard=keyboard
    )
    await callback_query.answer(text="Назад", show_alert=False)