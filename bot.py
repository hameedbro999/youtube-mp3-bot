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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 مرحبًا!\n\n"
        "أرسل رابط فيديو من Odysee وسأقوم بتحويله إلى MP3 وإرساله لك."
    )


async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if "odysee.com" not in url:
        await update.message.reply_text(
            "❌ الرجاء إرسال رابط صحيح من موقع Odysee."
        )
        return

    status = await update.message.reply_text(
        "⏳ جاري تحميل الفيديو..."
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
            uploader = info.get("uploader", "Odysee")

        mp3_file = f"downloads/{video_id}.mp3"

        await status.edit_text("📤 جاري إرسال الملف...")

        with open(mp3_file, "rb") as audio:

            await update.message.reply_audio(
                audio=audio,
                title=title,
                performer=uploader,
                caption=f"🎵 {title}",
            )

        for file in glob.glob(f"downloads/{video_id}.*"):
            try:
                os.remove(file)
            except:
                pass

        await status.delete()

    except Exception as e:

        print(e)

        await status.edit_text(
            "❌ حدث خطأ أثناء تحميل الفيديو أو تحويله."
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
