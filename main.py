import logging
import asyncpg
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import sqlite3
from datetime import datetime

# Замените 'YOUR_API_TOKEN' на ваш токен API, полученный от BotFather в Telegram.
API_TOKEN = os.getenv("TOKEN")

# Устанавливаем уровень логов для отладки.
logging.basicConfig(level=logging.INFO)

# Инициализируем бот и диспетчер.
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())





async def add_data_to_db(user_id, date, number):
    try:
        pool = await asyncpg.create_pool(db_connection)
        async with pool.acquire() as connection:
            await connection.execute(f'''
                INSERT INTO data (user_id, date, number) VALUES ({user_id}, '{date}', {number})
            ''')
        logging.info(f"User {user_id} added data to database.")
    except Exception as e:
        logging.exception(e)

# Обработчик команды /start.
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    try:
        session = await asyncpg.create_pool(db_connection)
        async with session.acquire() as conn:
            async with conn.transaction():
                await conn.execute(f'''
                    INSERT INTO users (user_id) VALUES ({message.from_user.id})
                ''')
            logging.info(f"User added data to database.")
    except Exception as e:
        logging.exception(e)
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
        await add_data_to_db(message.from_user.id, current_date, number)

        await message.answer("Спасибо! Твой ответ был сохранен.")
    except ValueError:
        # Если текст не является числом, отправляем сообщение об ошибке.
        await message.answer("Пожалуйста, введи число!")


if __name__ == '__main__':
    # Запускаем бота.
    executor.start_polling(dp, skip_updates=True)