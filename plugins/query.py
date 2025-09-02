import random
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, InputMediaPhoto
from pyrogram import Client, filters
from pyrogram.errors import QueryIdInvalid

from configs import Config
from utility.helper import is_subscribed
from utility.database import db
from plugins.save_media import save_media_in_channel, save_batch_media_in_channel

MediaList = {}


# ─── Clear User Batch ───────────────────────────────
@Client.on_message(filters.private & filters.command("clear_batch"))
async def clear_user_batch(bot: Client, m: Message):
    MediaList[str(m.from_user.id)] = []
    await m.reply_text("🗑️ **Your batch list has been cleared successfully!**")


# ─── Callback Query Handler ─────────────────────────
@Client.on_callback_query()
async def button(bot: Client, cmd: CallbackQuery):
    cb_data = cmd.data

    # ─── Force Subscription Check ────────────────────
    if cb_data.startswith("checksub"):
        _, fileid = cb_data.split("#")
        if Config.DYNAMIC_FSUB:
            fsub = await db.get_fsub()
        else:
            fsub = Config.FORCE_SUB
        if fsub and not await is_subscribed(bot, cmd, fsub):
            return await cmd.answer(
                f"⚠️ Hey {cmd.from_user.first_name},\n\n"
                "You must join our updates channel first!",
                show_alert=True,
            )
        return await cmd.answer(url=f"https://t.me/{Config.BOT_USERNAME}?start={fileid}")

    # ─── About Bot ──────────────────────────────────
    elif cb_data == "aboutbot":
        await cmd.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.SNOW_PICS),
                Config.ABOUT_BOT_TEXT.format(bot.mention)
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "👨‍💻 About Dev", callback_data="aboutdevs"),
                    InlineKeyboardButton("🏠 Home", callback_data="gotohome"),
                ]
            ])
        )

    # ─── About Dev ──────────────────────────────────
    elif cb_data == "aboutdevs":
        await cmd.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.SNOW_PICS),
                Config.ABOUT_DEV_TEXT
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🤖 About Bot", callback_data="aboutbot"),
                    InlineKeyboardButton("🏠 Home", callback_data="gotohome"),
                ]
            ])
        )

    # ─── Home Menu ──────────────────────────────────
    elif cb_data == "gotohome":
        await cmd.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.SNOW_PICS),
                Config.HOME_TEXT.format(
                    cmd.message.chat.first_name, cmd.message.chat.id)
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📢 Update Channel", url="https://t.me/Kdramaland"),
                    InlineKeyboardButton(
                        "💬 Support Group", url="https://t.me/Klands"),
                ],
                [
                    InlineKeyboardButton(
                        "🤖 About Bot", callback_data="aboutbot"),
                    InlineKeyboardButton(
                        "👨‍💻 About Dev", callback_data="aboutdevs"),
                ],
                [
                    InlineKeyboardButton(
                        "❌ Close", callback_data="closeMessage"),
                ]
            ])
        )

    # ─── Ban User from Updates Channel ──────────────
    elif cb_data.startswith("ban_user_"):
        user_id = cb_data.split("_", 2)[-1]
        if not Config.UPDATES_CHANNEL:
            return await cmd.answer("⚠️ Updates channel not set!", show_alert=True)
        if cmd.from_user.id != Config.BOT_OWNER:
            return await cmd.answer("⛔ You are not authorized for this action!", show_alert=True)

        try:
            await bot.kick_chat_member(int(Config.UPDATES_CHANNEL), int(user_id))
            return await cmd.answer("✅ User banned from updates channel.", show_alert=True)
        except Exception as e:
            return await cmd.answer(f"❌ Failed to ban user!\n\nError: {e}", show_alert=True)

    # ─── Save File to Batch ─────────────────────────
    elif cb_data == "addToBatchTrue":
        MediaList.setdefault(str(cmd.from_user.id), []).append(
            cmd.message.reply_to_message.id)
        await cmd.message.edit(
            "📂 **File saved to batch!**\n\n"
            "➡️ Use the button below to generate a batch link.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Get Batch Link",
                                      callback_data="getBatchLink")],
                [InlineKeyboardButton(
                    "❌ Close", callback_data="closeMessage")],
            ])
        )

    # ─── Save Media Directly ────────────────────────
    elif cb_data == "addToBatchFalse":
        await save_media_in_channel(bot, editable=cmd.message, message=cmd.message.reply_to_message)

    # ─── Generate Batch Link ─────────────────────────
    elif cb_data == "getBatchLink":
        message_ids = MediaList.get(str(cmd.from_user.id))
        if not message_ids:
            return await cmd.answer("⚠️ Your batch list is empty!", show_alert=True)

        await cmd.message.edit("⏳ **Generating your batch link...**")
        await save_batch_media_in_channel(bot=bot, editable=cmd.message, message_ids=message_ids)
        MediaList[str(cmd.from_user.id)] = []

    # ─── Close Message ──────────────────────────────
    elif cb_data == "closeMessage":
        await cmd.message.delete(True)

    # ─── Final Fallback ─────────────────────────────
    try:
        await cmd.answer()
    except QueryIdInvalid:
        pass
