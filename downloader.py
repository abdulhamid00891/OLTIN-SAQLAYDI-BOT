import os
import re
import asyncio
import aiohttp
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
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    return 'unknown'

def get_content_type(url: str) -> str:
    """Kontent turini aniqlash"""
    url_lower = url.lower()
    if '/reel/' in url_lower or '/reels/' in url_lower:
        return 'reel'
    elif '/stories/' in url_lower or '/story/' in url_lower:
        return 'story'
    elif '/shorts/' in url_lower:
        return 'short'
    elif '/p/' in url_lower:
        return 'post'
    return 'video'

async def download_instagram_media(url: str, user_id: int) -> dict:
    """Instagram uchun - Reels, Stories, Posts, Photos"""
    video_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    photo_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_photo.jpg")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    content_type = get_content_type(url)
    print(f"Instagram kontent turi: {content_type}")
    
    async with aiohttp.ClientSession() as session:
        # API 1: igdownloader
        try:
            api_url = "https://igdownloader.app/api/v1/instagram"
            payload = {'url': url}
            
            async with session.post(api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    media_list = data.get('media', []) or data.get('data', []) or [data]
                    
                    for media in media_list:
                        media_url = media.get('url') or media.get('video_url') or media.get('download_url')
                        media_type = media.get('type', 'video')
                        
                        if media_url:
                            async with session.get(media_url, headers=headers) as media_resp:
                                if media_resp.status == 200:
                                    is_photo = 'image' in media_type or media_url.endswith(('.jpg', '.jpeg', '.png', '.webp'))
                                    output_path = photo_path if is_photo else video_path
                                    
                                    with open(output_path, 'wb') as f:
                                        async for chunk in media_resp.content.iter_chunked(8192):
                                            f.write(chunk)
                                    
                                    file_size = os.path.getsize(output_path)
                                    if file_size > 5000:
                                        return {
                                            'success': True,
                                            'file_path': output_path,
                                            'title': f'Instagram {content_type.capitalize()}',
                                            'duration': 0,
                                            'file_size': file_size,
                                            'is_large': file_size > MAX_FILE_SIZE,
                                            'is_photo': is_photo
                                        }
        except Exception as e:
            print(f"igdownloader xatolik: {e}")
        
        # API 2: saveig
        try:
            api2_url = f"https://api.saveig.app/api/v1/media?url={url}"
            async with session.get(api2_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get('items', []) or [data]
                    
                    for item in items:
                        media_url = item.get('url') or item.get('video_url') or item.get('thumbnail')
                        if media_url:
                            is_photo = item.get('type') == 'image' or '.jpg' in media_url
                            output_path = photo_path if is_photo else video_path
                            
                            async with session.get(media_url, headers=headers) as media_resp:
                                if media_resp.status == 200:
                                    with open(output_path, 'wb') as f:
                                        async for chunk in media_resp.content.iter_chunked(8192):
                                            f.write(chunk)
                                    
                                    file_size = os.path.getsize(output_path)
                                    if file_size > 5000:
                                        return {
                                            'success': True,
                                            'file_path': output_path,
                                            'title': f'Instagram {content_type.capitalize()}',
                                            'duration': 0,
                                            'file_size': file_size,
                                            'is_large': file_size > MAX_FILE_SIZE,
                                            'is_photo': is_photo
                                        }
        except Exception as e:
            print(f"saveig xatolik: {e}")
        
        # API 3: FastDL uslubi
        try:
            fastdl_url = "https://fastdl.app/api/convert"
            form_data = aiohttp.FormData()
            form_data.add_field('url', url)
            
            async with session.post(fastdl_url, data=form_data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    media_url = data.get('url') or data.get('video') or data.get('image')
                    
                    if media_url:
                        is_photo = 'image' in str(data.get('type', '')) or media_url.endswith(('.jpg', '.jpeg', '.png'))
                        output_path = photo_path if is_photo else video_path
                        
                        async with session.get(media_url, headers=headers) as media_resp:
                            if media_resp.status == 200:
                                with open(output_path, 'wb') as f:
                                    async for chunk in media_resp.content.iter_chunked(8192):
                                        f.write(chunk)
                                
                                file_size = os.path.getsize(output_path)
                                if file_size > 5000:
                                    return {
                                        'success': True,
                                        'file_path': output_path,
                                        'title': f'Instagram {content_type.capitalize()}',
                                        'duration': 0,
                                        'file_size': file_size,
                                        'is_large': file_size > MAX_FILE_SIZE,
                                        'is_photo': is_photo
                                    }
        except Exception as e:
            print(f"FastDL xatolik: {e}")
    
    return {'success': False, 'error': 'Instagram yuklab olinmadi'}

async def download_tiktok_media(url: str, user_id: int) -> dict:
    """TikTok uchun yuklovchi"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    async with aiohttp.ClientSession() as session:
        # TikWM API
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('code') == 0:
                        video_data = data.get('data', {})
                        video_url = video_data.get('play') or video_data.get('hdplay') or video_data.get('wmplay')
                        
                        if video_url:
                            async with session.get(video_url, headers=headers) as video_resp:
                                if video_resp.status == 200:
                                    with open(output_path, 'wb') as f:
                                        async for chunk in video_resp.content.iter_chunked(8192):
                                            f.write(chunk)
                                    
                                    file_size = os.path.getsize(output_path)
                                    if file_size > 10000:
                                        return {
                                            'success': True,
                                            'file_path': output_path,
                                            'title': video_data.get('title', 'TikTok Video')[:50],
                                            'duration': video_data.get('duration', 0),
                                            'file_size': file_size,
                                            'is_large': file_size > MAX_FILE_SIZE,
                                            'is_photo': False
                                        }
        except Exception as e:
            print(f"TikWM xatolik: {e}")
        
        # Musicaldown API
        try:
            api2_url = "https://api.musicaldown.com/download"
            payload = {'url': url}
            async with session.post(api2_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    video_url = data.get('video_url') or data.get('url')
                    if video_url:
                        async with session.get(video_url, headers=headers) as video_resp:
                            if video_resp.status == 200:
                                with open(output_path, 'wb') as f:
                                    async for chunk in video_resp.content.iter_chunked(8192):
                                        f.write(chunk)
                                
                                file_size = os.path.getsize(output_path)
                                if file_size > 10000:
                                    return {
                                        'success': True,
                                        'file_path': output_path,
                                        'title': 'TikTok Video',
                                        'duration': 0,
                                        'file_size': file_size,
                                        'is_large': file_size > MAX_FILE_SIZE,
                                        'is_photo': False
                                    }
        except Exception as e:
            print(f"Musicaldown xatolik: {e}")
    
    return {'success': False, 'error': 'TikTok yuklab olinmadi'}

async def download_with_ytdlp(url: str, user_id: int) -> dict:
    """yt-dlp - YouTube Shorts, Facebook, Twitter va boshqalar"""
    output_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video.mp4")
    
    if os.path.exists(output_path):
        os.remove(output_path)
    
    content_type = get_content_type(url)
    
    ydl_opts = {
        'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'socket_timeout': 60,
        'retries': 5,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web']},
        },
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
            
            if file_size < 1000:
                return {'success': False, 'error': 'Fayl yuklanmadi'}
            
            title = info.get('title', 'Video')
            if content_type == 'short':
                title = f"YouTube Shorts: {title[:40]}"
            
            return {
                'success': True,
                'file_path': file_path,
                'title': title[:50],
                'duration': info.get('duration', 0),
                'file_size': file_size,
                'is_large': file_size > MAX_FILE_SIZE,
                'is_photo': False
            }
    except Exception as e:
        print(f"yt-dlp xatolik: {e}")
        return {'success': False, 'error': str(e)}

async def download_video(url: str, user_id: int) -> dict:
    """Asosiy yuklovchi - barcha platformalar"""
    
    # Eski fayllarni o'chirish
    for ext in ['.mp4', '.jpg', '.png']:
        path = os.path.join(DOWNLOAD_PATH, f"{user_id}_video{ext}")
        if os.path.exists(path):
            os.remove(path)
        path = os.path.join(DOWNLOAD_PATH, f"{user_id}_photo{ext}")
        if os.path.exists(path):
            os.remove(path)
    
    platform = get_platform(url)
    content_type = get_content_type(url)
    print(f"Platforma: {platform}, Turi: {content_type}")
    
    # Instagram - Reels, Stories, Posts, Photos
    if platform == 'instagram':
        print("Instagram API bilan urinilmoqda...")
        result = await download_instagram_media(url, user_id)
        if result['success']:
            return result
        print("Instagram API ishlamadi, yt-dlp sinash...")
    
    # TikTok
    elif platform == 'tiktok':
        print("TikTok API bilan urinilmoqda...")
        result = await download_tiktok_media(url, user_id)
        if result['success']:
            return result
        print("TikTok API ishlamadi, yt-dlp sinash...")
    
    # YouTube, Facebook, Twitter va boshqalar - yt-dlp
    print("yt-dlp bilan yuklanmoqda...")
    result = await download_with_ytdlp(url, user_id)
    
    if not result['success'] and platform in ['instagram', 'tiktok']:
        result['error'] = f"{platform.capitalize()} video/rasm topilmadi yoki maxfiy"
    
    return result

async def download_audio(url: str, user_id: int) -> dict:
    """Audio (MP3) yuklab olish"""
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
                for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                    if os.path.exists(base_path + ext):
                        file_path = base_path + ext
                        break
                else:
                    file_path = output_path
            
            return {
                'success': True,
                'file_path': file_path,
                'title': info.get('title', 'Audio')[:50],
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        print(f"Audio xatolik: {e}")
        return {'success': False, 'error': str(e)}

def cleanup_file(file_path: str):
    """Faylni o'chirish"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Cleanup xatolik: {e}")
