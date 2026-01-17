import os

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "8536538698:AAEccXb03s8FYdotZI93RVcyjLaAl321Rz8")

# Majburiy obuna bo'lishi kerak bo'lgan kanallar
REQUIRED_CHANNELS = [
    "@oltiariq_999_magazin_oqboyra",
    "@raqamlar_nomer_beeline_uzmobile"
]

# Yuklab olish papkasi
DOWNLOAD_PATH = os.path.join(os.path.dirname(__file__), "downloads")

# Maksimal fayl hajmi (bytes) - 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Database fayli
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "bot_database.db")

# Qo'llab-quvvatlanadigan platformalar
SUPPORTED_PLATFORMS = [
    "youtube.com", "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com", "fb.watch"
]

# Xabarlar (O'zbek tilida)
MESSAGES = {
    "welcome": "Assalomu alaykum, {name}! 👋\n\n🎬 Men video yuklab oluvchi botman.\n\nBotdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
    "check_subscription": "✅ Obunani tekshirish",
    "not_subscribed": "❌ Siz hali barcha kanallarga obuna bo'lmagansiz!\n\nIltimos, quyidagi kanallarga obuna bo'ling:",
    "subscribed": "✅ Ajoyib! Siz barcha kanallarga obuna bo'lgansiz!\n\n🔗 Endi menga YouTube, TikTok, Instagram yoki Facebook video havolasini yuboring.",
    "send_url": "🔗 Video havolasini yuboring:",
    "downloading": "⏳ Video yuklab olinmoqda... Iltimos, kuting.",
    "download_complete": "✅ Video tayyor!",
    "download_error": "❌ Xatolik yuz berdi. Iltimos, havolani tekshirib qaytadan urinib ko'ring.",
    "invalid_url": "❌ Noto'g'ri havola. Iltimos, YouTube, TikTok, Instagram yoki Facebook havolasini yuboring.",
    "file_too_large": "⚠️ Video hajmi juda katta (50MB dan ortiq). Siqilgan versiya yuklanmoqda...",
    "saved_to_playlist": "✅ Video playlistga saqlandi!",
    "playlist_empty": "📂 Sizning playlistingiz bo'sh.",
    "playlist_header": "📂 Sizning playlistingiz:",
    "help": """🎬 **Video Downloader Bot**

📌 **Qanday foydalanish:**
1. Kanallarga obuna bo'ling
2. Video havolasini yuboring
3. Videoni yuklab oling!

🔗 **Qo'llab-quvvatlanadigan platformalar:**
• YouTube
• TikTok
• Instagram
• Facebook

📂 **Buyruqlar:**
/start - Botni boshlash
/playlist - Saqlangan videolar
/help - Yordam"""
}
