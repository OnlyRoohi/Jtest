# RAJSHREE MUSIC BOT (MADARAMUSIC)

A Telegram Music Player bot that plays music in Telegram voice chats.
Built with Python using Pyrogram/Kurigram and Py-Tgcalls.
Direct yt-dlp backend — no external API dependency — 24h uptime.

**Owner:** MADARA  
**License:** MIT (Restricted) — See LICENSE file

---

## Setup

This is a background worker bot — it has no web frontend.

### Required Environment Variables
Set these in the Secrets/Environment Variables panel:
- `API_ID` — Telegram API ID (from my.telegram.org)
- `API_HASH` — Telegram API Hash (from my.telegram.org)
- `BOT_TOKEN` — Telegram Bot Token (from @BotFather)
- `MONGO_DB_URI` — MongoDB connection URI
- `OWNER_ID` — Your Telegram user ID
- `LOGGER_ID` — Telegram group/channel ID for bot logs

### Session Strings (Required for Music)
- `STRING_SESSION` — Pyrogram session string for the userbot assistant

### Optional
- `STRING_SESSION2` through `STRING_SESSION7` — additional session strings
- `MUST_JOIN` — your channel username to force users to join (leave empty to disable)
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` — for Spotify support
- `BOT_USERNAME` — your bot's Telegram username (without @)
- `BOT_NAME` — display name (default: Rajshree)

### Cookies (for yt-dlp, recommended)
Drop YouTube cookie `.txt` files (Netscape format) into `MADARAMUSIC/assets/`  
The bot auto-rotates between multiple cookie files for best uptime.

---

## Running

```bash
python3 -m MADARAMUSIC
```

---

## Security Notes

- `/eval` and `/sh` commands are restricted to `OWNER_ID` only
- `bkc.py` (porn/explicit content commands) has been permanently removed
- `mustjoin.py` now reads from `MUST_JOIN` env var — defaults to disabled
- All premium/custom Telegram emojis replaced with normal emojis
- No forced-join to any third-party channel

---

## User Preferences
- Package name: MADARAMUSIC (renamed from SHUKLAMUSIC)
- Bot branding: RAJSHREE MUSIC
- Bot owner display name: MADARA
- YouTube backend: direct yt-dlp (no Shruti/external API)
- No premium emojis anywhere in the bot
