# Video Downloader Telegram Bot

YouTube, TikTok, Instagram, Facebook video yuklab oluvchi Telegram bot.

## Xususiyatlar

- ✅ 4 ta platformadan video yuklash
- ✅ Kanal obunasini tekshirish
- ✅ Playlist tizimi
- ✅ Audio (MP3) yuklash

## O'rnatish

1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

2. FFmpeg o'rnatish (audio uchun):
- Windows: https://ffmpeg.org/download.html
- Linux: `sudo apt install ffmpeg`

3. Botni ishga tushirish:
```bash
python bot.py
```

## Railway'ga deploy

1. GitHub'ga push qiling
2. [Railway.app](https://railway.app) ga kiring
3. "New Project" → "Deploy from GitHub"
4. Repository tanlang
5. Environment variables qo'shing:
   - `BOT_TOKEN`: Bot tokeningiz

## Foydalanish

1. `/start` - Botni boshlash
2. Kanallarga obuna bo'ling
3. Video URL yuboring
4. Tugmalardan foydalaning:
   - 📂 Saqlash - Playlistga
   - 🔊 Musiqa - MP3 yuklash
   - 📤 Tarqatish - Forward qilish
