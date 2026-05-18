# Внешние зависимости
from maxapi.context import StatesGroup, State


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