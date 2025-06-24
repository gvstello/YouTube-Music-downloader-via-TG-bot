import os
import shutil

from telegram import Update
from telegram.ext import CallbackContext
from services.cache import save_to_cache
from services.downloader import download_audio, download_playlist


downloaded_songs = set()

def set_cache_reference(cache):                                                                                         #
    global downloaded_songs
    downloaded_songs = cache

def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text.strip()
    print(f'[DEBUG] Message text: {message_text}')

    if any(domain in message_text for domain in ['https://youtube.com', 'https://youtu.be', 'https://music.youtube.com']):
        update.message.reply_text('Let me YouTube link')
        return

    if "list=" in message_text or "playlist" in message_text:                                                           # Обработка плейлиста
        status = update.message.reply_text('Checking playlist...')
        videos = download_playlist(message_text)
        if not videos:
            status = update.message.reply_text('No videos found.')
            return

        status.edit_text(f'Found {len(videos)} videos in playlist')

        count = 0
        for video in videos:
            video_url = video['url']
            if video_url in downloaded_songs:
                update.message.reply_text("Skipping {video['title']}")
                continue

            message = update.message.reply_text("Downloading {video['title']}")
            audio_path, title = download_audio(video_url)
            if audio_path:
                with open(audio_path, 'rb') as audio:
                    ext = os.path.splitext(audio_path)[1] or '.mp3'
                    update.message.reply_voice(
                        voice=audio,
                        caption=f"{title}",
                        filename = f"{title}{ext}"
                    )
                message.edit_text("Sended")

                try:
                    os.remove(audio_path)
                    shutil.rmtree(os.path.dirname(audio_path))
                except Exception as e:
                    print(f"[CLEANUP] Error: {e}")

                downloaded_songs.add(video_url)
                save_to_cache(video_url, downloaded_songs)
                count += 1
            else:
                message.edit_text(f"Can not be download")

        status.edit_text(f"Playlist downloaded. {count} / {len(videos)}")
        return

    if message_text in downloaded_songs:                                                                                # Обработка трека
        update.message.reply_text("This track has already been downloaded")
        return

    status = update.message.reply_text("⏳ Downloading...")
    audio_path, title = download_audio(message_text)                                                                #Вывод пути и названия

    if audio_path:
        with open(audio_path, 'rb') as audio:
            ext = os.path.splitext(audio_path)[1] or '.mp3'
            update.message.reply_voice(                                                                             #Отправляет как голосовое
                voice=audio,
                caption=f"{title}",
                filename=f"{title}{ext}"
            )

        status.edit_text("✅ Done.")                                                                                #Обновление статуса(Эдит сообщения)

        try:                                                                                                        #Чистим времянку
            os.remove(audio_path)
            shutil.rmtree(os.path.dirname(audio_path))
        except Exception as e:
            print(f"[CLEANUP] Delete error: {e}")

        downloaded_songs.add(message_text)
        save_to_cache(message_text, downloaded_songs)
    else:
        status.edit_text("Failed to download audio.")