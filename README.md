# Income & Expense Telegram Bot

Telegram-бот для учёта личных доходов и расходов с возможностью просмотра статистики за выбранный период и построением графика по дням.

## Description

Бот позволяет:

- Добавлять доходы

- Добавлять расходы

- Просматривать статистику за выбранный период

- Строить график доходов и расходов по дням (для периода 27–31 день)

Данные хранятся в SQLite базе данных.

Проект реализован на базе асинхронного фреймворка aiogram.

____________________________________________________________

## Tech Stack

- Python 3.10+

- aiogram (Telegram Bot API framework)

- SQLite

- matplotlib

- aiogram-calendar (выбор дат)

____________________________________________________________

## Installation

1. Склонировать репозиторий

```
git clone https://github.com/justtryhard/income-expense-bot.git
cd income-expense-bot
```


2. Создать виртуальное окружение

Windows:

```
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```
python3 -m venv venv
source venv/bin/activate
```

3. Установить зависимости

```
pip install -r requirements.txt
```

4. Сконфигурировать окружение

Заменить значения в config.py:

```
API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
DB_NAME = "bot.db"
```


5. Запустить

```
python main.py
```