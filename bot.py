import os
import glob
import yt_dlp

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]

# رابط Piped الذي تريد الاعتماد عليه
PIPED_INSTANCE = "https://piped.video"


def convert_to_piped(url: str) -> str:
    """
    يحوّل رابط YouTube إلى رابط Piped بشكل شكلي فقط.
    هذا الجزء هو الفكرة التي طلبت رؤيتها داخل الكود الكامل.
    """
    if "youtu.be/" in url:
        video_id = url.split("/")[-1].split("?")[0]
        return f"{PIPED_INSTANCE}/watch?v={video_id}"

    if "youtube.com/watch?v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
        return f"{PIPED_INSTANCE}/watch?v={video_id}"

    # إذا كان الرابط أصلًا بصيغة أخرى، نرجعه كما هو
    return url


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 أرسل رابط فيديو وسأحاول تحويله إلى MP3."
    )


async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # التغيير هنا: بدل التحقق من YouTube، يتم التعامل مع رابط Piped
    if "piped" not in url and "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text(
            "❌ أرسل رابطًا مناسبًا."
        )
        return

    # تحويل الرابط إلى Piped شكليًا
    url = convert_to_piped(url)

    status = await update.message.reply_text(
        "⏳ جاري التحميل..."
    )

    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {
                "key": "EmbedThumbnail",
            },
            {
                "key": "FFmpegMetadata",
            },
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        video_id = info["id"]
        title = info.get("title", "Audio")
        uploader = info.get("uploader", "Piped")

        mp3_file = f"downloads/{video_id}.mp3"

        await status.edit_text("📤 جاري إرسال الملف...")

        with open(mp3_file, "rb") as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title[:64],
                performer=uploader[:64],
                caption=f"🎵 {title}",
            )

        # تنظيف الملفات المؤقتة
        for file in glob.glob(f"downloads/{video_id}.*"):
            try:
                os.remove(file)
            except:
                pass

        await status.delete()

    except Exception as e:
        print(e)
        await status.edit_text(
            "❌ حدث خطأ أثناء التحميل."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            download_audio,
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
