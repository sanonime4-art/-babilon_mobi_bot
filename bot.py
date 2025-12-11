# bot.py
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# ===== НАСТРОЙКИ =====

# Токен берём из переменной окружения TOKEN (на Railway ты уже её создаёшь)
TOKEN = os.getenv("TOKEN")   # НИ В КОЕМ СЛУЧАЕ не вставляй сюда сам токен!
ADMIN_ID = 5583235065        # твой Telegram ID (можно оставить как есть)

if not TOKEN:
    raise RuntimeError("TOKEN env var is not set. Please set TOKEN in Railway variables.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ===== СОСТОЯНИЯ (FSM) =====

class OrderState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_package = State()
    waiting_for_confirm = State()


# ===== КНОПКИ =====

def main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [types.KeyboardButton(text="📲 Ввести номер")],
            [types.KeyboardButton(text="ℹ️ О боте")],
        ],
    )
    return kb


def packages_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            text="20 000 MB – 60 с.",
            callback_data="pkg_20000_60"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            text="40 000 MB – 100 с.",
            callback_data="pkg_40000_100"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    return kb


def confirm_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
        types.InlineKeyboardButton(text="✏️ Изменить номер", callback_data="confirm_change_phone"),
    )
    kb.add(
        types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return kb


# ===== ХЭЛПЕРЫ =====

def is_valid_phone(text: str) -> bool:
    """
    Номер должен быть:
    - только цифры
    - длина ровно 9 символов
    Без ограничений по началу (17, 71, 91, 98, 94 и т.д. все допустимы).
    """
    return text.isdigit() and len(text) == 9


def format_order_text(phone: str, package_title: str) -> str:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    return (
        f"<b>Новый запрос на подключение пакета</b>\n\n"
        f"📅 Время: <code>{now}</code>\n"
        f"📞 Номер: <code>{phone}</code>\n"
        f"📦 Пакет: <b>{package_title}</b>"
    )


# ===== ХЭНДЛЕРЫ =====

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        "Салом! 👋\n\n"
        "<b>Babilon-Mobile интернет бастахо</b>\n\n"
        "Барои пайваст кардани баста, рақами телефони Babilon-и худро фиристед "
        "ё зер кунед «📲 Ввести номер».\n\n"
        "Номер должен быть в формате <code>9 цифр</code> (без +992)."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())
    await OrderState.waiting_for_phone.set()


@dp.message_handler(lambda m: m.text == "ℹ️ О боте", state="*")
async def about_bot(message: types.Message, state: FSMContext):
    text = (
        "Ин бот ба шумо кӯмак мекунад, ки бастахои интернети Babilon-Mobile-ро "
        "осон ва зуд фармоиш диҳед 📶\n\n"
        "1️⃣ Введите или отправьте номер (9 цифр)\n"
        "2️⃣ Выберите пакет\n"
        "3️⃣ Подтвердите заявку\n\n"
        "Пас аз тасдиқ, оператор ё администратор пайвасткуниро анҷом медиҳад."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@dp.message_handler(lambda m: m.text == "📲 Ввести номер", state="*")
async def ask_phone(message: types.Message, state: FSMContext):
    await OrderState.waiting_for_phone.set()
    await message.answer(
        "Лутфан рақами Babilon-и худро бо <b>9 рақам</b> фиристед.\n"
        "Масалан: <code>981234567</code>"
    )


@dp.message_handler(state=OrderState.waiting_for_phone, content_types=types.ContentTypes.TEXT)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")

    if not is_valid_phone(phone):
        await message.answer(
            "Номер нодуруст аст ❌\n"
            "Лутфан рақамро бо <b>9 рақам</b> фиристед, бидуни +992.\n"
            "Масалан: <code>981234567</code>"
        )
        return

    await state.update_data(phone=phone)

    await message.answer(
        f"Номер қабул шуд: <code>{phone}</code> ✅\n\n"
        "Ҳоло бастаро интихоб кунед:",
        reply_markup=packages_keyboard(),
    )
    await OrderState.waiting_for_package.set()


@dp.callback_query_handler(lambda c: c.data.startswith("pkg_"), state=OrderState.waiting_for_package)
async def choose_package(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data  # например: pkg_20000_60
    if data == "pkg_20000_60":
        package_title = "20 000 MB – 60 сомони (30 рӯз)"
    elif data == "pkg_40000_100":
        package_title = "40 000 MB – 100 сомони (30 рӯз)"
    else:
        package_title = "Пакет неизвестен"

    await state.update_data(package_title=package_title)

    user_data = await state.get_data()
    phone = user_data.get("phone", "неизвестно")

    text = (
        f"Шумо интихоб кардед:\n"
        f"📞 Номер: <code>{phone}</code>\n"
        f"📦 Пакет: <b>{package_title}</b>\n\n"
        "Тасдиқ мекунед?"
    )

    await callback.message.edit_text(text, reply_markup=confirm_keyboard())
    await OrderState.waiting_for_confirm.set()


@dp.callback_query_handler(lambda c: c.data == "confirm_change_phone", state=OrderState.waiting_for_confirm)
async def change_phone(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await OrderState.waiting_for_phone.set()
    await callback.message.edit_text(
        "Хуб, рақамро аз нав фиристед.\n"
        "Номер без +992, только <b>9 цифр</b>.",
    )


@dp.callback_query_handler(lambda c: c.data == "confirm_yes", state=OrderState.waiting_for_confirm)
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    phone = data.get("phone")
    package_title = data.get("package_title", "Неизвестный пакет")

    # Сообщение пользователю
    await callback.message.edit_text(
        "Дархости шумо қабул шуд ✅\n\n"
        f"📞 Номер: <code>{phone}</code>\n"
        f"📦 Пакет: <b>{package_title}</b>\n\n"
        "Оператор дар муддати кӯтоҳ бастаро пайваст мекунад. 🙌",
    )

    # Сообщение админу
    if ADMIN_ID:
        try:
            text = format_order_text(phone, package_title)
            await bot.send_message(ADMIN_ID, text)
        except Exception as e:
            logging.exception(f"Не удалось отправить сообщение админу: {e}")

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Операция отменена.")
    await state.finish()
    await callback.message.edit_text("Операция отменена ❌")
    await callback.message.answer(
        "Если хотите начать заново, отправьте /start",
        reply_markup=main_menu_keyboard(),
    )


@dp.message_handler(commands=["cancel"], state="*")
async def cancel_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Операция отменена ❌\n"
        "Барои оғоз кардан боз /start фиристед.",
        reply_markup=main_menu_keyboard(),
    )


# ===== ЗАПУСК БОТА =====

if __name__ == "__main__":
    logging.info("Starting Babilon Mobile bot...")
    executor.start_polling(dp, skip_updates=True)
