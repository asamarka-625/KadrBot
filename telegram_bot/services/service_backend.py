# Внешние зависимости
from typing import Dict, List
import requests
# Внутренние модули
from telegram_bot.core import config


def fetch_available_posts(filters="") -> Dict:
    url = f"{config.BACKEND}/api/judgment/vacancy/types{filters}"
    response = requests.get(url)
    return response.json()


def fetch_persons_info(filters="") -> Dict:
    url = f"{config.BACKEND}/api/judgment/district?vacancy={filters}"
    response = requests.get(url)
    return response.json()


def fetch_candidate_status(tgid="") -> Dict:
    url = f"{config.BACKEND}/api/candidate/{tgid}/check-status"
    response = requests.get(url)
    return response.json()


def post_candidate(
        name: str,
        surname: str,
        last_name: str,
        email: str,
        tgid: str,
        id_judgement_place
) -> Dict:
    url = f"{config.BACKEND}/api/candidate/"
    data = {
        "name": name,
        "surname": surname,
        "last_name": last_name,
        "email": email,
        "telegram_id": tgid,
        "id_judgement_place": id_judgement_place
    }

    response = requests.post(url, json=data)
    return response.json()


def fetch_judgement_place_byid(filters) -> Dict:
    url = f"{config.BACKEND}/api/judgment/{filters}"
    response = requests.get(url)
    return response.json()


def get_unique_data_by_field(field: "str", table_func) -> List["str"]:
    records = table_func()
    unique_set_list = set()

    for record in records:
        unique_set_list.add(record["fields"][field])

    return list(unique_set_list)


def fetch_judgment_places(district: str, post: int):
    url = f"{config.BACKEND}/api/judgment/"
    response = requests.get(url)

    filtered_response = [
         dictionary for dictionary in response.json()
         if dictionary['district'] == district and post in dictionary['vacancies']
    ]
    return filtered_response


def resend_document_status(tg_id):
    url = f"{config.BACKEND}/api/candidate/{tg_id}/recheck-status"
    response = requests.put(url)

    return response.json()
