# -----------------------------------------------
# 🔸 RAJSHREE MUSIC — MustJoin (Owner-Controlled)
# 🔹 Set MUST_JOIN env var to your channel username
#    to require users to join before using the bot.
#    Leave it empty (default) to disable this feature.
# -----------------------------------------------
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from MADARAMUSIC import app

# Set MUST_JOIN in your environment variables to your own channel.
# Leave empty to disable force-join (default = disabled).
MUST_JOIN = os.environ.get("MUST_JOIN", "").strip()

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.lstrip("@").isalpha() or MUST_JOIN.startswith("@"):
                link = "https://t.me/" + MUST_JOIN.lstrip("@")
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply_text(
                    f"🔒 <b>ᴊᴏɪɴ ʀᴇǫᴜɪʀᴇᴅ</b>\n\n"
                    f"ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📢 Join Channel", url=link)]]
                    )
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        pass
