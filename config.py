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
    "facebook.com", "fb.watch",
    "twitter.com", "x.com"
]

# Xabarlar (O'zbek tilida) - Mukammal dizayn
MESSAGES = {
    "welcome": """
╔══════════════════════════════╗
   🎬 <b>VIDEO YUKLOVCHI BOT</b>
╚══════════════════════════════╝

Assalomu alaykum, <b>{name}</b>! 👋

📥 Men quyidagi platformalardan video yuklab beraman:

   ▫️ YouTube
   ▫️ TikTok
   ▫️ Instagram
   ▫️ Facebook

━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 <b>Botdan foydalanish uchun 
     kanallarimizga obuna bo'ling:</b>
""",

    "check_subscription": "✅ Tekshirish",
    
    "not_subscribed": """
⚠️ <b>Diqqat!</b>

Siz hali barcha kanallarga obuna bo'lmagansiz!

Iltimos, quyidagi kanallarga obuna bo'ling:
""",

    "subscribed": """
╔══════════════════════════════╗
   ✅ <b>TAYYOR!</b>
╚══════════════════════════════╝

🎉 Ajoyib! Endi botdan foydalanishingiz mumkin.

📥 <b>Qanday foydalanish:</b>
▫️ Menga video havolasini yuboring
▫️ Men uni yuklab sizga jo'nataman

🌐 <b>Qo'llab-quvvatlanadigan saytlar:</b>
YouTube • TikTok • Instagram • Facebook
""",

    "send_url": "🔗 Video havolasini yuboring:",
    
    "downloading": """
⏳ <b>Yuklab olinmoqda...</b>

┌─────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────┘

Iltimos, kuting...
""",

    "download_complete": "✅ Video tayyor!",
    
    "download_error": """
❌ <b>Xatolik yuz berdi!</b>

Mumkin bo'lgan sabablar:
▫️ Video maxfiy yoki o'chirilgan
▫️ Havola noto'g'ri
▫️ Platforma cheklovi

💡 <b>Maslahat:</b> Boshqa video bilan sinab ko'ring.
""",

    "invalid_url": """
⚠️ <b>Noto'g'ri havola!</b>

Iltimos, quyidagi platformalardan havola yuboring:
▫️ YouTube
▫️ TikTok  
▫️ Instagram
▫️ Facebook
""",

    "file_too_large": """
⚠️ <b>Video hajmi katta!</b>

Video 50MB dan ortiq. Siqilgan versiya yuklanmoqda...
""",

    "saved_to_playlist": "✅ Video playlistga saqlandi!",
    
    "playlist_empty": "📂 Sizning playlistingiz hozircha bo'sh.",
    
    "playlist_header": """
╔══════════════════════════════╗
   📂 <b>SIZNING PLAYLISTINGIZ</b>
╚══════════════════════════════╝
""",

    "help": """
╔══════════════════════════════╗
   ❓ <b>YORDAM</b>
╚══════════════════════════════╝

📥 <b>Qanday foydalanish:</b>
1️⃣ Kanallarga obuna bo'ling
2️⃣ Video havolasini yuboring  
3️⃣ Videoni yuklab oling!

🌐 <b>Qo'llab-quvvatlanadigan saytlar:</b>
▫️ YouTube
▫️ TikTok
▫️ Instagram
▫️ Facebook

📂 <b>Buyruqlar:</b>
▫️ /start - Botni boshlash
▫️ /playlist - Saqlangan videolar
▫️ /help - Yordam

━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 <b>Muammo bo'lsa:</b>
Kanallarimizga murojaat qiling!
""",

    "video_caption": """
🎬 <b>{title}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 @OLTIN_SAQLAYDI_BOT orqali yuklandi
""",

    "audio_caption": """
🎵 <b>{title}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 @OLTIN_SAQLAYDI_BOT orqali yuklandi
"""
}
