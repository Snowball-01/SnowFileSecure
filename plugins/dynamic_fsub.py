from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChannelInvalid
from configs import Config
from utility.database import db


@Client.on_message(filters.private & filters.command("set_fsub") & filters.user(Config.ADMINS))
async def set_fsub(bot: Client, message: Message):
    """
    Set Force Subscribe channel/group ID
    Usage: /set_fsub -100xxxxxxxxxx
    """

    # No argument
    if len(message.command) == 1:
        return await message.reply_text(
            "> ❌ **Invalid Command!**\n\n"
            "> **Example:** `/set_fsub -1001234567890`"
        )

    chat_id = message.command[1]

    # Must start with -100
    if not chat_id.startswith("-100"):
        return await message.reply_text(
            "> ❌ **Invalid Chat ID!**\n\n"
            "> Chat ID must start with `-100`."
        )

    try:
        # Check if bot is admin
        member = await bot.get_chat_member(int(chat_id), bot.username)
    except ChannelInvalid:
        return await message.reply_text(
            "> ⚠️ **Error:** I am not an admin in this chat.\n\n"
            "> Please make sure I have **admin rights**."
        )

    if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await db.set_fsub(fsub_id=chat_id)
        return await message.reply_text(
            f"> ✅ **Force Subscribe set successfully!**\n\n"
            f"> Now users must join `{chat_id}`."
        )

    return await message.reply_text(
        "> ❌ **Failed to set Force Subscribe.**\n\n"
        "> Make sure I am an **admin** in the chat."
    )


@Client.on_message(filters.private & filters.command("del_fsub") & filters.user(Config.ADMINS))
async def del_fsub(bot: Client, message: Message):
    """
    Delete Force Subscribe setting
    """

    status = await message.reply_text("> ⏳ **Removing Force Subscribe...**")

    await db.set_fsub(fsub_id=None)

    await status.edit("> ✅ **Force Subscribe removed successfully!**")
