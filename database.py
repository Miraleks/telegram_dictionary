import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(open("sql/init.sql", "r").read())
    await conn.close()


async def get_user(telegram_id):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
    await conn.close()
    return user


async def create_user(telegram_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING", telegram_id)
    await conn.close()


async def add_word(user_id, word, meaning, example):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO words (user_id, word, meaning, example) VALUES ($1, $2, $3, $4)",
        user_id, word, meaning, example
    )
    await conn.close()