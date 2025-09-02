import os
import re
import sys
import json
import base64
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified

from configs import Config
from utility.helper import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ─── Helpers ─────────────────────────────────────────
def get_user_info(user):
    return (
        f"👤 **User Info**\n"
        f"> **Name:** `{user.first_name}`\n"
        f"> **Link:** [{user.first_name}](tg://user?id={user.id})\n"
        f"> **User ID:** `{user.id}`"
    )


def share_btn(url: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗 Open Link", url=url),
                InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={url}")
            ]
        ]
    )


# ─── Single File Link ─────────────────────────────────
@Client.on_message(filters.command(["link", "plink"]))
async def gen_link_s(bot, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply(
            "⚠️ **Reply to a media message to get a shareable link.**"
        )

    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO,
                         enums.MessageMediaType.AUDIO,
                         enums.MessageMediaType.DOCUMENT]:
        return await message.reply(
            "❌ **Unsupported media type!**\n"
            "> Only Video, Audio & Document are allowed."
        )

    if message.has_protected_content and message.chat.id not in Config.ADMINS:
        return await message.reply("🚫 **This message is protected. Cannot generate link.**")

    # Encode file_id
    file_id, _ = unpack_new_file_id(getattr(replied, file_type.value).file_id)
    string = "filep_" if message.text.lower().startswith("/plink") else "file_"
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode()).decode().strip("=")
    share_link = f"https://t.me/{Config.BOT_USERNAME}?start={outstr}"

    # Send link to user
    await message.reply(
        f"✅ **Here is your link:**\n\n`{share_link}`",
        reply_markup=share_btn(share_link)
    )

    # Log to admin channel
    await bot.send_message(
        Config.LOG_CHANNEL,
        f"📌 **Sharable Link Generated**\n\n{get_user_info(message.from_user)}",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open Link", url=share_link)]])
    )


# ─── Batch Link ───────────────────────────────────────
@Client.on_message(filters.command(["batch", "pbatch"]))
async def gen_link_batch(bot, message: Message):
    if " " not in message.text:
        return await message.reply(
            "⚠️ **Invalid format!**\n\n"
            "> Usage: `/batch <first_msg_link> <last_msg_link>`\n"
            "Example:\n"
            "`/batch https://t.me/Channel/10 https://t.me/Channel/20`"
        )

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply(
            "⚠️ **Invalid format!**\n\n"
            "You must pass **2 links** (start & end)."
        )

    _, first, last = links
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    def parse_link(link):
        match = regex.match(link)
        if not match:
            return None, None
        chat_id, msg_id = match.group(4), int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
        return chat_id, msg_id

    f_chat_id, f_msg_id = parse_link(first)
    l_chat_id, l_msg_id = parse_link(last)

    if not f_chat_id or not l_chat_id:
        return await message.reply("❌ **Invalid Telegram link provided.**")

    if f_chat_id != l_chat_id:
        return await message.reply("⚠️ **Both links must belong to the same chat!**")

    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply("🚫 **This is a private channel/group.**\n> Make me an **Admin** to index files.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("❌ **Invalid link provided.**")
    except Exception as e:
        return await message.reply(f"❌ **Error:** `{e}`")

    sts = await message.reply("⏳ **Generating batch link...**\n> This may take some time.")

    FRMT = (
        "**⏳ Generating Link...**\n"
        "> 📦 Total: `{total}`\n"
        "> ✅ Done: `{current}`\n"
        "> ⏳ Remaining: `{rem}`\n"
        "> ⚡ Status: `{sts}`"
    )

    outlist, og_msg, tot = [], 0, 0

    try:
        async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
            tot += 1
            if msg.empty or msg.service or not msg.media:
                continue
            try:
                file_type = msg.media
                file = getattr(msg, file_type.value)
                caption = getattr(msg, "caption", "")
                if caption:
                    caption = caption.html
                if file:
                    outlist.append({
                        "file_id": file.file_id,
                        "caption": caption,
                        "title": getattr(file, "file_name", ""),
                        "size": file.file_size,
                        "protect":True if message.text.lower().startswith("/pbatch") else False,
                    })
                    og_msg += 1
            except Exception:
                continue

            if not og_msg % 20:
                try:
                    await sts.edit(
                        FRMT.format(
                            total=l_msg_id - f_msg_id,
                            current=tot,
                            rem=(l_msg_id - f_msg_id) - tot,
                            sts="Saving..."
                        )
                    )
                except Exception:
                    pass

        # Save batch file
        tmp_file = f"batch_{message.from_user.id}.json"
        with open(tmp_file, "w+") as out:
            json.dump(outlist, out)

        post = await bot.send_document(
            Config.LOG_CHANNEL,
            tmp_file,
            file_name="Batch.json",
            caption="⚠️ **Batch File Generated for FileStore.**"
        )
        os.remove(tmp_file)

        file_id, _ = unpack_new_file_id(post.document.file_id)
        share_link = f"https://t.me/{Config.BOT_USERNAME}?start=BATCH-{file_id}"

        await sts.edit(
            f"✅ **Batch Link Generated!**\n\n"
            f"> Contains `{og_msg}` files.\n\n"
            f"`{share_link}`",
            reply_markup=share_btn(share_link)
        )

        await bot.send_message(
            Config.LOG_CHANNEL,
            f"📌 **Batch Link Generated**\n\n{get_user_info(message.from_user)}",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open Link", url=share_link)]])
        )

    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        await sts.edit(f"❌ **Error:** `{e}`")
