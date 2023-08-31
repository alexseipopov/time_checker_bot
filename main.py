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
from datetime import datetime

from database_handlers.db import insert_new_user

API_TOKEN = os.getenv("TOKEN")


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
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


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    await message.answer("Пожалуйста, введи число!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)