import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import ADMINS, TIME, MSG_ALRT, LOG_CHANNEL, PICS, SUPPORT_CHAT_ID
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
                InlineKeyboardButton('⚙ Lᴀᴛᴇꜱᴛ Mᴏᴠɪᴇ Rᴇʟᴇᴀꜱᴇꜱ ⚙', url=f'https://t.me/+uA5gEKm8WXk1ZTll')
               ],[
                InlineKeyboardButton('⚓️ Oᴛᴛ Iɴsᴛᴀɢʀᴀᴍ Cʜᴀɴɴᴇʟ ⚓️', url=f'https://www.instagram.com/new_ott__updates?igsh=enI5ZzIzcXkzd3Bl')
              ],[
                InlineKeyboardButton('🖥 Oᴛᴛ Uᴩᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ 🖥', url="https://t.me/MCUupdatesLINKS"),
        ]       
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [
                InlineKeyboardButton('⚙ Lᴀᴛᴇꜱᴛ Mᴏᴠɪᴇ Rᴇʟᴇᴀꜱᴇꜱ ⚙', url=f'https://t.me/+uA5gEKm8WXk1ZTll')
               ],[
                InlineKeyboardButton('⚓️ Oᴛᴛ Iɴsᴛᴀɢʀᴀᴍ Cʜᴀɴɴᴇʟ ⚓️', url=f'https://www.instagram.com/new_ott__updates?igsh=enI5ZzIzcXkzd3Bl')
              ],[
                InlineKeyboardButton('🖥 Oᴛᴛ Uᴩᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ 🖥', url="https://t.me/MCUupdatesLINKS"),
        ]       
        reply_markup = InlineKeyboardMarkup(buttons)      
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
                                              
@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer(MSG_ALRT)
    await message.message.edit('Succesfully Deleted All The Indexed Files.')
