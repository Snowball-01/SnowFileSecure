import os
import sys
import json
import base64
import asyncio
import random
import logging
from binascii import Error

from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait, ChatAdminRequired

from configs import Config
from utility.database import db
from utility.helper import (
    get_file_details,
    get_size,
    b64_to_str,
    is_subscribed,
    add_user_to_database,
    force_sub
)
from .send_file import send_media_and_reply

logger = logging.getLogger(__name__)

BATCH_FILES = {}


@Client.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):
    if Config.DYNAMIC_FSUB:
        fsub = await db.get_fsub()
    else:
        fsub = Config.FORCE_SUB

    # Force Sub
    if len(cmd.command) == 1:
        if fsub and not await is_subscribed(bot, cmd, fsub):
            return await force_sub(bot, cmd, fsub)

    if fsub and not await is_subscribed(bot, cmd, fsub):
        try:
            invite_link = await bot.create_chat_invite_link(fsub)
        except ChatAdminRequired:
            logger.error("⚠️ Bot must be admin in the ForceSub channel.")
            return

        btn = [[InlineKeyboardButton(
            "📢 Join Our Channel", url=invite_link.invite_link)]]

        if cmd.command[1] != "subscribe":
            try:
                file_id = cmd.command[1]
                pre = 'checksub'
                btn.append([InlineKeyboardButton(
                    "🔄 Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(
                    "🔄 Try Again", url=f"https://t.me/{Config.BOT_USERNAME}?start={cmd.command[1]}")])

        await bot.send_message(
            chat_id=cmd.from_user.id,
            text=f"> {Config.FORCE_SUB_TEXT}",
            reply_markup=InlineKeyboardMarkup(btn),
        )
        return

    usr_cmd = cmd.text.split("_", 1)[-1]

    # Default /start
    if usr_cmd == "/start":
        ms = await cmd.reply_sticker(random.choice(Config.STICKER_LIST))
        await asyncio.sleep(2)
        await add_user_to_database(bot, cmd)
        await ms.delete()

        await cmd.reply_photo(
            photo=random.choice(Config.SNOW_PICS),
            caption=Config.HOME_TEXT.format(
                cmd.from_user.first_name, cmd.from_user.id),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📢 Updates", url="https://t.me/Kdramaland"),
                    InlineKeyboardButton(
                        "💬 Support", url="https://t.me/Klands")
                ],
                [
                    InlineKeyboardButton(
                        "ℹ️ About Bot", callback_data="aboutbot"),
                    InlineKeyboardButton(
                        "👨‍💻 About Dev", callback_data="aboutdevs"),
                ],
                [InlineKeyboardButton("❌ Close", callback_data="closeMessage")]
            ])
        )
        return

    # File fetching
    if (cmd.text.strip().split("_"))[0].split(" ")[1] == Config.BOT_USERNAME:
        try:
            try:
                file_id = int(b64_to_str(usr_cmd).split("_")[-1])
            except (Error, UnicodeDecodeError):
                file_id = int(usr_cmd.split("_")[-1])

            GetMessage = await bot.get_messages(chat_id=Config.DB_CHANNEL, message_ids=file_id)
            message_ids = []

            if GetMessage.text:
                message_ids = GetMessage.text.split(" ")
                await cmd.reply_text(
                    text=f"> 📂 **Total Files Found:** `{len(message_ids)}`",
                    disable_web_page_preview=True
                )
            else:
                message_ids.append(int(GetMessage.id))

            for i in range(len(message_ids)):
                await send_media_and_reply(bot, user_id=cmd.from_user.id, file_id=int(message_ids[i]))

        except Exception as err:
            await cmd.reply_text(f"> ❌ Something went wrong!\n\n> **Error:** `{err}`")

    else:
        data = cmd.command[1]
        sent_messages = []
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

        # Batch mode
        if data.split("-", 1)[0] == "BATCH":
            sts = await cmd.reply("> ⏳ **Please wait, sending batch files...**")
            c_caption = await db.get_caption(cmd.from_user.id)
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)

            if not msgs:
                file = await bot.download_media(file_id)
                try:
                    with open(file) as file_data:
                        msgs = json.loads(file_data.read())
                except:
                    await sts.edit("> ❌ **Batch load failed.**")
                    return await bot.send_message(Config.LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs

            for msg in msgs:
                title = msg.get("title")
                size = get_size(int(msg.get("size", 0)))
                f_caption = msg.get("caption", "")
                if c_caption:
                    try:
                        f_caption = c_caption.format(
                            mention=cmd.from_user.mention,
                            filename=title or "",
                            filesize=size or ""
                        )
                    except Exception as e:
                        logger.exception(e)
                        f_caption = f_caption
                if not f_caption:
                    f_caption = f"📄 **{title}**"

                try:
                    filz = await bot.send_cached_media(
                        chat_id=cmd.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                    )
                    sent_messages.append(filz)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    filz = await bot.send_cached_media(
                        chat_id=cmd.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                    )
                    sent_messages.append(filz)
                except Exception as e:
                    logger.warning(e, exc_info=True)
                    continue
                await asyncio.sleep(1)

            await sts.delete()
            return await cmd.reply("> ✅ **All batch files sent successfully!**")

        # DSTORE mode
        elif data.split("-", 1)[0] == "DSTORE":
            sts = await cmd.reply("> ⏳ **Please wait, retrieving stored files...**")
            c_caption = await db.get_caption(cmd.from_user.id)
            b_string = data.split("-", 1)[1]
            decoded = (base64.urlsafe_b64decode(
                b_string + "=" * (-len(b_string) % 4))).decode("ascii")
            try:
                f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
            except:
                f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
                protect = "batch"

            async for msg in bot.iter_cmds(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
                if msg.media:
                    media = getattr(msg, msg.media)
                    if c_caption:
                        try:
                            f_caption = c_caption.format(
                                mention=cmd.from_user.mention,
                                filename=getattr(media, 'file_name', ''),
                                filesize=getattr(media, 'file_size', ''),
                                file_caption=getattr(msg, 'caption', '')
                            )
                        except Exception as e:
                            logger.exception(e)
                            f_caption = getattr(msg, 'caption', '')
                    else:
                        file_name = getattr(media, 'file_name', '')
                        f_caption = getattr(msg, 'caption', file_name)

                    try:
                        await msg.copy(
                            cmd.chat.id,
                            caption=f_caption,
                            protect_content=True if protect == "/pbatch" else False
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(
                            cmd.chat.id,
                            caption=f_caption,
                            protect_content=True if protect == "/pbatch" else False
                        )
                    except Exception as e:
                        logger.exception(e)
                        continue

                elif msg.empty:
                    continue
                else:
                    try:
                        await msg.copy(
                            cmd.chat.id,
                            protect_content=True if protect == "/pbatch" else False
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(
                            cmd.chat.id,
                            protect_content=True if protect == "/pbatch" else False
                        )
                    except Exception as e:
                        logger.exception(e)
                        continue
                await asyncio.sleep(1)

            await sts.delete()
            return await cmd.reply("> ✅ **All stored files sent successfully!**")

        # Single file
        files_ = await get_file_details(file_id)
        sm = await cmd.reply("> ⏳ **Fetching your file...**")

        if not files_:
            c_caption = await db.get_caption(cmd.from_user.id)
            await sm.delete()
            pre, file_id = ((base64.urlsafe_b64decode(
                data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:
                msg = await bot.send_cached_media(
                    chat_id=cmd.from_user.id,
                    file_id=file_id,
                    protect_content=True if pre == 'filep' else False
                )
                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = file.file_name
                size = get_size(file.file_size)
                f_caption = f"**{title}**"

                if c_caption:
                    try:
                        f_caption = c_caption.format(
                            filename=title or "",
                            filesize=size or ""
                        )
                    except:
                        return
                await msg.edit_caption(f_caption)
                return
            except:
                pass
            return await cmd.reply("> ❌ **No such file exists.**")

        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption

        if c_caption:
            try:
                f_caption = c_caption.format(
                    filename=title or "",
                    filesize=size or ""
                )
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if not f_caption:
            f_caption = f"**{files.file_name}**"

        await bot.send_cached_media(
            chat_id=cmd.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False
        )

        await cmd.reply("> ✅ **File sent successfully!**")


@Client.on_message((filters.document | filters.video | filters.audio) & ~filters.chat(Config.DB_CHANNEL) & filters.private)
async def main(bot: Client, message: Message):
    try:
        await add_user_to_database(bot, message)
        await message.reply_text(
            text="> 📂 **Choose an option below:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📦 Save in Batch", callback_data="addToBatchTrue")],
                [InlineKeyboardButton(
                    "🔗 Get Sharable Link", callback_data="addToBatchFalse")]
            ]),
            reply_to_message_id=message.id
        )
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
