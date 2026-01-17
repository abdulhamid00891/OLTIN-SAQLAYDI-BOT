import os
import re
import asyncio
import aiohttp
import yt_dlp
from config import DOWNLOAD_PATH, MAX_FILE_SIZE, SUPPORTED_PLATFORMS

# Downloads papkasini yaratish
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Cobalt API - Instagram, TikTok uchun
COBALT_API = "https://api.cobalt.tools/api/json"

def is_valid_url(url: str) -> bool:
    """URL to'g'ri platformadan ekanligini tekshirish"""
    url_lower = url.lower()
    return any(platform in url_lower for platform in SUPPORTED_PLATFORMS)

def extract_url(text: str) -> str | None:
    """Matndan URL ajratib olish"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None

def get_platform(url: str) -> str:
    """URL dan platformani aniqlash"""
    url_lower = url.lower()
    if 'instagram.com' in url_lower:
        return 'instagram'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    return 'unknown'

async def download_with_cobalt(url: str, user_id: int) -> dict:
    """Cobalt API orqali yuklab olish (Instagram, TikTok uchun yaxshi)"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'url': url,
        'vCodec': 'h264',
        'vQuality': '720',
        'aFormat': 'mp3',
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(COBALT_API, json=payload, headers=headers) as response:
                if response.status != 200:
                    return {'success': False, 'error': 'Cobalt API xatosi'}
                
                data = await response.json()
                
                if data.get('status') == 'error':
                    return {'success': False, 'error': data.get('text', 'Xatolik')}
                
                # Video URL olish
                video_url = data.get('url')
                if not video_url:
                    return {'success': False, 'error': 'Video URL topilmadi'}
                
                # Videoni yuklab olish
                async with session.get(video_url) as video_response:
                    if video_response.status != 200:
                        return {'success': False, 'error': 'Video yuklab olishda xatolik'}
                    
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await video_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                
                file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                
                return {
                    'success': True,
                    'file_path': output_path,
                    'title': 'Video',
                    'duration': 0,
                    'file_size': file_size,
                    'is_large': file_size > MAX_FILE_SIZE
                }
    except Exception as e:
        print(f"Cobalt xatolik: {e}")
        return {'success': False, 'error': str(e)}

async def download_with_ytdlp(url: str, user_id: int) -> dict:
    """yt-dlp orqali yuklab olish (YouTube uchun yaxshi)"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    
    # Oldingi faylni o'chirish
    if os.path.exists(output_path):
        os.remove(output_path)
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'socket_timeout': 30,
        'retries': 3,
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            if os.path.exists(output_path):
                file_path = output_path
            else:
                file_path = ydl.prepare_filename(info)
                if not file_path.endswith('.mp4'):
                    file_path = file_path.rsplit('.', 1)[0] + '.mp4'
            
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            return {
                'success': True,
                'file_path': file_path,
                'title': info.get('title', 'Video'),
                'duration': info.get('duration', 0),
                'file_size': file_size,
                'is_large': file_size > MAX_FILE_SIZE
            }
    except Exception as e:
        print(f"yt-dlp xatolik: {e}")
        return {'success': False, 'error': str(e)}

async def download_video(url: str, user_id: int) -> dict:
    """Video yuklab olish - platforma asosida metod tanlash"""
    platform = get_platform(url)
    
    # Instagram va TikTok uchun Cobalt API
    if platform in ['instagram', 'tiktok']:
        result = await download_with_cobalt(url, user_id)
        if result['success']:
            return result
        # Cobalt ishlamasa, yt-dlp bilan urinib ko'rish
        print(f"Cobalt ishlamadi, yt-dlp bilan urinilmoqda...")
    
    # YouTube va boshqalar uchun yt-dlp
    result = await download_with_ytdlp(url, user_id)
    if result['success']:
        return result
    
    # yt-dlp ishlamasa, Cobalt bilan urinib ko'rish
    if platform not in ['instagram', 'tiktok']:
        cobalt_result = await download_with_cobalt(url, user_id)
        if cobalt_result['success']:
            return cobalt_result
    
    return result

async def download_audio(url: str, user_id: int) -> dict:
    """Faqat audio (MP3) yuklab olish"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_audio.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            if os.path.exists(output_path):
                file_path = output_path
            else:
                base_path = output_path.replace('.mp3', '')
                for ext in ['.mp3', '.m4a', '.webm']:
                    if os.path.exists(base_path + ext):
                        file_path = base_path + ext
                        break
                else:
                    file_path = output_path
            
            return {
                'success': True,
                'file_path': file_path,
                'title': info.get('title', 'Audio'),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        print(f"Audio download xatolik: {e}")
        return {'success': False, 'error': str(e)}

def cleanup_file(file_path: str):
    """Vaqtinchalik faylni o'chirish"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Cleanup xatolik: {e}")
