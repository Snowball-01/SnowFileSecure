import asyncio
import humanize

from configs import Config
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from utility.helper import str_to_b64
from utility.database import db


# ─── Helpers ─────────────────────────────────────────
def user_info(user):
    """Format user details for logs"""
    return (
        f"👤 **User Info**\n"
        f"> **Name:** [{user.first_name}](tg://user?id={user.id})\n"
        f"> **User ID:** `{user.id}`"
    )


def action_buttons(share_link: str):
    """Buttons with file link + community links"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Open Link", url=share_link)],
        [
            InlineKeyboardButton("📢 Updates Channel",
                                 url="https://t.me/+HzGpLAZXTxoyYTNl"),
            InlineKeyboardButton(
                "💬 Support Group", url="https://t.me/+mCdsJ7mjeBEyZWQ1"),
        ]
    ])


# ─── Forward File to DB Channel ─────────────────────
async def forward_to_channel(bot: Client, message: Message, editable: Message):
    file = getattr(message, message.media.value)
    file_name = file.file_name
    file_size = humanize.naturalsize(file.file_size)

    # User custom caption
    c_caption = await db.get_caption(message.from_user.id)
    if c_caption:
        try:
            caption = c_caption.format(filename=file_name, filesize=file_size)
        except Exception:
            caption = f"**{file_name}**"
    else:
        caption = f"**{file_name}**"

    try:
        sent = await bot.copy_message(
            Config.DB_CHANNEL,
            message.from_user.id,
            message.id,
            caption=caption
        )
        return sent
    except FloodWait as e:
        if e.value > 45:
            await asyncio.sleep(e.value)
            await bot.send_message(
                Config.LOG_CHANNEL,
                f"⚠️ **FloodWait Alert**\n"
                f"> Wait: `{e.value}s`\n"
                f"> From User: `{editable.chat.id}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        "🚫 Ban User", callback_data=f"ban_user_{editable.chat.id}")]]
                )
            )
        return await forward_to_channel(bot, message, editable)


# ─── Save Batch Files ───────────────────────────────
async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list):
    try:
        message_ids_str, saved_count = "", 0
        user = editable.reply_to_message.from_user

        # Process all messages
        for msg in await bot.get_messages(chat_id=editable.chat.id, message_ids=message_ids):
            sent = await forward_to_channel(bot, msg, editable)
            if not sent:
                continue
            message_ids_str += f"{sent.id} "
            saved_count += 1
            await asyncio.sleep(2)  # avoid spam

        # Save reference message
        save_msg = await bot.send_message(
            Config.DB_CHANNEL,
            message_ids_str,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🗑️ Delete Batch", callback_data="closeMessage")]])
        )

        share_link = f"https://t.me/{Config.BOT_USERNAME}?start={Config.BOT_USERNAME}_{str_to_b64(str(save_msg.id))}"

        await editable.edit(
            "✅ **Batch Saved Successfully!**\n\n"
            f"> Total Files: `{saved_count}`\n"
            f"> Permanent Link: `{share_link}`",
            reply_markup=action_buttons(share_link),
            disable_web_page_preview=True
        )

        await bot.send_message(
            Config.LOG_CHANNEL,
            f"📦 **Batch Link Generated**\n\n{user_info(user)}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Open Link", url=share_link)]])
        )

    except Exception as err:
        await editable.edit(f"❌ **Batch Save Failed!**\n\n> Error: `{err}`")
        await bot.send_message(
            Config.LOG_CHANNEL,
            f"🚨 **Batch Save Error**\n\n"
            f"> From: `{editable.chat.id}`\n"
            f"> Error: `{err}`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "🚫 Ban User", callback_data=f"ban_user_{editable.chat.id}")]]
            )
        )


# ─── Save Single File ───────────────────────────────
async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        file = getattr(message, message.media.value)
        file_name = file.file_name
        file_size = humanize.naturalsize(file.file_size)
        user = editable.reply_to_message.from_user

        # Caption handling
        c_caption = await db.get_caption(message.from_user.id)
        if c_caption:
            try:
                caption = c_caption.format(
                    filename=file_name, filesize=file_size)
            except Exception:
                caption = f"**{file_name}**"
        else:
            caption = f"**{file_name}**"

        # Save file in DB
        forwarded = await bot.copy_message(
            Config.DB_CHANNEL,
            message.from_user.id,
            message.id,
            caption=caption
        )

        share_link = f"https://t.me/{Config.BOT_USERNAME}?start={Config.BOT_USERNAME}_{str_to_b64(str(forwarded.id))}"

        await editable.edit(
            "✅ **File Saved Successfully!**\n\n"
            f"> Permanent Link: `{share_link}`",
            reply_markup=action_buttons(share_link),
            disable_web_page_preview=True
        )

        await bot.send_message(
            Config.LOG_CHANNEL,
            f"📄 **File Link Generated**\n\n{user_info(user)}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Open Link", url=share_link)]])
        )

    except FloodWait as e:
        if e.value > 45:
            await asyncio.sleep(e.value)
            await bot.send_message(
                Config.LOG_CHANNEL,
                f"⚠️ **FloodWait Alert**\n"
                f"> Wait: `{e.value}s`\n"
                f"> From User: `{editable.chat.id}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        "🚫 Ban User", callback_data=f"ban_user_{editable.chat.id}")]]
                )
            )
        await save_media_in_channel(bot, editable, message)

    except Exception as err:
        await editable.edit(f"❌ **File Save Failed!**\n\n> Error: `{err}`")
        await bot.send_message(
            Config.LOG_CHANNEL,
            f"🚨 **File Save Error**\n\n"
            f"> From: `{editable.chat.id}`\n"
            f"> Error: `{err}`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "🚫 Ban User", callback_data=f"ban_user_{editable.chat.id}")]]
            )
        )
