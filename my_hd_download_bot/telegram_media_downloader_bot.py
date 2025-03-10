import os
import subprocess
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram.error import TelegramError

# API Token for the bot (obtained from @BotFather)
API_TOKEN = '7596113261:AAG02IDEfJX0mhioEUTEqHdqdxLrzdEkNT4'

# Temporary download folder (adjust as needed)
TEMP_DOWNLOAD_FOLDER = r'/tmp/'

def ffmpeg_installed():
    """Check if ffmpeg is installed by running 'ffmpeg -version'."""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except Exception:
        return False

# Function to handle real-time download progress
async def download_progress(d, message):
    try:
        if d['status'] == 'downloading':
            percentage = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
            # Update progress every 10% increments
            if int(percentage) % 10 == 0:
                try:
                    await message.edit_text(f"Download progress: {percentage:.2f}%")
                except Exception as e:
                    # Log the error but continue
                    print("Progress update error:", e)
        elif d['status'] == 'finished':
            try:
                await message.edit_text("Download complete, processing file...")
            except Exception as e:
                print("Progress update error:", e)
    except Exception as e:
        print("Error in download_progress:", e)

# Function to download videos or audios (YouTube, Twitter/X, and TikTok)
async def download_video(url, destination_folder, message, media_format="video"):
    try:
        if media_format == "audio":
            format_type = 'bestaudio/best'
            ext = 'mp3'
        else:
            if not ffmpeg_installed():
                await message.edit_text("Error: ffmpeg is not installed. Please install ffmpeg to merge video and audio streams.")
                return False
            format_type = 'bestvideo+bestaudio/best'
            ext = 'mp4'
        
        options = {
            'outtmpl': f'{destination_folder}/%(id)s.%(ext)s',
            'format': format_type,
            'restrictfilenames': True,
            'progress_hooks': [lambda d: asyncio.create_task(download_progress(d, message))],
            'merge_output_format': ext,
            'postprocessor_args': ['-c:a', 'aac', '-b:a', '128k'],
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error during download: {e}")
        return False

# Function to handle the /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Send a YouTube, Twitter/X, or TikTok link using /download <url>.\n'
        'The file will be downloaded, sent, and then deleted.'
    )

# Function to handle the /download command
async def download(update: Update, context: CallbackContext):
    try:
        message_text = update.message.text
        # Check for valid URL from supported platforms
        if any(domain in message_text for domain in [
            "https://www.youtube.com/", "https://youtu.be/",
            "https://twitter.com/", "https://x.com/",
            "https://www.tiktok.com/"
        ]):
            params = message_text.split(" ")
            url = params[1]
            media_format = "video" if len(params) < 3 or params[2].lower() != "audio" else "audio"
            destination_folder = TEMP_DOWNLOAD_FOLDER

            # Send initial status message
            message = await update.message.reply_text(f'Starting the {media_format} download from: {url}')

            success_download = await download_video(url, destination_folder, message, media_format)
            if not success_download:
                await message.edit_text('Error during the download. Please try again later.')
                return

            # Locate the most recent file in the destination folder
            video_filename = max(
                [os.path.join(destination_folder, f) for f in os.listdir(destination_folder)],
                key=os.path.getctime
            )

            await message.edit_text(f'Sending the {media_format}...')
            try:
                await update.message.reply_video(video=open(video_filename, 'rb'))
            except TelegramError as e:
                await message.edit_text(f'Error sending the file: {e}')
                print("Error sending the file:", e)
            finally:
                # Delete the file after sending it
                if os.path.exists(video_filename):
                    os.remove(video_filename)
        else:
            await update.message.reply_text('Please provide a valid YouTube, Twitter/X, or TikTok URL.')
    except Exception as e:
        await update.message.reply_text('An unexpected error occurred. Please try again later.')
        print("Error in the download function:", e)

def main():
    application = ApplicationBuilder().token(API_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('download', download))
    application.run_polling()

if __name__ == "__main__":
    main()
