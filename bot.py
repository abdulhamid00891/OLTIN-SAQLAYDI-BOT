import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, REQUIRED_CHANNELS, MESSAGES
from database import init_db, add_user, add_to_playlist, get_playlist
from downloader import is_valid_url, extract_url, download_video, download_audio, cleanup_file

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Foydalanuvchi so'nggi URL'ini saqlash
user_last_url = {}

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Foydalanuvchi barcha kanallarga obuna bo'lganini tekshirish"""
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"Kanal tekshirishda xatolik {channel}: {e}")
            return False
    return True

def get_channel_keyboard():
    """Kanallar tugmalari"""
    keyboard = []
    for i, channel in enumerate(REQUIRED_CHANNELS, 1):
        channel_name = channel.replace('@', '')
        keyboard.append([InlineKeyboardButton(f"📢 {i}-Kanal", url=f"https://t.me/{channel_name}")])
    keyboard.append([InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(keyboard)

def get_video_keyboard(has_url: bool = True):
    """Video tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton("📂 Saqlash", callback_data="save_playlist"),
            InlineKeyboardButton("🔊 Musiqa", callback_data="download_audio"),
        ],
        [InlineKeyboardButton("📤 Tarqatish", switch_inline_query="")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    """Asosiy tugmalar"""
    keyboard = [
        [InlineKeyboardButton("📂 Playlistim", callback_data="show_playlist")],
        [InlineKeyboardButton("❓ Yordam", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start buyrug'i"""
    user = update.effective_user
    await add_user(user.id, user.username, user.first_name)
    
    # Har doim kanallarni ko'rsatish (tekshirishsiz)
    welcome_msg = MESSAGES["welcome"].format(name=user.first_name or "do'stim")
    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_channel_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyrug'i"""
    await update.message.reply_text(
        MESSAGES["help"],
        parse_mode="Markdown"
    )

async def playlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Playlist ko'rish"""
    user_id = update.effective_user.id
    
    playlist = await get_playlist(user_id)
    
    if not playlist:
        await update.message.reply_text(MESSAGES["playlist_empty"])
        return
    
    await update.message.reply_text(MESSAGES["playlist_header"])
    
    for item in playlist[:10]:  # Oxirgi 10 ta
        try:
            if item['file_type'] == 'video':
                await context.bot.send_video(
                    chat_id=user_id,
                    video=item['file_id'],
                    caption=f"📹 {item['title']}"
                )
            else:
                await context.bot.send_audio(
                    chat_id=user_id,
                    audio=item['file_id'],
                    caption=f"🎵 {item['title']}"
                )
        except Exception as e:
            logger.error(f"Playlist yuborishda xatolik: {e}")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """URL qayta ishlash"""
    user = update.effective_user
    text = update.message.text
    
    # URL ajratib olish
    url = extract_url(text)
    if not url or not is_valid_url(url):
        await update.message.reply_text(MESSAGES["invalid_url"])
        return
    
    # URL'ni saqlash
    user_last_url[user.id] = url
    
    # Yuklab olish xabari
    status_msg = await update.message.reply_text(MESSAGES["downloading"])
    
    try:
        # Video yuklab olish
        result = await download_video(url, user.id)
        
        if not result['success']:
            await status_msg.edit_text(MESSAGES["download_error"])
            return
        
        file_path = result['file_path']
        
        # Fayl hajmini tekshirish
        if result.get('is_large'):
            await status_msg.edit_text(MESSAGES["file_too_large"])
        
        # Video yuborish
        with open(file_path, 'rb') as video_file:
            sent_message = await update.message.reply_video(
                video=video_file,
                caption=f"🎬 {result['title']}",
                reply_markup=get_video_keyboard()
            )
        
        # File ID saqlash (keyinroq playlist uchun)
        context.user_data['last_video'] = {
            'file_id': sent_message.video.file_id,
            'title': result['title'],
            'url': url
        }
        
        await status_msg.delete()
        
        # Faylni o'chirish
        cleanup_file(file_path)
        
    except Exception as e:
        logger.error(f"Video yuborishda xatolik: {e}")
        await status_msg.edit_text(MESSAGES["download_error"])

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback tugmalar"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    if data == "check_sub":
        # Tekshirmasdan o'tkazish
        await query.edit_message_text(
            MESSAGES["subscribed"],
            reply_markup=get_main_keyboard()
        )
    
    elif data == "save_playlist":
        # Playlistga saqlash
        last_video = context.user_data.get('last_video')
        if last_video:
            await add_to_playlist(
                user_id=user.id,
                file_id=last_video['file_id'],
                file_type='video',
                title=last_video['title'],
                url=last_video['url']
            )
            await query.answer(MESSAGES["saved_to_playlist"], show_alert=True)
        else:
            await query.answer("❌ Video topilmadi", show_alert=True)
    
    elif data == "download_audio":
        # Audio yuklab olish
        url = user_last_url.get(user.id)
        if not url:
            await query.answer("❌ URL topilmadi", show_alert=True)
            return
        
        await query.answer("🎵 Musiqa yuklanmoqda...")
        status_msg = await query.message.reply_text("⏳ Musiqa yuklab olinmoqda...")
        
        try:
            result = await download_audio(url, user.id)
            
            if result['success']:
                with open(result['file_path'], 'rb') as audio_file:
                    sent_audio = await query.message.reply_audio(
                        audio=audio_file,
                        caption=f"🎵 {result['title']}"
                    )
                
                # Audio file_id saqlash
                context.user_data['last_audio'] = {
                    'file_id': sent_audio.audio.file_id,
                    'title': result['title'],
                    'url': url
                }
                
                await status_msg.delete()
                cleanup_file(result['file_path'])
            else:
                await status_msg.edit_text(MESSAGES["download_error"])
        except Exception as e:
            logger.error(f"Audio xatolik: {e}")
            await status_msg.edit_text(MESSAGES["download_error"])
    
    elif data == "show_playlist":
        # Playlist ko'rsatish
        playlist = await get_playlist(user.id)
        
        if not playlist:
            await query.answer(MESSAGES["playlist_empty"], show_alert=True)
            return
        
        await query.message.reply_text(MESSAGES["playlist_header"])
        
        for item in playlist[:10]:
            try:
                if item['file_type'] == 'video':
                    await context.bot.send_video(
                        chat_id=user.id,
                        video=item['file_id'],
                        caption=f"📹 {item['title']}"
                    )
                else:
                    await context.bot.send_audio(
                        chat_id=user.id,
                        audio=item['file_id'],
                        caption=f"🎵 {item['title']}"
                    )
            except Exception as e:
                logger.error(f"Playlist item xatolik: {e}")
    
    elif data == "help":
        await query.message.reply_text(MESSAGES["help"], parse_mode="Markdown")

async def post_init(application):
    """Bot ishga tushganda"""
    await init_db()
    logger.info("Bot ishga tushdi!")

def main():
    """Asosiy funksiya"""
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Handlers qo'shish
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("playlist", playlist_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Botni ishga tushirish
    logger.info("Bot ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
