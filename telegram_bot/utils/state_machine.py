# Внешние зависимости
from aiogram.filters.state import State, StatesGroup


class PostAnketaStates(StatesGroup):
    position = State()
    district = State()
    site = State()
    submit_documents = State()
    policy = State()
    accept_policy = State()
    fio = State()
    email = State()
    user_send_docs = State()
    user_waiting_anket = State()
    user_collected_all_docs = State()
    enter_fio = State()


class BookingVisitor(StatesGroup):
    start_booking = State()
    enter_fio = State()
    choose_time_visit_bk = State()
    confirm_windows_bk = State()
    time_visit_hr = State()