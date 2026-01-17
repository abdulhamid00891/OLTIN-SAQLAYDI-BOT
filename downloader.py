import os
import re
import asyncio
import yt_dlp
from config import DOWNLOAD_PATH, MAX_FILE_SIZE, SUPPORTED_PLATFORMS

# Downloads papkasini yaratish
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def is_valid_url(url: str) -> bool:
    """URL to'g'ri platformadan ekanligini tekshirish"""
    url_lower = url.lower()
    return any(platform in url_lower for platform in SUPPORTED_PLATFORMS)

def extract_url(text: str) -> str | None:
    """Matndan URL ajratib olish"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None

async def get_video_info(url: str) -> dict | None:
    """Video ma'lumotlarini olish"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            return {
                'title': info.get('title', 'Video'),
                'duration': info.get('duration', 0),
                'filesize': info.get('filesize') or info.get('filesize_approx', 0),
                'thumbnail': info.get('thumbnail'),
                'url': url
            }
    except Exception as e:
        print(f"Video info xatolik: {e}")
        return None

async def download_video(url: str, user_id: int) -> dict:
    """Video yuklab olish"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            # Haqiqiy fayl nomini olish
            if os.path.exists(output_path):
                file_path = output_path
            else:
                # yt-dlp ba'zan boshqa nom beradi
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
        print(f"Download xatolik: {e}")
        return {
            'success': False,
            'error': str(e)
        }

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
            
            # MP3 fayl nomini topish
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
        return {
            'success': False,
            'error': str(e)
        }

def cleanup_file(file_path: str):
    """Vaqtinchalik faylni o'chirish"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Cleanup xatolik: {e}")
