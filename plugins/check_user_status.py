import datetime
from configs import Config
from utility.database import Database

db = Database(Config.DATABASE_URL, Config.BOT_USERNAME)


async def handle_user_status(bot, cmd):
    chat_id = cmd.from_user.id

    # ─── Register New User ─────────────────────────
    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        await bot.send_message(
            Config.LOG_CHANNEL,
            (
                "> 👤 **New User Joined**\n\n"
                f"➥ Name: [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id})\n"
                f"➥ ID: `{cmd.from_user.id}`\n"
                f"➥ Started using: @{Config.BOT_USERNAME}"
            )
        )

    # ─── Check Ban Status ──────────────────────────
    ban_status = await db.get_ban_status(chat_id)
    if ban_status["is_banned"]:
        banned_on = datetime.date.fromisoformat(ban_status["banned_on"])
        ban_duration = ban_status["ban_duration"]

        # Check if ban expired
        if (datetime.date.today() - banned_on).days > ban_duration:
            await db.remove_ban(chat_id)
        else:
            remaining_days = ban_duration - (datetime.date.today() - banned_on).days
            return await cmd.reply_text(
                "🚫 **Access Denied!**\n\n"
                f"> You are banned from using this bot.\n"
                f"> ⏳ Remaining Ban: `{remaining_days}` day(s)\n\n"
                "🔓 **If you think this is a mistake, contact [Admin](https://t.me/Snowball_Official)**"
            )
