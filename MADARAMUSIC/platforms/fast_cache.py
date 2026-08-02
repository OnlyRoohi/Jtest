import os
import asyncio
import aiohttp
import aiofiles
from MADARAMUSIC import app, LOGGER
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIG ---
PLAYLIST_ID = -1001957497326
MONGO_DB_URI = "mongodb+srv://Karma:Nothing0000@cluster0.ewjnsh1.mongodb.net/?appName=Cluster0"
SHRUTI_API_URL = "https://api.shrutibots.site"
SHRUTI_API_KEY = "ShrutiBotsvfxRF6Qt1ejYXnovI3TG"

logger = LOGGER(__name__)
mongodb = AsyncIOMotorClient(MONGO_DB_URI).MADARAMUSIC
trackdb = mongodb.track_cache

def get_vid_id(link):
    if "v=" in link: return link.split('v=')[-1].split('&')[0]
    return link.split('/')[-1]

async def _upload_to_channel(vid_id, file_path, title, is_video):
    try:
        if not os.path.exists(file_path): return
        db_id = f"{vid_id}_video" if is_video else vid_id
        if await trackdb.find_one({"vid_id": db_id}): return
        
        cap = f"**Song:** {title}\n**ID:** `{vid_id}`\n**Saved by:** {app.me.mention}"
        if is_video:
            msg = await app.send_video(PLAYLIST_ID, file_path, caption=cap, supports_streaming=True)
        else:
            msg = await app.send_audio(PLAYLIST_ID, file_path, caption=cap, title=title)

        if msg:
            await trackdb.update_one(
                {"vid_id": db_id}, 
                {"$set": {"message_id": msg.id, "title": title, "type": "video" if is_video else "audio"}}, 
                upsert=True
            )
            logger.info(f"✅ Cached to Channel: {title}")
    except Exception as e:
        logger.error(f"Cache Upload Error: {e}")

async def fetch_from_cache(vid_id, is_video=False):
    db_id = f"{vid_id}_video" if is_video else vid_id
    
    # 1. Local Check
    for ext in ["m4a", "mp4", "mp3", "webm"]:
        filepath = f"downloads/{vid_id}.{ext}"
        if os.path.exists(filepath) and os.path.getsize(filepath) > 2048:
            return os.path.abspath(filepath)

    # 2. Channel DB Check
    doc = await trackdb.find_one({"vid_id": db_id})
    if doc and "message_id" in doc:
        try:
            logger.info(f"🔄 Fetching from Channel DB (Msg ID: {doc['message_id']})")
            msg = await app.get_messages(PLAYLIST_ID, doc['message_id'])
            if msg and not msg.empty:
                media = msg.video or msg.audio or msg.document or msg.voice
                if media:
                    temp_path = f"downloads/{vid_id}.mp4"
                    file = await app.download_media(media.file_id, file_name=temp_path)
                    if file and os.path.getsize(file) > 2048:
                        return file
        except Exception as e:
            logger.error(f"Fetch Error: {e}")
    return None

async def smart_download(link, is_video=False, title="Unknown"):
    vid_id = get_vid_id(link)
    
    # 1. Try Cache First
    cached_file = await fetch_from_cache(vid_id, is_video)
    if cached_file:
        return cached_file, True

    # 2. Download via Shruti API
    ext = "mp4" if is_video else "mp3"
    type_str = "video" if is_video else "audio"
    file_path = f"downloads/{vid_id}.{ext}"
    os.makedirs("downloads", exist_ok=True)
    
    try:
        logger.info(f"🛡️ Downloading via API: {vid_id}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SHRUTI_API_URL}/download", params={"url": vid_id, "type": type_str, "api_key": SHRUTI_API_KEY}, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status == 200:
                    async with aiofiles.open(file_path, mode='wb') as f:
                        async for chunk in resp.content.iter_chunked(131072):
                            await f.write(chunk)
                    
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 2048:
                        # Upload to channel in background so bot doesn't hang
                        asyncio.create_task(_upload_to_channel(vid_id, file_path, title or vid_id, is_video))
                        return file_path, True
    except Exception as e:
        logger.error(f"API Download Failed: {e}")
        
    return None, False
