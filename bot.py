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

# التوكن محفوظ في GitHub Secrets باسم BOT_TOKEN
BOT_TOKEN = os.environ['BOT_TOKEN']

# رابط Invidious الذي سنستخدمه
INVIDIOUS_HOST = 'https://invidious.nerdvpn.de'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🎵 مرحبًا!\\n\\n'
        'أرسل رابط فيديو من Invidious وسأحوّله إلى MP3.'
    )


def normalize_url(url: str) -> str:
    """
    يقبل روابط Invidious أو YouTube ويحاول تحويلها إلى Invidious.
    """
    url = url.strip()

    # إذا كان الرابط من Invidious نتركه كما هو
    if 'invidious.' in url:
        return url

    # تحويل youtu.be إلى Invidious
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
        return f'{INVIDIOUS_HOST}/watch?v={video_id}'

    # تحويل youtube.com إلى Invidious
    if 'youtube.com/watch' in url and 'v=' in url:
        video_id = url.split('v=')[-1].split('&')[0]
        return f'{INVIDIOUS_HOST}/watch?v={video_id}'

    return url


async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    original_url = update.message.text.strip()
    url = normalize_url(original_url)

    # تحقق من الرابط
    if 'invidious.' not in url:
        await update.message.reply_text(
            '❌ أرسل رابط Invidious صحيح.\\n\\n'
            'مثال:\\n'
            'https://invidious.nerdvpn.de/watch?v=XXXXXXXX'
        )
        return

    status = await update.message.reply_text(
        '⏳ جاري تحميل الفيديو وتحويله إلى MP3...'
    )

    os.makedirs('downloads', exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'writethumbnail': True,
        'noplaylist': True,
        'quiet': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
            },
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # استخراج المعلومات وتنزيل الملف
            info = ydl.extract_info(url, download=True)

            video_id = info.get('id')
            title = info.get('title', 'Audio')
            uploader = info.get('uploader', 'Invidious')

        mp3_file = f'downloads/{video_id}.mp3'

        if not os.path.exists(mp3_file):
            await status.edit_text('❌ لم يتم إنشاء ملف MP3.')
            return

        await status.edit_text('📤 جاري إرسال الملف...')

        with open(mp3_file, 'rb') as audio:

            await update.message.reply_audio(
                audio=audio,
                title=title[:64],
                performer=uploader[:64],
                caption=f'🎵 {title}',
            )

        # حذف الملفات المؤقتة
        for file in glob.glob(f'downloads/{video_id}.*'):
            try:
                os.remove(file)
            except Exception:
                pass

        await status.delete()

    except Exception as e:

        print('ERROR:', e)

        await status.edit_text(
            '❌ حدث خطأ أثناء التحميل من Invidious.\\n\\n'
            'قد يكون الفيديو غير متاح أو أن واجهة Invidious لا تستطيع الوصول إليه حاليًا.'
        )


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            download_audio,
        )
    )

    print('Bot is running...')

    app.run_polling()


if __name__ == '__main__':
    main()
