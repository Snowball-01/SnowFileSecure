<h1 align="center">❄️ SnowFileSecure Bot</h1>
<p align="center">
  <i>A modern Telegram bot to save and share files with permanent links.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Snowball-01/SnowFileSecure?style=for-the-badge&logo=github" alt="Stars" />
  <img src="https://img.shields.io/github/forks/Snowball-01/SnowFileSecure?style=for-the-badge&logo=github" alt="Forks" />
  <img src="https://img.shields.io/github/issues/Snowball-01/SnowFileSecure?style=for-the-badge&logo=github" alt="Issues" />
  <img src="https://img.shields.io/github/license/Snowball-01/SnowFileSecure?style=for-the-badge" alt="License" />
</p>

---

## ✨ Features

* ⚡ Save and manage any media or file directly via Telegram.
* 🔒 Generates **permanent shareable links**.
* 📦 Works in **private chats** and **channels**.
* 🛡 Protects against **data loss** or **copyright strikes**.
* 🐍 Built with **Python 3**, **Pyrogram**, **MongoDB**.
* 🚀 Optimized for **VPS hosting**.

---

## 🎥 Demo

> *(Add bot demo screenshot or GIF here for better visuals)*

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [Configuration](#-configuration)
3. [Usage](#-usage)
4. [Environment Variables](#-environment-variables)
5. [Docker](#-docker)
6. [Contributing](#-contributing)
7. [License](#-license)

---

## ⚙️ Installation

```bash
git clone https://github.com/Snowball-01/SnowFileSecure.git
cd SnowFileSecure
pip install -r requirements.txt
```

---

## 🔧 Configuration

Create a `.env` file with your credentials:

### 📌 Example `.env`

```env
# ─── Snow Client Config ──────────────────────────────
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_USERNAME=YourBotUsername

# ─── Database Config ────────────────────────────────
DB_CHANNEL=-1001234567890
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname

# ─── Other Config ───────────────────────────────────
ADMINS=123456789 987654321
LOG_CHANNEL=-1009876543210
DYNAMIC_FSUB=False
FORCE_SUB=YourBackupChannel # without (@)
```

⚠️ **Do not commit `.env` to GitHub**.

---

## 🚀 Usage

Start the bot with:

```bash
python bot.py
```

Then:

* 📩 Send files to get permanent share links.
* ℹ️ Use `/about` for details.
* 📢 In channels, grant **edit permission** to the bot.

---

## 📌 Environment Variables Reference

| Variable       | Description                                | Required |
| -------------- | ------------------------------------------ | -------- |
| `API_ID`       | Telegram API ID                            | ✅        |
| `API_HASH`     | Telegram API Hash                          | ✅        |
| `BOT_TOKEN`    | Bot token from BotFather                   | ✅        |
| `BOT_USERNAME` | Username of your bot                       | ✅        |
| `DB_CHANNEL`   | Telegram channel ID for file storage       | ✅        |
| `DATABASE_URL` | MongoDB connection URI                     | ✅        |
| `ADMINS`       | Space-separated admin user IDs             | ✅        |
| `LOG_CHANNEL`  | Channel ID for logging                     | ✅        |
| `DYNAMIC_FSUB` | Enable/disable dynamic forced subscription | ❌        |
| `FORCE_SUB`    | Channel username for forced subscription   | ✅        |

---

## 🐳 Docker

Run with Docker:

```bash
docker build -t snowfilestore .
docker run --env-file .env snowfilestore
```

---

## 🤝 Contributing

💡 Contributions are welcome!

* 🐛 Report bugs via [Issues](https://github.com/Snowball-01/SnowFileSecure/issues)
* 🔥 Submit PRs for features or improvements
* 📂 Follow project structure in `/plugins` & `/utility`

---

## 📊 Repo Stats

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=Snowball-01&repo=SnowFileSecure&theme=tokyonight&hide_border=true&border_radius=20" />
  <br>
  <img src="https://github-readme-stats.vercel.app/api?username=Snowball-01&show_icons=true&theme=tokyonight&hide_border=true&border_radius=20" />
  <img src="https://github-readme-streak-stats.herokuapp.com?user=Snowball-01&theme=tokyonight&hide_border=true&border_radius=20" />
</p>

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
