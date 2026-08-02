import asyncio
import os
import re
from typing import Union
import aiohttp
import aiofiles
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, CustomSearch, Playlist
from motor.motor_asyncio import AsyncIOMotorClient

# --- MADARAMUSIC IMPORTS ---
from MADARAMUSIC import LOGGER, app 
from MADARAMUSIC.utils.formatters import time_to_seconds

# --- CONFIG VALUES ---
YT_API_KEY = "30DxNexGenBots0055e5"
YTPROXY = "https://tgapi.xbitcode.com"
PLAYLIST_ID = -1001957497326
MONGO_DB_URI = "mongodb+srv://Karma:Nothing0000@cluster0.ewjnsh1.mongodb.net/?appName=Cluster0"
LIMIT_SECONDS = 900
DOWNLOAD_DIR = "downloads"

# --- SHRUTI API CONFIG ---
SHRUTI_API_URL = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
SHRUTI_API_KEY = os.environ.get("SHRUTI_API_KEY", "ShrutiBotsvfxRF6Qt1ejYXnovI3TG") 

logger = LOGGER(__name__)

# --- DATABASE CONNECTION ---
_mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
mongodb = _mongo_async_.MADARAMUSIC  
trackdb = mongodb.track_cache

# =========================================================
# STANDALONE FUNCTIONS (Required by plugins/tools/song.py)
# =========================================================

async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3: return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SHRUTI_API_URL}/download", params={"url": video_id, "type": "audio", "api_key": SHRUTI_API_KEY}, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status != 200: return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072): f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
        return None
    except: return None

async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3: return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SHRUTI_API_URL}/download", params={"url": video_id, "type": "video", "api_key": SHRUTI_API_KEY}, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status != 200: return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072): f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
        return None
    except: return None

# =========================================================
# HELPER FOR ASYNC YT-DLP TO PREVENT EVENT LOOP BLOCKING
# =========================================================
def _extract_formats_sync(link):
    try:
        ytdl_opts = {"quiet": True, "no_warnings": True, "nocheckcertificate": True}
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for f in r.get("formats", []):
                try:
                    if "dash" not in str(f.get("format", "")).lower():
                        formats_available.append({
                            "format": f.get("format"),
                            "filesize": f.get("filesize"),
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "format_note": f.get("format_note"),
                            "yturl": link,
                        })
                except: continue
            return formats_available
    except Exception as e:
        logger.error(f"yt-dlp sync error: {e}")
        return []

# =========================================================
# MAIN YOUTUBE API CLASS
# =========================================================

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _find_file(self, vid_id):
        if not os.path.exists("downloads"): return None
        for ext in ["m4a", "mp4", "mp3", "webm"]:
            filepath = f"downloads/{vid_id}.{ext}"
            if os.path.exists(filepath):
                if os.path.getsize(filepath) > 2048: return os.path.abspath(filepath)
                else:
                    try: os.remove(filepath)
                    except: pass
        return None

    # --- UNIVERSAL UPLOAD ---
    async def _upload_to_cache(self, vid_id, file_path, title, is_video):
        try:
            if not os.path.exists(file_path): return
            db_id = f"{vid_id}_video" if is_video else vid_id
            if await trackdb.find_one({"vid_id": db_id}): return
            logger.info(f"📤 Uploading to Channel: {title}")
            cap = f"**Song:** {title}\n**ID:** `{vid_id}`\n**Saved by:** {app.me.mention}"
            
            msg = None
            if is_video: msg = await app.send_video(PLAYLIST_ID, file_path, caption=cap, supports_streaming=True)
            else: msg = await app.send_audio(PLAYLIST_ID, file_path, caption=cap, title=title)

            if msg:
                await trackdb.update_one({"vid_id": db_id}, {"$set": {"message_id": msg.id, "title": title, "type": "video" if is_video else "audio"}}, upsert=True)
                logger.info(f"✅ Upload Complete (Msg ID: {msg.id}): {title}")
        except Exception as e: logger.error(f"Upload Error: {e}")

    # --- UNIVERSAL RETRIEVAL ---
    async def get_cached_file(self, vid_id: str, is_video: bool = False):
        db_id = f"{vid_id}_video" if is_video else vid_id
        local_path = self._find_file(vid_id)
        if local_path: return local_path

        doc = await trackdb.find_one({"vid_id": db_id})
        if doc and "message_id" in doc:
            message_id = doc['message_id']
            temp_path = os.path.join("downloads", f"{vid_id}.mp4")
            try:
                logger.info(f"🔄 Fetching from Channel (Msg ID: {message_id})")
                cached_msg = await app.get_messages(PLAYLIST_ID, message_id)
                if not cached_msg or cached_msg.empty:
                    logger.warning("Message deleted in channel, cleaning DB.")
                    await trackdb.delete_one({"vid_id": db_id})
                    return None

                media_file = None
                if cached_msg.video: media_file = cached_msg.video.file_id
                elif cached_msg.audio: media_file = cached_msg.audio.file_id
                elif cached_msg.document: media_file = cached_msg.document.file_id
                elif cached_msg.voice: media_file = cached_msg.voice.file_id

                if media_file:
                    file = await app.download_media(media_file, file_name=temp_path)
                    if file and os.path.exists(file) and os.path.getsize(file) > 2048: return file
                if os.path.exists(temp_path): os.remove(temp_path)
            except Exception as e:
                logger.error(f"Cache Retrieval Failed: {e}")
                if os.path.exists(temp_path): os.remove(temp_path)
        return None

    # --- APIs ---
    async def get_api_url(self, vid_id, is_video):
        try:
            if not YT_API_KEY or not YTPROXY: return None
            headers = {"x-api-key": YT_API_KEY}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{YTPROXY}/info/{vid_id}", headers=headers, timeout=10) as resp:
                    if resp.status != 200: return None
                    data = await resp.json()
                    if data.get("status") != "success": return None
                    return data.get("video_url") if is_video else data.get("audio_url")
        except: return None

    async def _shruti_api_download(self, vid_id, is_video):
        ext = "mp4" if is_video else "mp3"
        type_str = "video" if is_video else "audio"
        file_path = os.path.join("downloads", f"{vid_id}.{ext}")
        os.makedirs("downloads", exist_ok=True)
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"🛡️ Using Shruti API for {vid_id}")
                async with session.get(f"{SHRUTI_API_URL}/download", params={"url": vid_id, "type": type_str, "api_key": SHRUTI_API_KEY}, timeout=aiohttp.ClientTimeout(total=600 if is_video else 300)) as response:
                    if response.status != 200: return None
                    async with aiofiles.open(file_path, mode='wb') as f:
                        async for chunk in response.content.iter_chunked(131072): await f.write(chunk)
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 2048: return file_path
        except Exception as e: logger.error(f"Shruti API Failed: {e}")
        return None

    async def _background_process(self, vid_id, link, title, is_video, duration_sec=None):
        if duration_sec is None:
            try:
                dur_str = await self.duration(link)
                duration_sec = time_to_seconds(dur_str)
            except: duration_sec = 0
        if duration_sec > LIMIT_SECONDS: return
        os.makedirs("downloads", exist_ok=True)
        if self._find_file(vid_id): return
        filepath = os.path.join("downloads", f"{vid_id}.mp4")
        try:
            api_direct_url = await self.get_api_url(vid_id, is_video)
            if api_direct_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_direct_url) as resp:
                        if resp.status == 200:
                            async with aiofiles.open(filepath, mode='wb') as f:
                                async for chunk in resp.content.iter_chunked(1048576): await f.write(chunk)
                            if os.path.exists(filepath) and os.path.getsize(filepath) > 2048:
                                await self._upload_to_cache(vid_id, filepath, title, is_video)
                                return 
        except: pass

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid:
            vid_id = link
            link = self.base + link
        else:
            vid_id = link.split('v=')[-1].split('&')[0] if "v=" in link else link.split('/')[-1]
        is_video_request = bool(video or songvideo)

        cached_path = await self.get_cached_file(vid_id, is_video=is_video_request)
        if cached_path: return cached_path, True

        try:
            api_url = await self.get_api_url(vid_id, is_video_request)
            if api_url:
                logger.info(f"🚀 API Stream: {title or vid_id}")
                asyncio.create_task(self._background_process(vid_id, link, title or vid_id, is_video_request))
                return api_url, True
        except Exception as e: logger.error(f"Primary API Failed: {e}")

        logger.warning(f"⚠️ Switching to Shruti API for {vid_id}...")
        fallback_file = await self._shruti_api_download(vid_id, is_video_request)
        if fallback_file:
            logger.info(f"✅ Shruti Download Success: {title or vid_id}")
            await self._upload_to_cache(vid_id, fallback_file, title or vid_id, is_video_request)
            return fallback_file, True
        
        logger.error("❌ All APIs Failed.")
        return None, False

    # =========================================================
    # 🛡️ BULLETPROOF METADATA UTILS (Fixes "Failed to process query")
    # =========================================================
    
    async def _safe_search(self, query: str, limit: int = 1):
        try:
            search = VideosSearch(query, limit=limit)
            res = (await search.next()).get("result", [])
            if res: return res
        except: pass
        try:
            search = CustomSearch(query=query, searchPreferences="EgIYAw==", limit=limit)
            res = (await search.next()).get("result", [])
            if res: return res
        except: pass
        return []

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK: return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=1)
        if not res: raise ValueError("No search results")
        result = res[0]
        title = result.get("title", "Unknown")
        duration_min = result.get("duration", "0:00")
        vidid = result.get("id", "")
        thumbnails = result.get("thumbnails", [{"url": ""}])
        thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
        try: duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        except: duration_sec = 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=1)
        return res[0].get("title", "Unknown") if res else None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=1)
        return res[0].get("duration", "0:00") if res else "0:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=1)
        if res:
            thumbs = res[0].get("thumbnails", [{"url": ""}])
            return thumbs[0]["url"].split("?")[0] if thumbs else ""
        return ""

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        try:
            plist = await Playlist.get(link)
            videos = plist.get("videos") or []
            ids = [data.get("id") for data in videos[:limit] if data.get("id")]
            return ids
        except:
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=1)
        if not res: raise ValueError("No search results")
        result = res[0]
        title = result.get("title", "Unknown")
        duration_min = result.get("duration", "0:00")
        vidid = result.get("id", "")
        yturl = result.get("link", link)
        thumbnails = result.get("thumbnails", [{"url": ""}])
        thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
        return {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            loop = asyncio.get_event_loop()
            formats_available = await loop.run_in_executor(None, _extract_formats_sync, link)
            return formats_available, link
        except Exception as e:
            logger.error(f"Formats error: {e}")
            return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        res = await self._safe_search(link, limit=10)
        if not res: raise ValueError("No search results")
        result = res[query_type] if query_type < len(res) else res[0]
        title = result.get("title", "Unknown")
        duration_min = result.get("duration", "0:00")
        vidid = result.get("id", "")
        thumbnails = result.get("thumbnails", [{"url": ""}])
        thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
        return title, duration_min, thumbnail, vidid

YouTube = YouTubeAPI()
