import asyncio
import time
import sqlite3
import fnmatch
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import ChatPermissions, ChatMemberUpdated, ContentType
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from uidtsb import get_user_simple

ALLOWED_CHANNELS = [-1001620433786, -1001372687943, -1001536772735, -1001667805833,
                    -1002345911986, -1001768096856, -1001640821962, -1001564386161,
                    -1001925689412, -1001682049112, -1001360911185, -1001683532449,
                    -1001628633023, -1001663074595, -1001573970133, -1001637258570,
                    -1001654742345, -1001951614079]

ida=[1758430459, 1042704010, 1132619666, 1329032674, 157398547, 1722862662]

TOKEN = "5840636568:AAE5ieurhmd0HW2FY-KTd5cpA4flRnCuhmI"
TO_CHAT_ID = 1758430459
get_chat_id = -1002308587530

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = sqlite3.connect('sb.db')
cursor = db.cursor()

helpt = ('Функционал:\n'
        '/warn - выдает предупреждение пользователю, при достижении 3 предупреждений пользователь будет заблокирован. Работает как ответом на сообщение, так и через "собачку".'
        'Необходимо указать причину\n\n'
        '/unwarn - снимает с пользователя одно предупреждение, аналогично работает и по ответу, и по упоминанию.\n\n'
        '/ban - блокирует пользователя в чате. Работает по ответу на сообщение или по упоминанию.\n\n'
        '/unban - убирает пользователя из черного списка.\n\n'
        '/mute - накладывает на пользователя запрет на отправку сообщений. Синтаксис следующий:\n\n'
        '/mute @Vvvvvvvvv222221 1 d/h/m\n'
        'Можно использовать и через ответ на сообщение, тогда упоминание не нужно писать. Если не указать время то пользователь будет ограничен навсегда.\n\n'
        '/unmute - возвращает пользователю право отправлять сообщения. Работает по ответу или через «собачку».\n\n'
        '/rules - отправляет в чат сообщение с правилами.\n\n'
        '/report - отправляет в личные сообщения адептам сообщение о жалобе и само сообщение, на которое пожаловались.\n\n'
        '/debag - отправляет создателю сообщение об ошибке, если таковая есть.\n\n'
        '/chatoff - выключает чат.\n\n'
        '/chaton - включает чат.\n\n'
        '/off - команда для отключения бота.\n\n'
        '/on - команда для включения бота.\n\n'
        '/help - показать это сообщение(только в личке с ботом\n\n'
        '/ping - команда для проверки пингования.\n\n\n\n'
        'Автоматически удаляет команды от тех пользователей, которые не являются администраторами, а также сразу удаляет команды (через /) от сами админов одновременно с выполнением команды.\n'
        'Не требует списка администраторов - реагирует на команды от тех, кто имеет «звание» (он же префикс).\n\n'
        'Умеет банить те ссылки, которых нет в «белом списке».\n\n'
        'Имеет «белый список», включающий в себя каналы, от лица которых пишут Бандиты, и ссылки с ресурсами.\n\n'
        'Так же в бота встроена функции отправки правил под новые посты в тг канале.\n\n'
        'Фильтр мата\n\n'
        'Фильтр ссылок\n\n'
        'Приветствие новых пользователей\n\n')


tt = (
    "1) будь вежлив к другим участникам и не нарушай атмосферу чата; \n2) реклама чего угодно (ссылки) запрещена;\n"
    "3) спам, политика, религия, агрессия не приветствуются;\n"
    "4) мат запрещён! бот не пощадит;\n"
    "5) отправляйте не более двух стикеров подряд;\n"
    "6) будьте котиками;\n"
    "7) за контент сексуального характера или же который может быть неприятным для участников чата, а так же за спойлеры выдаётся предупреждение.\n"
    "Чтобы не получать их за спойлеры лучше использовать функцию скрытия сообщения (в начале и в конце предложения ставить ||).\n"
    "8) Этот чат - свободная зона от Геншина/Бравл Старса.\n"
    "9) Смотрите аниме где угодно, но в чат не кидайте ссылки/названия сторонних проектов.\n"
    "10) Не кидайте свои озвучки. Ждите конкурсы.\n"
    "11) Язык чата - русский")


file = open('banwords.txt', 'r', encoding='utf-8')
banwordlist = []
for i in file:
    banwordlist.append(i.replace('\n', '', 1))
file.close()
f = open('urlwhitelist.txt', 'r')
wlu = []
for i in f:
    wlu.append(i.replace('\n', '', 1))
f.close()
l = open('banwordsprof.txt', 'r', encoding='utf-8')
bwp =[]
for i in l:
    bwp.append(i.replace('\n', '', 1))
l.close()

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

@dp.message(Command('off'))
async def vkl(message: types.Message):
    global on
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):
        on = 0
        await message.reply('Бот выключен, чтобы включить введите команду /on')
        await message.delete()
    else:
        await message.reply('Эта штучка для админа')

@dp.message(Command('on'))
async def vkl(message: types.Message):
    global on
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):
        on = 1
        await message.reply('Бот включен, чтобы выключить введите команду /off')
        await message.delete()
    else:
        await message.delete()


async def open_chat_full_permissions(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
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


async def close_chat_no_permissions(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
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
async def handle_chaton(message: types.Message):
    await open_chat_full_permissions(message)

@dp.message(Command("chatoff"))
async def handle_chatoff(message: types.Message):
    await close_chat_no_permissions(message)

@dp.callback_query(lambda i: i.data in ['mn', 'mo', 'bn', 'bo', 'dd', 'sk', "cpt"])
async def rep(callback: types.CallbackQuery):
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
        if callback.from_user.id == nuid:
            chatid = callback.message.chat.id
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await bot.restrict_chat_member(chatid, callback.from_user.id, permissions)
            await callback.answer(
                "Отлично! Вы человек, приятного общения",
                show_alert=True )
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await callback.answer(
                f"⚠️ Внимание!\n\nЭто сообщение для {nuf}",
                show_alert=True)




class DebugState(StatesGroup):
    waiting_for_debug_message = State()


class AutorState(StatesGroup):
    waiting_for_autor_response = State()


async def is_user_admin(chat_id: int, user_id: int) -> bool:
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

@dp.message(Command('warn'))
async def warn_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id
        ap = message.from_user.username

        if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split(maxsplit=2)
                    up = t[1]
                    pr = t[2]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_warn = await get_user_simple(up)
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
async def warn_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id
        ap = message.from_user.username

        if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split(maxsplit=3)
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_warn = await get_user_simple(up)
                else:
                    t = message.text.split( maxsplit=1)
                    user_to_warn = message.reply_to_message.from_user.id
                    up = message.reply_to_message.from_user.username
                try:
                    cursor.execute("SELECT warning FROM warnlist WHERE uid=" + str(user_to_warn))
                    wn = cursor.fetchone()

                    if wn>0:
                        cursor.execute("UPDATE warnlist SET warning= " + str(wn) + " where uid=" + str(user_to_warn))
                        db.commit()
                        wn = wn[0] - 1
                except TypeError:
                    wn = 0
                    cursor.execute("INSERT OR IGNORE INTO warnlist (uid, warning) VALUES (?, ?)", (user_to_warn, wn))
                    db.commit()
                if wn == 0:
                    await bot.ban_chat_member(chat_id, user_to_warn)
                    await message.reply(
                        f"У пользователя {up} нет предупреждений")
                    await message.delete()
                else:
                    await message.reply(f"С пользователя @{up} снято одно предупреждение ({wn}/3). \nAдминистратор: @{ap}")
                    await message.delete()
            except Exception as e:
                await message.reply("Не удалось выполнить команду.")
                await message.delete()
        else:
            await message.delete()

@dp.message(Command('ping'))
async def ping(message: types.Message):
    if on == 1:
        await message.reply('Понг')

@dp.message(Command('help'))
async def help(message: types.Message):
    if message.chat.id in ida:
        await bot.send_message(message.chat.id, helpt)


@dp.message(Command('ban'))
async def ban_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

                try:
                    if not message.reply_to_message:
                        t = message.text.split()
                        up = t[1]
                        if up[0] == '@':
                            up = up.replace('@', '', 1)
                            user_to_ban = await get_user_simple(up)
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
async def rule(message: types.Message):
    if on == 1:
        await message.reply("Правила чата:\n"+tt)
        await message.delete()


@dp.message(Command('unban'))
async def unban_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079):

            try:
                if not message.reply_to_message:
                    t = message.text.split()
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_ban = await get_user_simple(up)
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
async def mute_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not (await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
            await message.delete()
            return

        try:
            if not message.reply_to_message:
                t = message.text.split()
                if len(t) > 1:
                    up = t[1]
                    if up[0] == '@':
                        up = up.replace('@', '', 1)
                        user_to_mute = await get_user_simple(up)
                    else:
                        await message.reply("Укажите @username пользователя.")
                        await message.delete()
                        return
                else:
                    await message.reply("Ответьте на сообщение пользователя или укажите @username.")
                    await message.delete()
                    return
            else:
                user_to_mute = message.reply_to_message.from_user.id
            target_status = (await bot.get_chat_member(chat_id, user_to_mute)).status
            if target_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                await message.reply("Невозможно замутить администратора.")
                await message.delete()
                return

            duration = 100000000000000000
            args = message.text.split()
            time_index = None
            for i, arg in enumerate(args):
                if arg.isdigit() and i > 0:
                    try:
                        duration = int(arg)
                        time_index = i
                        break
                    except ValueError:
                        pass


            time_unit = 'min'
            if time_index and time_index + 1 < len(args):
                next_arg = args[time_index + 1].lower()
                if next_arg in ['min', 'm', 'мин', 'минут']:
                    time_unit = 'min'
                elif next_arg in ['h', 'hour', 'ч', 'час', 'часов']:
                    time_unit = 'h'
                elif next_arg in ['d', 'day', 'д', 'день', 'дней']:
                    time_unit = 'd'

            # Вычисляем время мута
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

            permissions = ChatPermissions(can_send_messages=False)
            await bot.restrict_chat_member(chat_id, user_to_mute, permissions, until_date=until_date)

            target_user = await bot.get_chat_member(chat_id, user_to_mute)
            user_name = f" @{target_user.user.username}"
            if duration==100000000000000000:
                await message.reply(f"Пользователь {user_name} замучен навсегда.")
                await message.delete()
            else:
                await message.reply(f"Пользователь {user_name} замучен на {time_text}.")
                await message.delete()
        except Exception as e:
            print(f"Mute error: {e}")
            await message.reply("Не удалось замутить пользователя.")
            await message.delete()


@dp.message(Command('unmute'))
async def unmute_user(message: types.Message):
    if on == 1:
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not (await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001951614079)):
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
                    else:
                        await message.reply("Укажите @username пользователя.")
                        await message.delete()
                        return
                else:
                    await message.reply("Ответьте на сообщение пользователя или укажите @username.")
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
            user_name = target_user.user.first_name
            if target_user.user.last_name:
                user_name += f" {target_user.user.last_name}"
            if target_user.user.username:
                user_name += f" (@{target_user.user.username})"

            await message.reply(f"Пользователь {user_name} размучен.")
            await message.delete()
        except Exception as e:
            print(f"Unmute error: {e}")
            await message.reply("Не удалось размутить пользователя.")
            await message.delete()

@dp.message(Command('report'))
async def rep(message:types.Message):
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
            await message.reply('Спасибо за жалобу на сообщение! Отправлено уведомление админам')
            await message.delete()
            tomsgid = [1758430459, 1042704010, 1132619666,  157398547, 1722862662, 1329032674]
            for i in tomsgid:
                await bot.send_message(i, f'В чате обнаружено подозрительное <a href="https://t.me/c/1398602500/{rmessage_id}">сообщение</a>!\n \n \n \n'
                                                    f'{opnm} @{opun} пожаловался на {nnm} @{nun}\n \n \n \nТекст сообщения: {tm} \n'
                                                    f'<a href="https://t.me/c/1398602500/{rmessage_id}">Перейти к сообщению</a>', parse_mode="HTML",
                                                    disable_web_page_preview=True, reply_markup=g.as_markup())
###


        ###

        #
        else:
            await message.reply('Используй это в ответ на сообщение')
            await message.delete()



@dp.message(Command('debug'))
async def debug_command(message: types.Message, state: FSMContext):
    await message.answer('Введите Ваше обращение к какому-то прогеру')
    await state.set_state(DebugState.waiting_for_debug_message)


@dp.message(DebugState.waiting_for_debug_message)
async def debug_new(message: types.Message, state: FSMContext):
    await bot.forward_message(TO_CHAT_ID, message.chat.id, message.message_id)
    await message.answer('Ваше обращение принято')
    await state.clear()


@dp.message(Command('autor'))
async def autor_command(message: types.Message, state: FSMContext):
    if message.chat.id == TO_CHAT_ID:
        await message.answer('Введи ответ')
        await state.set_state(AutorState.waiting_for_autor_response)
    else:
        await message.answer('Эта штучка не для тебя.')


@dp.message(AutorState.waiting_for_autor_response)
async def autor_response(message: types.Message, state: FSMContext):
    await bot.send_message(get_chat_id, message.text)
    await message.answer('Отправлено')
    await state.clear()


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_joined_html_mention(event: ChatMemberUpdated):
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

        user_mention = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
        welcome_text = (
                f"{user_mention}, Добро пожаловать в чат. Ознакомьтесь с правилами чата ниже:\n" + tt
        )

        permissions = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat.id, user.id, permissions)

        await bot.send_message(
            chat.id,
            welcome_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=captcha.as_markup()
        )



@dp.message(lambda message: any(
    entity.type in ["url", "text_link"]
    for entity in message.entities or []
))
async def handle_entity_links(message: types.Message):
    if on == 1:
        extracted_links = []
        for entity in message.entities or []:
            if entity.type == "url":
                link = message.text[entity.offset:entity.offset + entity.length]
                extracted_links.append(link)
            elif entity.type == "text_link":
                extracted_links.append(entity.url)


        has_forbidden_links = False
        for link in extracted_links:
            link_allowed = False

            for mask in wlu:
                if fnmatch.fnmatch(link, mask):
                    link_allowed = True
                    break

            if not link_allowed:
                has_forbidden_links = True
                break

        if has_forbidden_links:
            chat_id = message.chat.id
            user_id = message.from_user.id

            if not await is_user_admin(chat_id, user_id):
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
async def bw(message: types.Message):
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
        if await is_user_admin(chat_id, user_id) or (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id in ALLOWED_CHANNELS):
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
        found_bad_word = False
        soo = message.text.split()

        for word in soo:
            for pattern in banwordlist:
                if fnmatch.fnmatch(word.lower(), pattern):  # Проверяем в нижнем регистре
                    found_bad_word = True
                    break  # Прерываем внутренний цикл
            if found_bad_word:
                break  # Прерываем внешний цикл

        if found_bad_word and not (message.sender_chat and message.sender_chat.type == "channel" and message.sender_chat.id == -1001628633023):
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



async def main():
    await dp.start_polling(bot)
#


if __name__ == '__main__':
    asyncio.run(main())