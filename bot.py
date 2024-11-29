import asyncio
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import init_db, get_user, create_user, add_word
from openai import OpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()  # Создаем роутер для маршрутизации команд

# openai.api_key = OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Инициализация базы данных
init_db()

# Обработчик команды /start
@router.message(Command("start"))
async def start_handler(message: Message):
    await create_user(message.from_user.id)
    await message.answer(
        "Welcome to the Language Bot! Use /add to add a word, /quiz for a quiz, or /settings to update preferences."
    )

# Обработчик команды /add
@router.message(Command("add"))
async def add_word_command_handler(message: Message):
    await message.answer("Please enter the word you want to add:")

    # Динамическая обработка ввода слова
    @router.message(F.text)
    async def process_word(msg: Message):
        user = await get_user(msg.from_user.id)
        if not user:
            await msg.reply("You need to register first with /start.")
            return

        word = msg.text.strip()
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Say this is a test",
                    }
                ],
                model="gpt-3.5-turbo",
            )


            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "user", "content": f"Explain the word '{word}' with an example."}
            #     ]
            # )
            meaning = response['choices'][0]['message']['content']
            example = f"Example: {word} in a sentence."

            await add_word(user['id'], word, meaning, example)
            await msg.reply(f"Word added!\n\nMeaning: {meaning}\n{example}")
        except Exception as e:
            await msg.reply(f"Error while processing the word: {e}")

# Обработчик команды /quiz
@router.message(Command("quiz"))
async def quiz_handler(message: Message):
    await message.reply("Quiz functionality will be implemented soon!")

# Обработчик команды /settings
@router.message(Command("settings"))
async def settings_handler(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Set language"), KeyboardButton("Set notification period"))
    await message.answer("Choose a setting to update:", reply_markup=kb)

# Главная функция для запуска бота
async def main():
    await init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
