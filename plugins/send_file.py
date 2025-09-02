import asyncio
from configs import Config
from pyrogram import Client
from pyrogram.errors import FloodWait


async def media_forward(bot: Client, user_id: int, file_id: int):

    try:
        return await bot.copy_message(chat_id=user_id, from_chat_id=Config.DB_CHANNEL,
                                      message_id=file_id)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return media_forward(bot, user_id, file_id)


async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    await media_forward(bot, user_id, file_id)
    await asyncio.sleep(1)
