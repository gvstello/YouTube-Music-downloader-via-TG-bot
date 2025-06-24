import os
import tempfile
import time
import yt_dlp
import glob



def download_audio(url):                                                                                                #Логика скачивания файла (возвращает путь и название)
    try:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'audio.%(ext)s')

        download_opts = {
            'format': 'm4a/mp3/webm',
            'postprocessors': [],                                                                                       # не используем FFmpeg
            'outtmpl': temp_path,
            'nocheckcertificate': True,
            'ignoreerrors': True,
        }

        with yt_dlp.YoutubeDL(download_opts) as ydl:                                                                    #Подключаем yt_dlp скачиваем в temp
            info = ydl.extract_info(url)
            title = info.get('title', 'Unknown')

            for _ in range(30):                                                                                         # Ждём появления файла 30 сек
                audio_files = (
                    glob.glob(os.path.join(temp_dir, '*.m3u8')) +
                    glob.glob(os.path.join(temp_dir, '*.mp3')) +
                    glob.glob(os.path.join(temp_dir, '*.m4a')) +
                    glob.glob(os.path.join(temp_dir, '*.webm')) +
                    glob.glob(os.path.join(temp_dir, '*.mp4'))
                )
                if audio_files:
                    break
                time.sleep(1)

            if not audio_files:
                print(f"[download_audio] Не найден файл аудио")
                return None, None

            audio_path = audio_files[0]
            time.sleep(1.5)  # подстраховка, чтобы файл успел дописаться

            return audio_path, title

    except Exception as e:
        print(f"[download_audio] Ошибка: {str(e)}")
        return None, None

def download_playlist(url):                                                                                             #Возвращает список из плейлиста: [{url, title}, ...]
    try:
        options = {
            'quiet': True,
            'extract_flat': True,                                                                                       # Только ссылки, без скачивания
            'force_generic_extractor': False,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' not in info:
                print("[playlist] Не найдены entries")
                return []

            return [
                {
                    'url': entry['url'] if entry['url'].startswith('http') else f"https://www.youtube.com/watch?v={entry['id']}",
                    'title': entry.get('title', 'Unknown')
                }
                for entry in info['entries'] if entry
            ]

    except Exception as e:
        print(f"[playlist] Ошибка: {e}")
        return []