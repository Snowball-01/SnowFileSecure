import os
import re
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

id_pattern = re.compile(r"^.\d+$")


class Config(object):
    # ─── Snow Client Config ──────────────────────────────
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")  # ⚠️ without (@)

    # ─── Database Config ────────────────────────────────
    DB_CHANNEL = int(os.environ.get("DB_CHANNEL", ""))  # ⚠️ must start with (-100)
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # ─── Other Config ───────────────────────────────────
    ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "").split()] if os.environ.get("ADMINS") else []
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))  # ⚠️ must start with (-100)
    DYNAMIC_FSUB = os.environ.get("DYNAMIC_FSUB", "False").lower() == "true"
    FORCE_SUB = os.environ.get("FORCE_SUB", "")  # ⚠️ SET THIS IF DYNAMIC_FSUB IS DISABLE 
    FORCE_SUB_TEXT = (
        "FORCE_SUB_TEXT",
        "**⚠️ Access Denied!**\n\n"
        "> You are not a member of our __Backup Channel__.\n\n"
        "➥ To unlock files, please:\n"
        "   1️⃣ Click on **❆ Join Our Backup Channel ❆**\n"
        "   2️⃣ Join the channel\n"
        "   3️⃣ Tap **↻ Try Again**\n\n"
        "__Once done, files will be available instantly!__",
    )

    SNOW_PICS = (
        "https://i.ibb.co/1YtK5RC7/image-2025-09-01-00-03-34.png "
        "https://i.ibb.co/0j4sjNnb/image-2025-09-01-00-04-18.png "
        "https://i.ibb.co/0v5H5wR/image-2025-09-01-00-11-15.png "
        "https://i.ibb.co/kgFb7zw2/image-2025-09-01-00-22-38.png "
        "https://i.ibb.co/KzpSN3qW/image-2025-09-01-00-56-24.png "
        "https://i.ibb.co/2YHsVd84/image-2025-09-01-01-00-39.png "
        "https://i.ibb.co/n8ffjSGX/image-2025-09-01-01-08-54.png "
        "https://i.ibb.co/STcY0qF/image-2025-09-01-01-29-04.png "
        "https://i.ibb.co/xSTncPCy/image-2025-09-01-01-44-54.png"
    ).split()

    STICKER_LIST = (
        "CAACAgUAAxkBAAEOXnVoDRJl3cPuB2NM-KsawM2oiheEpQAC-BMAAloPIVTXy-u405E-ljYE "
        "CAACAgUAAxkBAAEOXndoDRJvOLwv2t_WRcurdXBVqgV_pgACFBEAApnXGFTzROW3qYnPHjYE "
        "CAACAgUAAxkBAAEOXnloDRJxO0xqNOB01_9Vj85vvU3ZsgACuhQAApWeIVT49xrUlwgT_TYE "
        "CAACAgUAAxkBAAEOXntoDRKNKIoPgWwad8TylzNwSpx70QACehIAAmPpGVS94d8_5WCbBTYE "
        "CAACAgUAAxkBAAEOXn1oDRKVe4R5Ru5HEZqq2Gw9JwUiBAACsRgAAhxGGFStTAamCtyADDYE "
        "CAACAgUAAxkBAAEOXn9oDRKcV0rzn-Q5LsKER59s1S1MuwACfBUAAhI4GVRVncvIczydZTYE "
        "CAACAgUAAxkBAAEOXoFoDRKj_kkiQhfxr7nt1YTvncVFXgACqxUAAqUmIFTGXvznC_o_NTYE "
        "CAACAgUAAxkBAAEOXoNoDRKqUNudsVJOjdA53TBfDVRa2QAC3hYAAvukGFQcLHgws9NL0jYE "
        "CAACAgUAAxkBAAEOXoVoDRKxPWeVz6hXrU-aWFGc10DR7AACyRkAAh5IGFRmce-hZFtG5zYE "
        "CAACAgUAAxkBAAEOXodoDRK3V6vZiFFi8pFMeE7U2ah-7QACSRUAAr9yIFTgk-oIceFdoDYE "
        "CAACAgUAAxkBAAEOXoloDRK-oEKF6jtx81ggZ4ni4t8uLAACHxQAAoCRIFSr7kRKb9dWUTYE "
        "CAACAgUAAxkBAAEOXotoDRLFegiDjgguuk3N0cx_KuwLewACbBYAAp_wGVQoPrC9NUGZ1jYE "
        "CAACAgUAAxkBAAEOXo1oDRLN7bKvm9c__XMJO9kG7LKyjQAChBYAAlH5GVS5UVs0itWoMTYE "
        "CAACAgUAAxkBAAEOXo9oDRLTAx5bqk68Hc30FT9aJmnUOAACVBYAAlnzIVSdYbYXFgephDYE "
        "CAACAgUAAxkBAAEOXpFoDRLqQk5wu1UimKSwkMxiD4t2SAACuRQAAtsaGFTCtQxA3VUc9jYE "
        "CAACAgUAAxkBAAEOXpNoDRL_vdJo6VK7LcpBLdUyP86aZQAC5hUAAq02IFQlKRfy2MoTnTYE "
        "CAACAgUAAxkBAAEOXpVoDRMGNXR92uVj3RHTqIBXGz_WEQACNxMAAluVGFS1tCMc5lAIDTYE "
        "CAACAgUAAxkBAAEOXpdoDRMPb0OGA9oRTzBavosPk2qOyAACvBIAAmI1IFQw1_vZ19uSJDYE "
        "CAACAgUAAxkBAAEOXploDRMVAmg3wb2rJfU_PixohTQiLAACkxoAAvfhGFQKIAOy5279HDYE "
        "CAACAgUAAxkBAAEOXptoDRMdiQtPWVyhs9VzOObr5VURpwACSBYAAltxIVQ4-qfFw1MbjTYE "
        "CAACAgUAAxkBAAEOXp1oDRMkrVal4WlRBCJgBlEhKDLSawAClRcAApqrGFTCwBF6lmpJGDYE "
        "CAACAgUAAxkBAAEOXp9oDRMrgf5YzqU7-Ks0q1UKH8Ci_wACNxQAAuXPGVSLh3FkEumnTjYE "
        "CAACAgUAAxkBAAEOXqFoDRMzt68j_Kj1pE5ukejP-Knu2gACiRMAAtMGGFSia74I8v0L6jYE "
        "CAACAgUAAxkBAAEOXqNoDRM7dekBxUGCNVOZvf5ANHSbUgACqxUAAjDEIVSS4ok-qLEAAbU2BA "
        "CAACAgUAAxkBAAEOXqVoDRNCPzk-iJOQSfpvOskjyDjeLQACbRcAAkn7GVTdi07rrVEUmDYE "
        "CAACAgUAAxkBAAEOXqtoDRNYfheegZiz6O1Ol7yf92Fr3wAChhQAAgIeIVQYVQrL_P44rjYE"
    ).split()

    BOT_UPTIME = time.time()

    # ─── Web Support Config ──────────────────────────────
    PORT = os.environ.get("PORT", "8080")
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))

    # ─── Bot Texts ──────────────────────────────────────
    ABOUT_BOT_TEXT = """
**❆ Permanent FileStore Bot ❆**

> Send me any **media/file**, I’ll save it and give you a **shareable permanent link**.  
> Works in both **private chats** & **channels** (with edit permission).

**Features:**
➥ **Bot Name** : {}
➥ **Developer** : [ѕησωвαℓℓ ❄️](https://t.me/Snowball_Official)  
➥ **Founder of** : [K-Lᴀɴᴅ](https://t.me/Kdramaland)  
➥ **Library** : [Pyrogram](https://github.com/pyrogram)  
➥ **Language** : [Python 3](https://www.python.org)  
➥ **Database** : [MongoDB](https://cloud.mongodb.com)  
➥ **Server** : `VPS`  
➥ **Version** : `v2.0.0`
"""

    ABOUT_DEV_TEXT = """
🧑🏻‍💻 **Developer** : [Snowball](https://t.me/Snowball_Official)  

> A simple learner, improving daily by exploring **official docs**.  

⚡ **Note**:  
➥ Adult content will be deleted from database.  
➥ Respect the work & keep it clean.  

💠 **Want to Support?**  
[Donate Me](https://t.me/Snowball_Official)
"""

    HOME_TEXT = """
**👋 Hello [{}](tg://user?id={})**

> ❆ Welcome to **Permanent FileStore Bot** ❆  

__✨ How It Works? ✨__  
🍃 Send me any file → I’ll upload it to my **database** → You’ll get a **permanent share link**.  

**⚡ Benefits:**  
> • Protects your movie/channel files from **copyright strikes**  
> • Works in both **DMs** & **Channels**  
> • Safe, Fast & Reliable  

Type `/about` to know more!
"""


ABOUT_TEXT = """
**❆ About This Bot ❆**

> A simple yet powerful **Permanent FileStore Bot**.  
> Save files once, get a **forever shareable link** — no limits, no worries.

**✨ What I Can Do?**
➥ Store any **media/file** permanently  
➥ Provide **instant share links**  
➥ Work in both **Private Chats & Channels**  
➥ Protect channel owners from **copyright strikes**  

**🔧 Tech Behind Me**
➥ **Language** : `Python 3`  
➥ **Library** : [Pyrogram](https://github.com/pyrogram)  
➥ **Database** : [MongoDB](https://cloud.mongodb.com)  
➥ **Server** : `VPS`  

**👨‍💻 Developer**
➥ [ѕησωвαℓℓ ❄️](https://t.me/Snowball_Official)  
__A learner & builder, constantly improving.__  

**💠 Version** : `v2.0.0`  
"""
