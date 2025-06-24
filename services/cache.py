from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / 'downloaded_songs.txt'          #Вместо os.path.join юзаем Path

def load_cache():                                                           #Загружает все строки из файла и возвращает множество ссылок (set()), чтобы не было повторений.
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_cache(url, cache):                                              #Добавляет новый URL и сохраняет всё обратно в файл.
    cache.add(url)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        for item in cache:
            f.write(f"{item}\n")