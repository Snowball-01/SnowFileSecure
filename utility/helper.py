import asyncio
import logging
from base64 import standard_b64encode, standard_b64decode, urlsafe_b64encode
from struct import pack

from pyrogram import enums, Client
from pyrogram.errors import UserNotParticipant
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance, Document, fields

from configs import Config
from .database import db as database


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# MongoDB setup
client = AsyncIOMotorClient(Config.DATABASE_URL)
db = client[Config.BOT_USERNAME]
instance = Instance.from_db(db)


@instance.register
class Media(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        collection_name = "STORE_FILES"


# -------------------- Encoding Helpers -------------------- #
def str_to_b64(value: str) -> str:
    return standard_b64encode(value.encode()).decode()


def b64_to_str(value: str) -> str:
    return standard_b64decode(value.encode()).decode()


def encode_file_id(raw: bytes) -> str:
    """Encode raw bytes into a file_id-like base64 string."""
    r, n = b"", 0
    for i in raw + b"\x16\x04":  # 22 + 4 as bytes
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id: str) -> tuple[str, str]:
    """Return (file_id, file_ref) from a new_file_id."""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash,
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref


# -------------------- Database Helpers -------------------- #
async def get_file_details(query: str):
    """Fetch file details by file_id."""
    cursor = Media.find({"file_id": query})
    return await cursor.to_list(length=1)


def get_size(size: int | float) -> str:
    """Convert bytes into human-readable size."""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"


# -------------------- Force Subscribe Helpers -------------------- #
async def is_subscribed(bot: Client, query: Message, fsub: str) -> bool:
    try:
        user = await bot.get_chat_member(fsub, query.from_user.id)
        return user.status != enums.ChatMemberStatus.BANNED
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.warning("Error checking subscription", exc_info=True)
        return False


async def force_sub(bot: Client, cmd: Message, fsub: str):
    """Send force subscribe message with join button."""
    invite_link = await bot.create_chat_invite_link(fsub)
    buttons = [[InlineKeyboardButton("📢 Join Update Channel", url=invite_link.invite_link)]]
    text = (
        "> ⚠️ **You must join our update channel to use this bot.**\n\n"
        "> Please join and try again."
    )
    return await cmd.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))


# -------------------- User Helpers -------------------- #
async def add_user_to_database(bot: Client, cmd: Message):
    """Add a new user to the database and log to admin channel."""
    if not await database.is_user_exist(cmd.from_user.id):
        await database.add_user(cmd.from_user.id)

        if Config.LOG_CHANNEL:
            try:
                await bot.send_message(
                    int(Config.LOG_CHANNEL),
                    (
                        f"> 👤 **#NEW_USER**\n\n"
                        f"> [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id}) "
                        f"started @{Config.BOT_USERNAME}"
                    ),
                )
            except Exception as e:
                logger.warning("Failed to log new user", exc_info=True)


# -------------------- Cleanup Helpers -------------------- #
async def delete_files_after_delay(messages: list[Message], delay_minutes: int, logger: logging.Logger = logger):
    """Delete a list of messages after a delay in minutes."""
    try:
        await asyncio.sleep(delay_minutes * 60)  # Convert minutes to seconds
        for message in messages:
            try:
                await message.delete()
            except Exception as e:
                logger.warning("Failed to delete a message", exc_info=True)
    except Exception as e:
        logger.warning("Error in delete_files_after_delay", exc_info=True)
