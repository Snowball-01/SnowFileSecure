from pyrogram import Client, filters
from utility.database import db


# ─── Set Caption ─────────────────────────────
@Client.on_message(filters.private & filters.command("set_caption"))
async def set_caption(client, message):
    if len(message.command) == 1:
        return await message.reply_text(
            "**⚡ Set Custom Caption**\n\n"
            "You can use placeholders like:\n"
            "> `{filename}` → File Name\n"
            "> `{filesize}` → File Size\n\n"
            "**Example:**\n"
            "`/set_caption {filename}\n\n💾 Size: {filesize}`"
        )

    caption = message.text.split(" ", 1)[1]
    await db.set_caption(message.from_user.id, caption=caption)

    await message.reply_text(
        "**✅ Caption Saved Successfully!**\n\n"
        f"> Now all your files will include this caption."
    )


# ─── Delete Caption ──────────────────────────
@Client.on_message(filters.private & filters.command("del_caption"))
async def delete_caption(client, message):
    caption = await db.get_caption(message.from_user.id)

    if not caption:
        return await message.reply_text("😔 **No caption found to delete!**")

    await db.set_caption(message.from_user.id, caption=None)
    await message.reply_text("🗑️ **Your caption has been deleted successfully!**")


# ─── See Caption ─────────────────────────────
@Client.on_message(filters.private & filters.command("see_caption"))
async def see_caption(client, message):
    caption = await db.get_caption(message.from_user.id)

    if caption:
        await message.reply_text(
            "**📌 Your Current Caption:**\n\n"
            f"`{caption}`"
        )
    else:
        await message.reply_text("😔 **You haven't set any caption yet!**")
