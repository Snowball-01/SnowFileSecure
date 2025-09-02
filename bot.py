import logging
import logging.config
from datetime import datetime
from typing import Union, Optional, AsyncGenerator

from pytz import timezone
from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer

from configs import Config

# ────────────────────────────────
# Logging Configuration
# ────────────────────────────────
logging.config.fileConfig("logging.conf")
log = logging.getLogger("FileStoreBot")
log.setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


# ────────────────────────────────
# Bot Class
# ────────────────────────────────
class Bot(Client):
    def __init__(self):
        super().__init__(
            name=Config.BOT_USERNAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={"root": "plugins"},
        )
        self.start_time = datetime.now()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username

        # ─── Webhook Setup ───
        if Config.WEBHOOK:
            from plugins import web_server
            from aiohttp import web

            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", Config.PORT).start()

        # ─── Startup Logs ───
        log.info("🚀 Bot started successfully!")
        log.info(f"🤖 Name: {me.first_name}")
        log.info(f"🔗 Username: @{me.username}")
        log.info(f"📚 Pyrogram v{__version__} | Layer {layer}")
        log.info(f"🕒 Started at: {self.start_time.strftime('%d-%m-%Y %I:%M:%S %p')}")

        # ─── Notify Owner ───
        try:
            await self.send_message(
                Config.ADMINS[0],
                f"✅ **{me.first_name}** is now online!\n\n"
                f"🕒 Started at: `{self.start_time.strftime('%d-%m-%Y %I:%M:%S %p')}`\n"
                f"📚 Version: `Pyrogram v{__version__} | Layer {layer}`",
            )
        except Exception as e:
            log.warning(f"⚠️ Couldn’t send start message to owner: {e}")

        # ─── Notify Log Channel ───
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**🔄 {me.mention} restarted!**\n\n"
                    f"📅 Date: `{curr.strftime('%d %B, %Y')}`\n"
                    f"⏰ Time: `{curr.strftime('%I:%M:%S %p')}`\n"
                    f"🌐 Timezone: `Asia/Kolkata`\n\n"
                    f"🉐 Version: `Pyrogram v{__version__} | Layer {layer}`",
                )
            except Exception as e:
                log.error("❌ Failed to send restart message in LOG_CHANNEL. "
                          "Make sure bot is **Admin** there.")

    async def stop(self, *args):
        await super().stop()
        uptime = datetime.now() - self.start_time
        log.info(f"🛑 Bot stopped! Uptime: {uptime}")

    async def iter_messages(
        self, chat_id: Union[int, str], limit: int, offset: int = 0
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Custom message iterator with offset support."""
        current = offset
        while current < limit:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(
                chat_id, list(range(current, current + new_diff + 1))
            )
            for message in messages:
                yield message
                current += 1


# ────────────────────────────────
# Run Bot
# ────────────────────────────────
if __name__ == "__main__":
    bot = Bot()
    bot.run()
