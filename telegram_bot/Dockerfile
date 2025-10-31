FROM python:3.12.3-slim

# Устанавливаем необходимые зависимости
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /

# Копируем код бота в контейнер
COPY . /telegram_bot

CMD ["python", "-c", "from telegram_bot.main import main_run; main_run()"]
