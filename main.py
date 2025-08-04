import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv
from keep_alive import keep_alive  # <-- добавлено

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

PRICE_PER_STAR = 222

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

buy_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text="💫 Купить звезды")]]
)

class BuyStars(StatesGroup):
    waiting_for_amount = State()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Добро пожаловать! Нажми кнопку ниже, чтобы купить звёзды:",
        reply_markup=buy_keyboard
    )

@dp.message(lambda msg: msg.text == "💫 Купить звезды")
async def ask_quantity(message: Message, state: FSMContext):
    await message.answer("Сколько звёзд вы хотите купить?\n(Минимум 50)")
    await state.set_state(BuyStars.waiting_for_amount)

@dp.message(BuyStars.waiting_for_amount)
async def get_amount(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text)
        if amount < 50:
            await msg.answer("Минимум 50 звёзд. Попробуй ещё раз.")
            return
        total_price = amount * PRICE_PER_STAR
        await msg.answer(
            f"Итого: {amount} звёзд × {PRICE_PER_STAR} сум = {total_price} сум\n"
            "💸 Кидайте полную сумму на карту: 8888 8888 8888 8888.\n"
            "После оплаты ожидайте подтверждение."
        )
        user_info = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name
        await bot.send_message(
            ADMIN_ID,
            f"💰 Новый заказ от {user_info}:\n"
            f"{amount} звёзд за {total_price} сум"
        )
        await msg.answer("Ваш заказ принят! Скоро с вами свяжутся 😊")
        await state.clear()
    except ValueError:
        await msg.answer("Напиши число, например: 100")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    keep_alive()  # <-- запускаем Flask-сервер
    asyncio.run(main())

