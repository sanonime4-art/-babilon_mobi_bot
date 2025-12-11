import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("5936609930:AAFiOZ0fX1BeggQ63EJzNWzfIsM-NlUlufA")   # Берём токен с Railway

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Интернет-пакеты")],
        [KeyboardButton(text="ℹ️ Информация")],
        [KeyboardButton(text="📞 Поддержка")],
    ],
    resize_keyboard=True
)

ADMIN_ID = 5583235065  # Твой Telegram ID

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Салом! Ман боти сунъй мебошам.\n"
        "Барои пайваст кардани бастаҳо аз меню истифода баред.",
        reply_markup=main_menu
    )

@dp.message(lambda msg: msg.text == "📞 Поддержка")
async def support(message: types.Message):
    await message.answer("Пишите сюда: @babilon_mobille")

@dp.message(lambda msg: msg.text == "ℹ️ Информация")
async def info(message: types.Message):
    await message.answer("Информация о боте: версия 1.0")

@dp.message(lambda msg: msg.text == "📦 Интернет-пакеты")
async def packages(message: types.Message):
    await message.answer(
        "Бастаҳои дастрас:\n"
        "20 000 MB – 60 сомонӣ\n"
        "40 000 MB – 100 сомонӣ"
    )

if name == "main":
    dp.run_polling(bot)
