import datetime
import motor.motor_asyncio
from configs import Config


def ban_status_default(is_banned: bool = False, duration: int = 0, reason: str = "") -> dict:
    """Default ban status structure."""
    return dict(
        is_banned=is_banned,
        ban_duration=duration,
        banned_on=datetime.datetime.utcnow().isoformat() if is_banned else datetime.date.max.isoformat(),
        ban_reason=reason
    )


class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, user_id: int) -> dict:
        """Return a new user document with defaults."""
        base = dict(
            id=int(user_id),
            join_date=datetime.datetime.utcnow().isoformat(),
            caption=None,
        )
        if user_id in Config.ADMINS:
            base["force_sub"] = None
        else:
            base["ban_status"] = ban_status_default()
        return base

    # -------------------- Caption -------------------- #
    async def set_caption(self, user_id: int, caption: str | None):
        await self.col.update_one({"id": int(user_id)}, {"$set": {"caption": caption}})

    async def get_caption(self, user_id: int) -> str | None:
        user = await self.col.find_one({"id": int(user_id)})
        return user.get("caption") if user else None

    # -------------------- Users -------------------- #
    async def add_user(self, user_id: int):
        await self.col.insert_one(self.new_user(user_id))

    async def is_user_exist(self, user_id: int) -> bool:
        return bool(await self.col.find_one({"id": int(user_id)}))

    async def total_users_count(self) -> int:
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id: int):
        await self.col.delete_many({"id": int(user_id)})

    # -------------------- Ban System -------------------- #
    async def remove_ban(self, user_id: int):
        await self.col.update_one({"id": int(user_id)}, {"$set": {"ban_status": ban_status_default()}})

    async def ban_user(self, user_id: int, ban_duration: int, ban_reason: str):
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {"ban_status": ban_status_default(True, ban_duration, ban_reason)}}
        )

    async def get_ban_status(self, user_id: int) -> dict:
        user = await self.col.find_one({"id": int(user_id)})
        return user.get("ban_status", ban_status_default()) if user else ban_status_default()

    async def get_all_banned_users(self):
        return self.col.find({"ban_status.is_banned": True})

    # -------------------- Force Subscribe -------------------- #
    async def set_fsub(self, fsub_id: str | None):
        await self.col.update_one({"id": int(Config.ADMINS[0])}, {"$set": {"force_sub": fsub_id}})

    async def get_fsub(self) -> str | None:
        admin = await self.col.find_one({"id": int(Config.ADMINS[0])})
        return admin.get("force_sub") if admin else None


# Initialize DB
db = Database(Config.DATABASE_URL, Config.BOT_USERNAME)
