PIPED_INSTANCE = "https://piped.video"

def convert_to_piped(url):
    if "youtu.be/" in url:
        video_id = url.split("/")[-1].split("?")[0]
        return f"{PIPED_INSTANCE}/watch?v={video_id}"

    if "youtube.com/watch?v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
        return f"{PIPED_INSTANCE}/watch?v={video_id}"

    return url


async def download_audio(update, context):

    url = update.message.text.strip()

    url = convert_to_piped(url)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3"
            },
            {
                "key": "EmbedThumbnail"
            },
            {
                "key": "FFmpegMetadata"
            }
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
