import logging
import asyncpg
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from datetime import datetime, timedelta

from database_handlers.db import insert_new_user, insert_new_hours_count, update_description

storage = MemoryStorage()

API_TOKEN = os.getenv("TOKEN")


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.row(
    types.KeyboardButton(text="Зафиксировать время"),
    types.KeyboardButton(text="Зафиксировать задачи"),
)
menu_keyboard.add(
    types.KeyboardButton(text="Закрыть период")
)


class UserStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_tasks = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    res = await insert_new_user(message.from_user.id)
    if res:
        await message.answer("Привет! Я буду присылать тебе опросы о потраченном времени!", reply_markup=menu_keyboard)
    else:
        await message.answer("Привет! Ты уже зарегистрирован!", reply_markup=menu_keyboard)


@dp.message_handler(Text(equals=["Зафиксировать время", "Зафиксировать задачи", "Закрыть период"]))
async def get_poll(message: types.Message, state: FSMContext):
    if message.text == "Зафиксировать время":
        await UserStates.waiting_for_time.set()
        await message.answer("Фиксируем время. Введите время целым числом:")
    elif message.text == "Зафиксировать задачи":
        await UserStates.waiting_for_tasks.set()
        await message.answer("Фиксируем задачи. Опишите одним сообщением задачи за день:")
    elif message.text == "Закрыть период":
        await message.answer("Составляем отчет. Введите отчет:")
    else:
        await message.answer("Что-то пошло не так. Попробуйте еще раз.")


@dp.message_handler(state=UserStates.waiting_for_time)
async def process_input(message: types.Message, state: FSMContext):
    try:
        target = int(message.text)
        prev_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        res = await insert_new_hours_count(message.from_user.id, target, prev_date)
        if res:
            await message.answer(f"Ответ успешно сохранен")
        else:
            await message.answer(f"Ответ не сохранен")
    except ValueError:
        await message.answer("Пожалуйста, введи число!")
        return
    await state.finish()


@dp.message_handler(state=UserStates.waiting_for_tasks)
async def process_input(message: types.Message, state: FSMContext):
    try:
        prev_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        res = await update_description(message.from_user.id, message.text, prev_date)
        if res:
            await message.answer(f"Ответ успешно сохранен")
        else:
            await message.answer(f"Ответ не сохранен")
    except ValueError:
        await message.answer("Пожалуйста, введи число!")
        return
    await state.finish()


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    await message.answer("Пожалуйста, введи число!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)