import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# pip install python-telegram-bot==13.15

from services.cache import load_cache, save_to_cache                                                                    #Подключаем cache.py

from handlers.commands import start
from handlers.messages import handle_message, set_cache_reference


env_path = Path(__file__).resolve().parent / "config" / ".env"

if not env_path.exists():
    print(f".env not found at: {env_path}")
else:
    print(f"Loading .env: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)


BOT_TOKEN = os.getenv("BOT_TOKEN")                                                                                      #В файле .env
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "downloads")                                                             #В файле .env



if not BOT_TOKEN:
    print("BOT_TOKEN can't be found in .env!")
    exit(1)

downloaded_songs = load_cache()
set_cache_reference(downloaded_songs)


def main():                                                                                                             #Основная логика бота
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))                                                     # Регистрируем обработчик команды /start
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))                             #Врубаем фильтры

    print("🚀 Бот запущен!")                                                                                            # Запускаем опрос обновлений (прослушка)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":                                                                                              #Точка выхода
    main()