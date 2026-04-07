from telethon import TelegramClient
from telethon import connection  # важно!
API_ID = 29093049
API_HASH = 'ef9c85d5d2c2c9dc4d79ae281ec83a8d'

async def get_user_simple(username):
    # Данные вашего MTProto прокси
    proxy_host = "mt.geodema.network"
    proxy_port = 443
    secret = "6fab08b49908b2b3c055eb6e7055ff07"  # например, "ee1234567890abcdef..."

    # Кортеж из трёх элементов (без указания типа)
    proxy = (proxy_host, proxy_port, secret)

    # Указываем класс подключения (выберите нужный)
    conn = connection.ConnectionTcpMTProxyRandomizedIntermediate

    async with TelegramClient('strafimov2006', API_ID, API_HASH,
                              proxy=proxy, connection=conn) as client:
        try:
            user = await client.get_entity(username)
            return user.id
        except Exception as e:
            print(f"Ошибка получения user_id: {e}")
            return None