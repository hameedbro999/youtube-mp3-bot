import os
import yt_dlp

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


BOT_TOKEN = os.environ["BOT_TOKEN"]


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🎵 أرسل رابط يوتيوب"
    )


async def download_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    url = update.message.text.strip()

    if (
        "youtube.com" not in url
        and "youtu.be" not in url
    ):

        await update.message.reply_text(
            "❌ أرسل رابط يوتيوب صحيح"
        )

        return


    status = await update.message.reply_text(
        "⏳ جاري التحميل..."
    )


    os.makedirs(
        "downloads",
        exist_ok=True
    )


    options = {

        "format": "bestaudio/best",

        "outtmpl":
        "downloads/%(id)s.%(ext)s",

        "writethumbnail": True,

        "postprocessors": [

            {

                "key":
                "FFmpegExtractAudio",

                "preferredcodec":
                "mp3",

                "preferredquality":
                "192"

            },

            {

                "key":
                "EmbedThumbnail"

            },

            {

                "key":
                "FFmpegMetadata"

            }

        ]

    }


    try:

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )


        video_id = info["id"]

        title = info.get(
            "title",
            "Audio"
        )


        filename = (
            f"downloads/{video_id}.mp3"
        )


        await status.edit_text(
            "📤 جاري إرسال الملف..."
        )


        with open(
            filename,
            "rb"
        ) as audio:

            await update.message.reply_audio(

                audio=audio,

                title=title[:64],

                caption=(
                    f"🎵 {title}"
                )

            )


        os.remove(filename)


        await status.delete()


    except Exception as error:

        print(error)


        await status.edit_text(

            "❌ حدث خطأ أثناء التحميل"

        )


def main():

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    app.add_handler(

        CommandHandler(
            "start",
            start
        )

    )


    app.add_handler(

        MessageHandler(

            filters.TEXT
            & ~filters.COMMAND,

            download_audio

        )

    )


    app.run_polling()


if __name__ == "__main__":

    main()
