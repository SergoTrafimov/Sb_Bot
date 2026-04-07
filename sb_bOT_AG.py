import asyncio
import time
import sqlite3
import fnmatch
import string
import constant
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import ChatPermissions, ChatMemberUpdated, ContentType
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from uidtsb import get_user_simple
from constant import TOKEN, TO_CHAT_ID, ALLOWED_CHANNELS, ida, helpt, get_chat_id, tt, wlupd
import re
from aiogram.utils.markdown import hlink
from aiogram.client.session.aiohttp import AiohttpSession
import ssl
from aiohttp import TCPConnector
import warnings
import logging



# ========== ДОБАВЛЕНО ДЛЯ ПРОКСИ ==========
import random
import aiohttp
from aiogram.exceptions import TelegramNetworkError

PROXY_SOURCES = [
    # ваши исходные ссылки
    "https://raw.githubusercontent.com/Argh94/Proxy-List/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/socks5.txt",

    # новые ссылки (постоянно обновляемые)
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/refs/heads/master/proxy.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/refs/heads/master/socks5.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/refs/heads/main/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online/socks5.txt",
]

async def fetch_proxy_list():
    proxies = []
    for url in PROXY_SOURCES:
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        lines = [line.strip() for line in text.splitlines() if line.strip()]
                        for line in lines:
                            # Удаляем возможные префиксы socks5:// или socks5:
                            if line.startswith('socks5://'):
                                line = line[9:]
                            elif line.startswith('socks5:'):
                                line = line[6:]

                            # Теперь line должен быть ip:port
                            if ':' not in line:
                                continue
                            parts = line.split(':')
                            if len(parts) < 2:
                                continue
                            ip = parts[0]
                            port = parts[1]
                            # Проверяем, что порт состоит из цифр
                            if not port.isdigit():
                                continue
                            # Убеждаемся, что ip не пустой
                            if ip:
                                proxies.append(f"socks5://{ip}:{port}")
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
    proxies = list(dict.fromkeys(proxies))
    print(f"Загружено {len(proxies)} прокси")
    return proxies
# =========================================

# Удаляем глобальные session и bot (они больше не нужны)
# session = AiohttpSession(proxy=PROXY_URL)   # удалено
# bot = Bot(token=TOKEN, session=session)      # удалено

dp = Dispatcher()
pending_users = {}

kbuc = 0


dp = Dispatcher()
db = sqlite3.connect('sb.db')
cursor = db.cursor()

banwordlist = []
wlu = []  # whitelist urls
bwp = []  # ban words prof
bf = []   # ban frase


def load_lists():
    global banwordlist, wlu, bwp, bf

    with open('banwords.txt', 'r', encoding='utf-8') as file:
        banwordlist = [line.strip() for line in file if line.strip()]

    with open('urlwhitelist.txt', 'r', encoding='utf-8') as f:
        wlu = [line.strip() for line in f if line.strip()]

    with open('banwordsprof.txt', 'r', encoding='utf-8') as l:
        bwp = [line.strip() for line in l if line.strip()]

    with open('banfrase.txt', 'r', encoding='utf-8') as fr:
        bf = [line.strip() for line in fr if line.strip()]


# Загрузите при старте бота
load_lists()



g = InlineKeyboardBuilder()
g.add(InlineKeyboardButton(text="Запретить писать нарушителю 1 час", callback_data="mn"))
g.add(InlineKeyboardButton(text="❗️Запретить писать отправителю 1 час", callback_data="mo"))
g.add(InlineKeyboardButton(text="Забанить нарушителя", callback_data="bn"))
g.add(InlineKeyboardButton(text="❗️Забанить отправителя", callback_data="bo"))
g.add(InlineKeyboardButton(text="Удалить сообщение", callback_data="dd"))
g.add(InlineKeyboardButton(text="Игнорировать", callback_data="sk"))
g.adjust(1)

captcha = InlineKeyboardBuilder()
captcha.add(InlineKeyboardButton(text='Пройти проверку', callback_data='cpt'))

on = 1

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def remove_punctuation(text: str) -> str:
    """Удаляет все знаки препинания из текста"""
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

@dp.message(Command('off'))
async def vkl(message: types.Message, bot: Bot):
    global on
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):
        on = 0
        await message.reply('Бот выключен, чтобы включить введите команду /on')
        await message.delete()
    else:
        await message.reply('Эта штучка для админа')

@dp.message(Command('on'))
async def vkl(message: types.Message, bot: Bot):
    global on
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):
        on = 1
        await message.reply('Бот включен, чтобы выключить введите команду /off')
        await message.delete()
    else:
        await message.delete()


async def open_chat_full_permissions(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
        await message.delete()
        return

    try:

        full_permissions = ChatPermissions(
            # Текстовые сообщения
            can_send_messages=True,

            # Медиа контент
            can_send_media_messages=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=False,
            can_send_audios=True,
            can_send_documents=True,
            can_send_other_messages=True,
            can_send_voice_notes=False,
            # Дополнительные разрешения
            can_add_web_page_previews=True,
            can_send_polls=False,
            # Административные права (обычно оставляем выключенными)
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_topics=False
        )

        # Применяем настройки к группе
        await bot.set_chat_permissions(chat_id, full_permissions)
        await message.reply(
            "🔓Чат открыт с полными разрешениями!\n\n"
            "Адепт, выключи голосовые сообщения!")
        await message.delete()

    except Exception as e:
        await message.reply(f"❌ Ошибка при открытии чата: {str(e)}")
        await message.delete()


async def close_chat_no_permissions(bot: Bot, message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
        await message.delete()
        return

    try:
        # Полностью ограничиваем права
        restricted_permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_audios=False,
            can_send_documents=False,
            can_add_web_page_previews=False,
            can_send_polls=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_topics=False
        )

        await bot.set_chat_permissions(chat_id, restricted_permissions)

        await message.reply("🔒 Чат полностью закрыт!\n\n")
        await message.delete()

    except Exception as e:
        await message.reply(f"❌ Ошибка при закрытии чата: {str(e)}")
        await message.delete()

@dp.message(Command("chaton"))
async def handle_chaton(message: types.Message, bot: Bot):
    await open_chat_full_permissions(bot, message)

@dp.message(Command("chatoff"))
async def handle_chatoff(message: types.Message, bot: Bot):
    await close_chat_no_permissions(bot, message)

@dp.callback_query(lambda i: i.data in ['mn', 'mo', 'bn', 'bo', 'dd', 'sk', "cpt"])
async def rep(callback: types.CallbackQuery, bot: Bot):
    global opid, nid, rmessage_id, rchat_id, opun, nun, nuid
    if callback.data == 'mn':
        permissions = ChatPermissions(can_send_messages=False)
        until_date = time.time() + 3600
        await bot.restrict_chat_member(rchat_id, nid, permissions, until_date=until_date)
        await bot.send_message(rchat_id, f"Пользователь @{nun} замучен на 1 час.")
        chat_id = callback.from_user.id
        await bot.send_message(chat_id, "Готово")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'mo':
        permissions = ChatPermissions(can_send_messages=False)
        until_date = time.time() + 3600
        await bot.restrict_chat_member(rchat_id, opid, permissions, until_date=until_date)
        await bot.send_message(rchat_id, f"Пользователь @{opun} замучен на 1 час.")
        chat_id = callback.from_user.id
        await bot.send_message(chat_id, "Готово")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'bn':
        await bot.ban_chat_member(rchat_id, nid)
        await bot.send_message(rchat_id, f"Пользователь @{nun} забанен")
        chat_id = callback.from_user.id
        await bot.send_message(chat_id, "Готово")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'bo':
        chat_id=callback.from_user.id
        await bot.ban_chat_member(rchat_id, nid)
        await bot.delete_message(rchat_id, rmessage_id)
        await bot.send_message(rchat_id, f"Пользователь @{opun} забанен")
        await bot.send_message(chat_id, "Готово")
        await bot.send_message(chat_id, "Готово")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == "dd":
        await bot.delete_message(rchat_id, rmessage_id)
        chat_id=callback.from_user.id
        await bot.send_message(chat_id, "Готово")
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == "sk":
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == "cpt":
        user_id = callback.from_user.id

        if user_id in pending_users:
            chat_id = pending_users[user_id]['chat_id']

            # Подтверждаем нажатие кнопки
            await callback.answer(
                "Отлично! Вы человек, приятного общения",
                show_alert=True)

            # Обрабатываем успешное прохождение капчи
            await handle_captcha_success(bot, user_id, chat_id)
        else:
            await callback.answer(
                f"⚠️ Внимание!\n\nЭто сообщение для {nuf}",
                show_alert=True)




class DebugState(StatesGroup):
    waiting_for_debug_message = State()


class AutorState(StatesGroup):
    waiting_for_autor_response = State()


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]:
            return True

        else:
            return False

    except Exception as e:
        print(f"Ошибка проверки прав администратора: {e}")
        return False

@dp.message(Command('whitelist'))
async def whiteupd(message: types.Message, bot: Bot):
    if message.from_user.id in ida:
        await bot.send_message(message.chat.id, wlupd)

@dp.message(Command('wlupd'))
async def wlup(message: types.Message, bot: Bot):
    if message.from_user.id in ida:
        try:
            s = message.text.split()[1].strip().lower()
            if s.startswith('*') and s.endswith('*'):
                with open('urlwhitelist.txt', 'a', encoding='utf-8') as f:
                    f.write(f'\n{s}')
                load_lists()  # Немедленно обновляем список в памяти
                await message.answer('Отлично, теперь обнови белый список командой /reload')
            else:
                await message.answer('Ссылка не похожа на маску, перепроверь и повтори попытку')
        except IndexError:
            await message.answer('Укажите маску: /wlupd *amediateka.ru*')
    else:
        await bot.send_message(message.chat.id, "Эта штучка не для тебя")

async def reload(message: types.Message, bot: Bot):
    load_lists()
    await bot.send_message(message.chat.id, 'Обновлено!')

@dp.message(Command('warn'))
async def warn_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id
        ap = message.from_user.username

        if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split(maxsplit=2)
                    if len(t)==3:
                        up = t[1]
                        pr = t[2]
                    else:
                        up = t[1]
                        pr = 'Причина не указана'
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_warn = await get_user_simple(up)
                    elif int(up):
                        user_to_warn = up
                else:
                    t = message.text.split( maxsplit=1)
                    pr = t[1]
                    user_to_warn = message.reply_to_message.from_user.id
                    up = message.reply_to_message.from_user.username
                try:
                    cursor.execute("SELECT warning FROM warnlist WHERE uid=" + str(user_to_warn))
                    wn = cursor.fetchone()
                    wn = wn[0] + 1
                    cursor.execute("UPDATE warnlist SET warning= " + str(wn) + " where uid=" + str(user_to_warn))
                    db.commit()
                except TypeError:
                    wn = 1
                    cursor.execute("INSERT OR IGNORE INTO warnlist (uid, warning) VALUES (?, ?)", (user_to_warn, wn))
                    db.commit()
                if wn == 3:
                    await bot.ban_chat_member(chat_id, user_to_warn)
                    await message.reply(
                        f"Пользователю @{up} вынесено предупреждение {wn}/3. \nAдминистратор: @{ap} \nПричина: {pr} \nДостигнут лимит предупреждений. Пользователь забанен")
                    await message.delete()
                else:
                    await message.reply(f"Пользователю @{up} вынесено предупреждение {wn}/3. \nAдминистратор: @{ap} \nПричина: {pr}")
                    await message.delete()
            except Exception as e:
                await message.reply("Не удалось выдать предуппреждение пользователю.")
                await message.delete()
        else:
            await message.delete()

@dp.message(Command('unwarn'))
async def warn_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id
        ap = message.from_user.username

        if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split(maxsplit=3)
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_warn = await get_user_simple(up)
                    elif int(up):
                        user_to_warn = up
                else:
                    t = message.text.split( maxsplit=1)
                    user_to_warn = message.reply_to_message.from_user.id
                    up = message.reply_to_message.from_user.username
                try:
                    cursor.execute("SELECT warning FROM warnlist WHERE uid=" + str(user_to_warn))
                    wn = cursor.fetchone()

                    if wn[0]>0:
                        wn = wn[0] - 1
                        cursor.execute("UPDATE warnlist SET warning= " + str(wn) + " where uid=" + str(user_to_warn))
                        db.commit()
                        await message.reply(
                            f"С пользователя @{up} снято одно предупреждение ({wn}/3). \nAдминистратор: @{ap}")
                    elif wn[0] == 0:
                        await message.reply(
                        f"У пользователя {up} нет предупреждений")
                except TypeError:
                    wn = 0
                    cursor.execute("INSERT OR IGNORE INTO warnlist (uid, warning) VALUES (?, ?)", (user_to_warn, wn))
                    db.commit()
                await message.delete()
            except Exception as e:
                await message.reply("Не удалось выполнить команду.")
                await message.delete()
        else:
            await message.delete()

@dp.message(Command('ping'))
async def ping(message: types.Message, bot: Bot):
    if on == 1:
        await message.reply('Понг')

@dp.message(Command('help'))
async def help(message: types.Message, bot: Bot):
    if message.chat.id in ida:
        await bot.send_message(message.chat.id, helpt)


@dp.message(Command('ban'))
async def ban_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

                try:
                    if not message.reply_to_message:
                        t = message.text.split()
                        up = t[1]
                        if up[0] == '@':
                            up = up.replace('@', '', 1)
                            user_to_ban = await get_user_simple(up)
                        elif int(up):
                            user_to_ban = up
                    else:
                        user_to_ban = message.reply_to_message.from_user.id
                    await bot.ban_chat_member(chat_id, user_to_ban)
                    await message.reply("Пользователь забанен.")
                    await message.delete()
                except Exception as e:
                    await message.reply("Не удалось забанить пользователя.")
                    await message.delete()
        else:
            await message.delete()


@dp.message(Command('rules'))
async def rule(message: types.Message, bot: Bot):
    if on == 1:
        await message.reply("Правила чата:\n"+tt)
        await message.delete()


@dp.message(Command('unban'))
async def unban_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split()
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_ban = await get_user_simple(up)
                    elif int(up):
                        user_to_ban = up
                else:
                    user_to_ban = message.reply_to_message.from_user.id
                await bot.unban_chat_member(chat_id, user_to_ban)
                await message.reply("Пользователь разабанен.")
                await message.delete()
            except Exception as e:
                await message.reply("Не удалось разабанить пользователя.")
                await message.delete()
        else:
            await message.delete()


@dp.message(Command('mute'))
async def mute_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not (await is_user_admin(bot, chat_id, user_id) or
                (message.sender_chat and message.sender_chat.type == "channel" and
                 message.sender_chat.id == -1001951614079)):
            await message.delete()
            return

        try:
            # Получаем ID пользователя для мута
            if not message.reply_to_message:
                t = message.text.split()
                if len(t) > 1:
                    up = t[1]
                    # Проверяем, является ли аргумент числовым ID
                    if up.isdigit():
                        user_to_mute = int(up)
                    elif up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_mute = await get_user_simple(up)
                    else:
                        # Пробуем преобразовать в число (на случай если это число без @)
                        try:
                            user_to_mute = int(up)
                        except ValueError:
                            await message.reply("Укажите @username пользователя или цифровой ID.")
                            await message.delete()
                            return
                else:
                    await message.reply("Ответьте на сообщение пользователя или укажите @username/ID.")
                    await message.delete()
                    return
            else:
                user_to_mute = message.reply_to_message.from_user.id

            # Проверяем, не является ли пользователь администратором
            target_status = (await bot.get_chat_member(chat_id, user_to_mute)).status
            if target_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                await message.reply("Невозможно замутить администратора.")
                await message.delete()
                return

            # Парсим аргументы для времени
            args = message.text.split()
            duration = 100000000000000000  # Значение для вечного мута
            time_unit = 'min'  # По умолчанию минуты

            # Определяем индекс аргумента с временем
            time_arg_index = 2 if not message.reply_to_message else 1

            if len(args) > time_arg_index:
                time_arg = args[time_arg_index]

                # Регулярное выражение для поиска числа и единицы времени
                # Поддерживает: 10мин, 10мин, 5h, 3hour, 2d, 7day и т.д.
                pattern = r'^(\d+)(min|m|мин|минут|h|hour|ч|час|часов|d|day|д|день|дней)?$'
                match = re.match(pattern, time_arg.lower())

                if match:
                    duration = int(match.group(1))
                    if match.group(2):  # Если единица времени указана в том же аргументе
                        unit = match.group(2)
                        if unit in ['min', 'm', 'мин', 'минут']:
                            time_unit = 'min'
                        elif unit in ['h', 'hour', 'ч', 'час', 'часов']:
                            time_unit = 'h'
                        elif unit in ['d', 'day', 'д', 'день', 'дней']:
                            time_unit = 'd'
                    elif len(args) > time_arg_index + 1:  # Если единица времени отдельным аргументом
                        next_arg = args[time_arg_index + 1].lower()
                        if next_arg in ['min', 'm', 'мин', 'минут']:
                            time_unit = 'min'
                        elif next_arg in ['h', 'hour', 'ч', 'час', 'часов']:
                            time_unit = 'h'
                        elif next_arg in ['d', 'day', 'д', 'день', 'дней']:
                            time_unit = 'd'
                else:
                    # Если не удалось распарсить, пробуем как число
                    try:
                        duration = int(time_arg)
                        if len(args) > time_arg_index + 1:
                            next_arg = args[time_arg_index + 1].lower()
                            if next_arg in ['min', 'm', 'мин', 'минут']:
                                time_unit = 'min'
                            elif next_arg in ['h', 'hour', 'ч', 'час', 'часов']:
                                time_unit = 'h'
                            elif next_arg in ['d', 'day', 'д', 'день', 'дней']:
                                time_unit = 'd'
                    except ValueError:
                        pass  # Оставляем вечный мут

            # Вычисляем время мута
            if duration == 100000000000000000:
                until_date = None  # Навсегда
                time_text = "навсегда"
            else:
                if time_unit == 'min':
                    until_date = time.time() + duration * 60
                    time_text = f"{duration} минут"
                elif time_unit == 'h':
                    until_date = time.time() + duration * 3600
                    time_text = f"{duration} часов"
                elif time_unit == 'd':
                    until_date = time.time() + duration * 86400
                    time_text = f"{duration} дней"
                else:
                    until_date = time.time() + duration * 60
                    time_text = f"{duration} минут"

            # Применяем мут
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )

            if until_date:
                await bot.restrict_chat_member(chat_id, user_to_mute, permissions, until_date=until_date)
            else:
                await bot.restrict_chat_member(chat_id, user_to_mute, permissions)

            # Формируем ответ
            target_user = await bot.get_chat_member(chat_id, user_to_mute)
            user_name = f"@{target_user.user.username}"
            if duration == 100000000000000000:
                await message.reply(f"Пользователь {user_name} ({target_user.user.id}) замучен навсегда.")
                await message.delete()
            else:
                await message.reply(f"Пользователь {user_name} ({target_user.user.id}) замучен на {time_text}.")
                await message.delete()

            await message.delete()

        except Exception as e:
            print(f"Mute error: {e}")
            await message.reply("Не удалось замутить пользователя.")
            await message.delete()


@dp.message(Command('unmute'))
async def unmute_user(message: types.Message, bot: Bot):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not (await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
            await message.delete()
            return

        try:
            if not message.reply_to_message:
                t = message.text.split()
                if len(t) > 1:
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_unmute = await get_user_simple(up)
                    elif int(up):
                        user_to_unmute = up
                    else:
                        await message.reply("Укажите @username или id пользователя.")
                        await message.delete()
                        return
                else:
                    await message.reply("Ответьте на сообщение пользователя или укажите @username (или id).")
                    await message.delete()
                    return
            else:
                user_to_unmute = message.reply_to_message.from_user.id

            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )

            await bot.restrict_chat_member(chat_id, user_to_unmute, permissions)


            # Получаем информацию о пользователе для ответа
            target_user = await bot.get_chat_member(chat_id, user_to_unmute)
            if target_user.user.username:
                user_name = f" (@{target_user.user.username})"
            else: user_name = target_user.user.first_name

            await message.reply(f"Пользователь {user_name} {target_user.user.id} размучен.")
            await message.delete()
        except Exception as e:
            print(f"Unmute error: {e}")
            await message.reply("Не удалось размутить пользователя.")
            await message.delete()

@dp.message(Command('report'))
async def rep(message:types.Message, bot: Bot):
    if on == 1:
        global opid, nid, rmessage_id, rchat_id, opun, nun
        if message.reply_to_message:
            print(message.chat.id)
            rchat_id = message.chat.id
            rmessage_id = message.reply_to_message.message_id
            opid = message.from_user.id
            opnm = message.from_user.full_name
            opun = message.from_user.username
            nid = message.reply_to_message.from_user.id
            nnm = message.reply_to_message.from_user.full_name
            nun = message.reply_to_message.from_user.username
            tm = message.reply_to_message.text
            kom = message.text.split(maxsplit=1)
            if len(kom)==2:
                komment = kom[1]
            else:
                komment = "Комментарий не дан"
            await message.reply('Спасибо за жалобу на сообщение! Отправлено уведомление админам')
            await message.delete()
            tomsgid = [1758430459, 1042704010, 1132619666,  157398547, 1722862662, 1329032674]
            for i in tomsgid:
                await bot.send_message(i, f'В чате обнаружено подозрительное <a href="https://t.me/c/1398602500/{rmessage_id}">сообщение</a>!\n \n \n \n'
                                                    f'{opnm} @{opun} пожаловался на {nnm} @{nun}\n \n \n \nТекст сообщения: {tm} \n \n'
                                                    f'Комментарий сообщившего: {komment} \n \n'
                                                    f'<a href="https://t.me/c/1398602500/{rmessage_id}">Перейти к сообщению</a>', parse_mode="HTML",
                                                    disable_web_page_preview=True, reply_markup=g.as_markup())

        else:
            await message.reply('Используй это в ответ на сообщение')
            await message.delete()

@dp.message(Command('update'))
async def update(message:types.Message, bot: Bot):
    texts = message.text.split(maxsplit=1)
    text = texts[1]
    for i in ida:
        await bot.send_message(i, f'Обновление функционала: \n Что нового? \n {text}')

@dp.message(Command('debug'))
async def debug_command(message: types.Message, state: FSMContext, bot: Bot):
    await message.answer('Введите Ваше обращение к какому-то прогеру')
    await state.set_state(DebugState.waiting_for_debug_message)


@dp.message(DebugState.waiting_for_debug_message)
async def debug_new(message: types.Message, state: FSMContext, bot: Bot):
    await bot.forward_message(TO_CHAT_ID, message.chat.id, message.message_id)
    await message.answer('Ваше обращение принято')
    await state.clear()


@dp.message(Command('autor'))
async def autor_command(message: types.Message, state: FSMContext, bot: Bot):
    if message.chat.id == TO_CHAT_ID:
        await message.answer('Введи ответ')
        await state.set_state(AutorState.waiting_for_autor_response)
    else:
        await message.answer('Эта штучка не для тебя.')


@dp.message(AutorState.waiting_for_autor_response)
async def autor_response(message: types.Message, state: FSMContext, bot: Bot):
    await bot.send_message(get_chat_id, message.text)
    await message.answer('Отправлено')
    await state.clear()


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_joined_html_mention(event: ChatMemberUpdated, bot: Bot):
    global nuid, nuf
    if on == 1:
        user = event.new_chat_member.user
        chat = event.chat
        nuid = user.id
        nuf = user.full_name

        # Пропускаем ботов
        if user.is_bot:
            return

        # Проверяем каждое слово в имени пользователя
        user_words = user.full_name.lower().split() if user.full_name else []

        # Проверяем наличие запрещенных слов
        for word in user_words:
            for banned_pattern in bwp:
                if fnmatch.fnmatch(word, banned_pattern):
                    print(f'True: найдено запрещенное слово "{banned_pattern}" в "{word}"')
                    try:
                        await bot.ban_chat_member(chat.id, user.id)
                        return
                    except Exception as e:
                        print(f"Ошибка бана: {e}")
                        return

        # Получаем текущие права пользователя (могут уже быть ограничения)
        try:
            chat_member = await bot.get_chat_member(chat.id, user.id)
            original_permissions = None

            # Проверяем тип пользователя для получения прав
            if chat_member.status == ChatMemberStatus.RESTRICTED:
                # Для ограниченного пользователя (в муте) используем соответствующие поля
                original_permissions = {
                    'can_send_messages': chat_member.can_send_messages,
                    'can_send_media_messages': chat_member.can_send_media_messages,
                    'can_send_polls': chat_member.can_send_polls,
                    'can_send_other_messages': chat_member.can_send_other_messages,
                    'can_add_web_page_previews': chat_member.can_add_web_page_previews,
                    'can_change_info': chat_member.can_change_info,
                    'can_invite_users': chat_member.can_invite_users,
                    'can_pin_messages': chat_member.can_pin_messages,
                    'until_date': chat_member.until_date  # Сохраняем дату окончания мута, если есть
                }
            elif chat_member.status == ChatMemberStatus.MEMBER:
                # Для обычного участника - полные права
                original_permissions = {
                    'can_send_messages': True,
                    'can_send_media_messages': True,
                    'can_send_polls': True,
                    'can_send_other_messages': True,
                    'can_add_web_page_previews': True,
                    'can_change_info': False,
                    'can_invite_users': True,
                    'can_pin_messages': False,
                    'until_date': None
                }
            # Для администраторов и создателей не применяем капчу
            elif chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return

        except Exception as e:
            print(f"Ошибка получения прав пользователя: {e}")
            # В случае ошибки устанавливаем стандартные права
            original_permissions = {
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': True,
                'can_send_other_messages': True,
                'can_add_web_page_previews': True,
                'can_change_info': False,
                'can_invite_users': True,
                'can_pin_messages': False,
                'until_date': None
            }

        # Устанавливаем временное ограничение на отправку сообщений для капчи
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )

        try:
            # Применяем ограничение для капчи
            await bot.restrict_chat_member(chat.id, user.id, permissions)
        except Exception as e:
            print(f"Ошибка ограничения пользователя: {e}")
            return

        user_mention = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
        welcome_text = (
                f"{user_mention}, Добро пожаловать в чат. Ознакомьтесь с правилами чата ниже:\n" + tt
        )

        captcha_message = await bot.send_message(
            chat.id,
            welcome_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=captcha.as_markup()
        )

        # Добавляем пользователя в список ожидания с сохраненными правами
        pending_users[user.id] = {
            'chat_id': chat.id,
            'join_time': asyncio.get_event_loop().time(),
            'captcha_message_id': captcha_message.message_id,
            'original_permissions': original_permissions  # Сохраняем исходные права
        }

        # Запускаем таймер на бан через 60 секунд
        asyncio.create_task(ban_user_if_no_captcha(bot, user.id, chat.id))


async def ban_user_if_no_captcha(bot: Bot, user_id: int, chat_id: int):
    global kbuc
    """Банит пользователя если он не прошел капчу за 60 секунд"""
    try:
        # Ждем 60 секунд
        await asyncio.sleep(60)

        # Проверяем, все еще ли пользователь в ожидании
        if user_id in pending_users:
            kbuc += 1
            print(f'Количество забаненных пользователей с момента последнего перезапуска: {kbuc}')
            try:
                # Баним пользователя
                await bot.ban_chat_member(chat_id, user_id)
            except Exception as e:
                print(f"Ошибка бана за неактивность: {e}")

            # Удаляем пользователя из списка ожидания
            if user_id in pending_users:
                # Пытаемся удалить сообщение с капчей
                try:
                    captcha_message_id = pending_users[user_id]['captcha_message_id']
                    await bot.delete_message(chat_id, captcha_message_id)
                except:
                    pass

                del pending_users[user_id]

    except asyncio.CancelledError:
        # Таймер был отменен (пользователь прошел капчу)
        pass


async def handle_captcha_success(bot: Bot, user_id: int, chat_id: int):
    """Обрабатывает успешное прохождение капчи"""
    if user_id in pending_users:
        # Получаем сохраненные исходные права пользователя
        original_permissions = pending_users[user_id].get('original_permissions')

        if original_permissions:
            # Восстанавливаем исходные права пользователя (с сохранением мута)
            permissions = ChatPermissions(
                can_send_messages=original_permissions['can_send_messages'],
                can_send_media_messages=original_permissions['can_send_media_messages'],
                can_send_polls=original_permissions['can_send_polls'],
                can_send_other_messages=original_permissions['can_send_other_messages'],
                can_add_web_page_previews=original_permissions['can_add_web_page_previews'],
                can_change_info=original_permissions['can_change_info'],
                can_invite_users=original_permissions['can_invite_users'],
                can_pin_messages=original_permissions['can_pin_messages']
            )

            # Если был мут с определенной датой окончания, восстанавливаем его
            until_date = original_permissions.get('until_date')

            try:
                if until_date:
                    # Восстанавливаем мут с оригинальной датой окончания
                    await bot.restrict_chat_member(chat_id, user_id, permissions, until_date=until_date)
                else:
                    # Восстанавливаем права без мута
                    await bot.restrict_chat_member(chat_id, user_id, permissions)
            except Exception as e:
                print(f"Ошибка восстановления прав: {e}")
        else:
            # Если не удалось получить исходные права, устанавливаем стандартные
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )

            try:
                await bot.restrict_chat_member(chat_id, user_id, permissions)
            except Exception as e:
                print(f"Ошибка восстановления стандартных прав: {e}")

        # Удаляем сообщение с капчей
        try:
            captcha_message_id = pending_users[user_id]['captcha_message_id']
            await bot.delete_message(chat_id, captcha_message_id)
        except Exception as e:
            print(f"Ошибка удаления сообщения капчи: {e}")

        # Удаляем пользователя из списка ожидания
        del pending_users[user_id]


processed_groups = set()


@dp.message(F.content_type.in_([
    ContentType.TEXT,
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.AUDIO,
    ContentType.VOICE,
    ContentType.VIDEO_NOTE,
    ContentType.DOCUMENT
]))
async def bw(message: types.Message, bot: Bot):
    global soo, kbuc, found_bad_word
    found_bad_word = False
    if on == 1:
        if message.from_user.id == 777000:
            # Для групп медиа проверяем, не обрабатывали ли мы уже эту группу
            if message.media_group_id:
                if message.media_group_id not in processed_groups:
                    processed_groups.add(message.media_group_id)
                    await message.reply("В комментариях действуют следующие правила:\n" + tt)
            else:
                # Одиночное сообщение
                await message.reply("В комментариях действуют следующие правила:\n" + tt)

            return

        chat_id = message.chat.id
        user_id = message.from_user.id
        # Проверяем права администратора
        if await is_user_admin(bot, chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id in ALLOWED_CHANNELS):
            return
        if message.sender_chat and message.sender_chat.type == "channel":
                channel_id = message.sender_chat.id
                channel_title = message.sender_chat.title

                # Проверяем, разрешен ли каналwarn

                if channel_id not in ALLOWED_CHANNELS:
                    try:
                        # Баним канал (ограничиваем отправку сообщений)
                        await bot.ban_chat_sender_chat(
                            chat_id=message.chat.id,
                            sender_chat_id=channel_id
                        )

                        # Удаляем сообщение канала
                        await message.delete()
                    except Exception as e:
                        print(f"Ошибка блокировки канала {channel_title}: {e}")
                        # Пытаемся хотя бы удалить сообщение
                        try:
                            await message.delete()
                        except:
                            pass
        # Проверяем наличие запрещенных слов
        found_ban_word = False
        if message.text:
            clean_text = remove_punctuation(message.text)
            soo = clean_text.split()
        else:
            if message.caption != None:
                clean_text = remove_punctuation(message.caption)
                soo = clean_text.split()
            else:
                soo = "None"

        for word in soo:
            for pattern in banwordlist:
                if fnmatch.fnmatch(word.lower(), pattern):  # Проверяем в нижнем регистре
                    found_ban_word = True
                    break  # Прерываем внутренний цикл
            if found_ban_word:
                break  # Прерываем внешний цикл

        if found_ban_word and not (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001628633023):
            try:
                up = message.from_user.username or message.from_user.first_name

                # Работа с базой данных
                cursor.execute("SELECT warning FROM warnlist WHERE uid=?", (user_id,))
                result = cursor.fetchone()

                if result:
                    wn = result[0] + 1
                    cursor.execute("UPDATE warnlist SET warning=? WHERE uid=?", (wn, user_id))
                else:
                    wn = 1
                    cursor.execute("INSERT INTO warnlist (uid, warning) VALUES (?, ?)", (user_id, wn))

                db.commit()

                if wn >= 3:
                    await bot.ban_chat_member(chat_id, user_id)
                    await message.reply(
                        f"Пользователю @{up} вынесено предупреждение {wn}/3.\n"
                        f"Сообщение содержит запрещенные слова!\n"
                        f"Достигнут лимит предупреждений. Пользователь забанен"
                    )
                else:
                    await message.reply(
                        f"Пользователю @{up} вынесено предупреждение {wn}/3.\n"
                        f"Сообщение содержит запрещенные слова!"
                    )

                await message.delete()

            except Exception as e:
                print(f"Ошибка: {e}")
                await message.reply("Не удалось выдать предупреждение пользователю.")

        if found_ban_word == False:
            found_bad_word = False
            for i in range(len(soo) - 3):
                frase = f'{soo[i]}{soo[i + 1]}{soo[i + 2]}{soo[i + 3]}'
                for fr in bf:
                    if fnmatch.fnmatch(frase.lower(), fr):  # Проверяем в нижнем регистре
                        found_bad_word = True
                        break  # Прерываем внутренний цикл
                    if found_bad_word:
                        break  # Прерываем внешний цикл

        if found_bad_word and not (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001628633023):
                await bot.ban_chat_member(message.chat.id, message.from_user.id)
                kbuc+=1
                print(f'Количество забаненных пользователь с момента последнего перезапуска: {kbuc}')
                await message.delete()





        extracted_links = []

        # Проверяем текст сообщения
        if message.text and message.entities:
            for entity in message.entities:
                if entity.type == "url":
                    link = message.text[entity.offset:entity.offset + entity.length].lower()
                    extracted_links.append(link)
                elif entity.type == "text_link":
                    extracted_links.append(entity.url.lower())

        # Проверяем подпись к медиафайлам
        if message.caption and message.caption_entities:
            for entity in message.caption_entities:
                if entity.type == "url":
                    link = message.caption[entity.offset:entity.offset + entity.length].lower()
                    extracted_links.append(link)
                elif entity.type == "text_link":
                    extracted_links.append(entity.url.lower())

        # Если ссылок нет - выходим
        if not extracted_links:
            return

        # Убираем дубликаты
        extracted_links = list(set(extracted_links))

        has_forbidden_links = False
        for link in extracted_links:
            link_allowed = False

            for mask in wlu:
                if fnmatch.fnmatch(link, mask.lower()):
                    link_allowed = True
                    print(f"Ссылка разрешена: {link} по маске {mask}")
                    break

            if not link_allowed:
                has_forbidden_links = True
                print(f"Запрещенная ссылка: {link}")
                break

        if has_forbidden_links:
            chat_id = message.chat.id
            user_id = message.from_user.id

            if on ==1:
                try:
                    up = message.from_user.username or message.from_user.first_name
                    cursor.execute("SELECT warning FROM warnlist WHERE uid=?", (user_id,))
                    result = cursor.fetchone()

                    if result:
                        wn = result[0] + 1
                        cursor.execute("UPDATE warnlist SET warning=? WHERE uid=?", (wn, user_id))
                    else:
                        wn = 1
                        cursor.execute("INSERT INTO warnlist (uid, warning) VALUES (?, ?)", (user_id, wn))

                    db.commit()

                    if wn >= 3:
                        await bot.ban_chat_member(chat_id, user_id)
                        await message.reply(
                            f"Пользователю @{up} вынесено предупреждение {wn}/3. \n"
                            f"Ваше сообщение содержит запрещенные ссылки!\n"
                            f"Достигнут лимит предупреждений. Пользователь забанен"
                        )
                    else:
                        await message.reply(
                            f"Пользователю @{up} вынесено предупреждение {wn}/3. \n"
                            f"Ваше сообщение содержит запрещенные ссылки!"
                        )

                    await message.delete()

                except Exception as e:
                    print(f"Database error: {e}")
                    await message.reply("Не удалось выдать предупреждение пользователю.")

# ========== ДОБАВЛЕННЫЙ ЗАПУСК С ПЕРЕБОРОМ ПРОКСИ ==========


warnings.filterwarnings("ignore", category=ResourceWarning)

# --- 2. Настраиваем логирование для шумных библиотек
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

# --- 3. Главное: подменяем обработчик исключений цикла событий
# Эта функция будет игнорировать только сообщения, содержащие "Unclosed connection"
def _silence_aiohttp_warnings(loop, context):
    # Если сообщение содержит "Unclosed connection" — просто игнорируем его
    if 'Unclosed connection' in context.get('message', ''):
        return
    # В противном случае передаём управление стандартному обработчику
    loop.default_exception_handler(context)

# Получаем текущий цикл событий и устанавливаем наш обработчик
loop = asyncio.get_event_loop()
loop.set_exception_handler(_silence_aiohttp_warnings)
class CustomAiohttpSession(AiohttpSession):
    async def create_session(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self._connector = aiohttp.TCPConnector(ssl=ssl_context)
        self._session = aiohttp.ClientSession(connector=self._connector)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()
        await super().close()


async def run_bot_with_proxy(proxy_url: str):
    """
    Запускает бота с указанным прокси.
    Любая ошибка (сетевая, таймаут, SSL и т.д.) приводит к выбросу исключения,
    чтобы main переключился на следующий прокси.
    """
    # Проверка формата прокси
    if not proxy_url or '://' not in proxy_url:
        raise ValueError(f"Некорректный формат прокси: {proxy_url}")
    if proxy_url.count('/') > 2 and proxy_url.startswith('socks5:///'):
        raise ValueError(f"Прокси содержит пустой хост: {proxy_url}")

    # Создаём кастомную сессию с отключённой проверкой SSL (ваш класс)
    session = CustomAiohttpSession(proxy=proxy_url)
    bot = Bot(token=TOKEN, session=session)

    try:
        print(f"🚀 Запуск бота с прокси: {proxy_url}")
        await dp.start_polling(bot)
    except (TelegramNetworkError, aiohttp.ClientError, asyncio.TimeoutError, OSError, ConnectionError) as e:
        # Сетевые ошибки – переключаем прокси
        raise RuntimeError(f"Сетевая ошибка: {type(e).__name__}: {e}") from e
    except Exception as e:
        # Любая другая ошибка – тоже переключаем прокси
        print(f"❗ Неожиданная ошибка при работе с прокси {proxy_url}: {e}")
        raise RuntimeError(f"Неожиданная ошибка: {e}") from e
    finally:
        # Закрываем сессии, даже если была ошибка
        await bot.session.close()
        await session.close()
        await asyncio.sleep(0.1)


async def main():
    """
    Бесконечный перебор прокси. При любой ошибке переходит к следующему прокси.
    Остановка только по Ctrl+C.
    """
    print("📥 Загружаем список прокси...")
    proxies = await fetch_proxy_list()  # ваша функция получения прокси
    if not proxies:
        print("⚠️ Не удалось загрузить прокси, используем резервный список.")
        proxies = ["socks5://109.120.191.248:1080"]

    print(f"✅ Загружено {len(proxies)} прокси. Начинаем бесконечный перебор...")

    index = 0
    while True:
        proxy = proxies[index % len(proxies)]
        index += 1
        print(f"\n🔄 Попытка #{index} с прокси: {proxy}")

        try:
            await run_bot_with_proxy(proxy)
            # Если дошли сюда – бот завершился без ошибок (например, нажали Ctrl+C внутри run_bot_with_proxy)
            print("✅ Бот штатно завершил работу. Выходим.")
            break
        except RuntimeError as e:
            # Прокси не сработал – переходим к следующему
            print(f"⚠️ Прокси {proxy} не работает: {e}")
            await asyncio.sleep(1)   # пауза перед следующей попыткой
        except KeyboardInterrupt:
            # Пользователь нажал Ctrl+C во время работы main
            print("👋 Бот остановлен пользователем.")
            break
        except Exception as e:
            # На всякий случай перехватываем всё, что не учли
            print(f"❌ Критическая ошибка: {e}. Продолжаем перебор...")
            await asyncio.sleep(2)

    print("🛑 Бот завершил работу.")
if __name__ == "__main__":
    asyncio.run(main())