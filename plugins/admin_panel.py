import os
import sys
import time
import asyncio
import logging
import datetime
import traceback

from configs import Config
from plugins.check_user_status import handle_user_status
from utility.database import db

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid
)

# ─── Logger Setup ─────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ─── Check User Status ────────────────────────
@Client.on_message(filters.private)
async def check_user(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)
    return await cmd.continue_propagation()

# ─── Bot Stats ────────────────────────────────


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMINS))
async def get_stats(bot, message: Message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(
        time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply("⏳ **Fetching bot status...**")
    end_t = time.time()
    ping_ms = (end_t - start_t) * 1000

    await st.edit(
        text=(
            "**📊 Bot Status Report**\n\n"
            f"⏰ Uptime: `{uptime}`\n"
            f"⚡ Ping: `{ping_ms:.3f} ms`\n"
            f"👥 Total Users: `{total_users}`"
        )
    )


# ─── Restart ──────────────────────────────────
@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMINS))
async def restart_bot(_, m: Message):
    await m.reply_text("🔄 **Restarting bot...**\n> Please wait a few seconds ⏳")
    os.execl(sys.executable, sys.executable, *sys.argv)


# ─── Broadcast ────────────────────────────────
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMINS) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(
        Config.LOG_CHANNEL,
        f"📢 **Broadcast Started by:** {m.from_user.mention} (`{m.from_user.id}`)"
    )

    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("🚀 **Broadcast initiated...**")

    done, success, failed = 0, 0, 0
    start_time = time.time()
    total_users = await db.total_users_count()

    async for user in all_users:
        status = await send_msg(user["id"], broadcast_msg)
        if status == 200:
            success += 1
        else:
            failed += 1
            if status == 400:
                await db.delete_user(user["id"])
        done += 1

        if not done % 20:
            await sts_msg.edit(
                f"📢 **Broadcast Progress**\n\n"
                f"> 👥 Total Users: `{total_users}`\n"
                f"> ✅ Success: `{success}`\n"
                f"> ❌ Failed: `{failed}`\n"
                f"> 📌 Completed: `{done}/{total_users}`"
            )

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"✅ **Broadcast Completed!**\n\n"
        f"⏳ Duration: `{completed_in}`\n"
        f"👥 Total Users: `{total_users}`\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`"
    )


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
        logger.info(f"⚠️ User {user_id} removed (invalid/deactivated/blocked)")
        return 400
    except Exception as e:
        logger.error(f"❌ Error sending to {user_id}: {e}")
        return 500


# ─── Ban User ─────────────────────────────────
@Client.on_message(filters.private & filters.command("ban_user") & filters.user(Config.ADMINS))
async def ban_user(c: Client, m: Message):
    if len(m.command) < 4:
        return await m.reply_text(
            "🚫 **Ban Command Usage:**\n\n"
            "`/ban_user user_id duration reason`\n\n"
            "> Example:\n"
            "> `/ban_user 1234567 30 Misusing the bot`"
        )

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])

        if user_id in Config.ADMINS:
            return

        await db.ban_user(user_id, ban_duration, ban_reason)

        # Notify user
        try:
            await c.send_message(
                user_id,
                f"🚫 **You are banned from using this bot!**\n\n"
                f"⏳ Duration: `{ban_duration}` day(s)\n"
                f"📝 Reason: __{ban_reason}__\n\n"
                f"> 🔒 Contact admin if you think this is a mistake."
            )
            notified = "✅ User notified successfully!"
        except Exception:
            notified = "⚠️ Failed to notify the user."

        await m.reply_text(
            f"🚷 **Ban Successful**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"⏳ Duration: `{ban_duration}` day(s)\n"
            f"📝 Reason: {ban_reason}\n\n"
            f"> {notified}"
        )
    except Exception:
        await m.reply_text(
            f"❌ **Error while banning user**\n\n"
            f"> `{traceback.format_exc()}`"
        )


# ─── Unban User ───────────────────────────────
@Client.on_message(filters.private & filters.command("unban_user") & filters.user(Config.ADMINS))
async def unban_user(c: Client, m: Message):
    if len(m.command) < 2:
        return await m.reply_text(
            "♻️ **Unban Command Usage:**\n\n"
            "`/unban_user user_id`\n\n"
            "> Example:\n"
            "> `/unban_user 1234567`"
        )

    try:
        user_id = int(m.command[1])
        if user_id in Config.ADMINS:
            return
        await db.remove_ban(user_id)

        try:
            await c.send_message(user_id, "✅ **Your ban has been lifted!**")
            notified = "✅ User notified successfully!"
        except Exception:
            notified = "⚠️ Failed to notify the user."

        await m.reply_text(
            f"♻️ **Unban Successful**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"> {notified}"
        )
    except Exception:
        await m.reply_text(
            f"❌ **Error while unbanning user**\n\n"
            f"> `{traceback.format_exc()}`"
        )


# ─── List Banned Users ────────────────────────
@Client.on_message(filters.private & filters.command("banned_users") & filters.user(Config.ADMINS))
async def banned_users(_, m: Message):
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count, text = 0, ""

    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]

        banned_usr_count += 1
        text += (
            f"> 👤 User ID: `{user_id}`\n"
            f"> ⏳ Duration: `{ban_duration}` days\n"
            f"> 📅 Banned On: `{banned_on}`\n"
            f"> 📝 Reason: {ban_reason}\n\n"
        )

    reply_text = f"🚷 **Total Banned Users:** `{banned_usr_count}`\n\n{text}"

    if len(reply_text) > 4096:
        with open("banned-users.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-users.txt", caption="🚷 Banned Users List")
        os.remove("banned-users.txt")
    else:
        await m.reply_text(reply_text)
