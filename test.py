import asyncio
import time
import sqlite3
import fnmatch
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import ChatPermissions, ChatMemberUpdated, ContentType
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from uidtsb import get_user_simple
from constant import TOKEN, TO_CHAT_ID, ALLOWED_CHANNELS, ida, helpt, get_chat_id, tt
import re
from aiogram.utils.markdown import hlink

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = sqlite3.connect('sb.db')
cursor = db.cursor()
on=1

g = InlineKeyboardBuilder()
g.add(InlineKeyboardButton(text="Запретить писать нарушителю 1 час", callback_data="mn"))
g.add(InlineKeyboardButton(text="❗️Запретить писать отправителю 1 час", callback_data="mo"))
g.add(InlineKeyboardButton(text="Забанить нарушителя", callback_data="bn"))
g.add(InlineKeyboardButton(text="❗️Забанить отправителя", callback_data="bo"))
g.add(InlineKeyboardButton(text="Удалить сообщение", callback_data="dd"))
g.add(InlineKeyboardButton(text="Игнорировать", callback_data="sk"))
g.adjust(1)


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




@dp.message(Command('spam'))
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
            kom = message.text.split(maxsplit=1)
            if len(kom)==2:
                komment = kom[1]
            else:
                komment = "Комментарий не дан"
            await message.reply('Спасибо за жалобу на сообщение! Отправлено уведомление админам. Нарушитель ограничен.')
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
            until_date = time.time() +  3600
            if until_date:
                await bot.restrict_chat_member(rchat_id, nid, permissions, until_date=until_date)
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


async def main():
    await dp.start_polling(bot)


#


if __name__ == '__main__':
    asyncio.run(main())
