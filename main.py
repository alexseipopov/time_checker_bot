import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import sqlite3
from datetime import datetime, timedelta

# Замените 'YOUR_API_TOKEN' на ваш токен API, полученный от BotFather в Telegram.
API_TOKEN = os.getenv("TOKEN")

# Устанавливаем уровень логов для отладки.
logging.basicConfig(level=logging.INFO)

# Инициализируем бот и диспетчер.
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Путь к базе данных SQLite.
db_path = 'data.db'

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS data (user_id INTEGER, date TEXT, number INTEGER)')
    conn.commit()


# Функция для добавления данных в базу данных.
def add_data_to_db(user_id, date, number):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO data (user_id, date, number) VALUES (?, ?, ?)', (user_id, date, number))
        conn.commit()


# Функция для отправки ежедневного вопроса.
async def send_daily_question():
    # Получаем текущую дату и время.
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Формируем вопрос для отправки.
    question_text = f"Сколько часов ты сегодня работал? ({current_date}):"

    # Получаем список всех зарегистрированных пользователей.
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT user_id FROM data')
        users = cursor.fetchall()

    # Отправляем вопрос каждому пользователю.
    for user_id in users:
        await bot.send_message(user_id[0], question_text)


# Обработчик команды /start.
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я буду присылать тебе опросы о потраченном времени!")


# Обработчик текстовых сообщений с числом.
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    try:
        # Пытаемся преобразовать текст в число.
        number = int(message.text)

        # Получаем текущую дату и время.
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Сохраняем данные в базе данных.
        add_data_to_db(message.from_user.id, current_date, number)

        await message.answer("Спасибо! Твой ответ был сохранен.")
    except ValueError:
        # Если текст не является числом, отправляем сообщение об ошибке.
        await message.answer("Пожалуйста, введи число!")


# Цикл для отправки ежедневного вопроса.
async def daily_question_loop():
    while True:
        # Отправляем вопрос.
        await send_daily_question()

        # Ждем 24 часа перед следующей отправкой вопроса.
        await asyncio.sleep(24 * 60 * 60)

if __name__ == '__main__':
    # Запускаем цикл для отправки ежедневного вопроса.
    loop = asyncio.get_event_loop()
    loop.create_task(daily_question_loop())

    # Запускаем бота.
    executor.start_polling(dp, skip_updates=True)