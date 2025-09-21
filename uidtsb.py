
import asyncio
from telethon import TelegramClient

API_ID = 29093049
API_HASH = 'ef9c85d5d2c2c9dc4d79ae281ec83a8d'

async def get_user_simple(username):
    async with TelegramClient('strafimov2006', API_ID, API_HASH) as client:
        try:
            # Получаем пользователя
            user = await client.get_entity(username)
          #  print(f"ID: {user.id}")
            return user.id
        except Exception as e:
            print(f"Ошибка: {e}")

