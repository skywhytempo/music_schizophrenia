import os
from dotenv import load_dotenv # Импортируем загрузчик
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from datetime import datetime

def print_error(e):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", ">>>", e)




def send_welcome():
    print("=== Экспорт SPOTIFY === \n\n" +
          "Программа позволяет экспортировать любой плейлист Яндекс Музыки в текстовое " +
          "представление ИМЯ ИСПОЛНИТЕЛЯ - НАЗВАНИЕ ТРЕКА.\n\n" +
          "1. Скопируйте и вставьте ниже ссылку на плейлист. Обязательно проверьте, чтобы она была " +
          "вида https://music.yandex.ru/users/USERNAME/playlists/PLAYLIST_ID. <b><i>Также убедитесь, что плейлист ❗️не приватный❗️</i></b>\n" +
          "2. Если плейлист большой, может потребоваться некоторое время для обработки.\n" +
          "3. Если ссылка корректная, но возникает ошибка, то, вероятно, сработал 'бан' со " +
          "стороны Яндекса. В таком случае попробуйте еще раз через некоторое время или на " +
          "другом устройстве.\n" +
          "4. Предложения, критика и прочее принимаются тута: https://t.me/aleqsanbr")
    print("Также функционал доступен на сайте :) https://files.u-pov.ru/programs/YandexMusicExport")

def handle_message(playlist_url):

    try:
        # --- ЭТАП 0: Авторизация в spotipy ---
        load_dotenv()

        if not os.getenv('SPOTIPY_CLIENT_ID'):
            print("Ошибка: Ключи не найдены!")
        else:
            print("Ключи успешно загружены.")

        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # --- ЭТАП 1: Получение всех треков (Пагинация) ---
        print("--- Шаг 1: Скачивание списка треков ---")

        playlist = sp.playlist(playlist_url, fields='name,tracks.total')
        playlist_name = playlist['name']
        total_tracks = playlist['tracks']['total']

        print(f"Название плейлиста: {playlist_name}")
        print(f"Всего треков: {total_tracks}")
        print("\nЗагрузка треков...")

        all_tracks = []

        limit = 100
        offset = 0

        while offset < total_tracks:
            results = sp.playlist_tracks(playlist_url, limit=limit, offset=offset)
            all_tracks.extend(results["items"])

            print(f"Загружено {min(offset, total_tracks)} из {total_tracks} треков...")

            # Переходим к следующей порции
            offset += limit

        # --- ЭТАП 2: Сбор уникальных ID артистов ---
        print("\n--- Шаг 2: Анализ артистов ---")

        artists_ids = set()

        for item in all_tracks:
            track = item['track']
            if track and track['artists']:
                # Берем ID только первого (основного) артиста
                main_artist_id = track['artists'][0]['id']
                if main_artist_id:  # Бывает, что ID нет (редкость, но бывает)
                    artists_ids.add(main_artist_id)

        unique_artists_list = list(artists_ids)
        print(f"Найдено уникальных артистов: {len(unique_artists_list)}")


        # --- ЭТАП 3: Получение жанров (Пакетная обработка) ---
        print("\n--- Шаг 3: Загрузка жанров (пачками по 50) ---")

        artist_genres_map = {}  # Словарь вида {'id_артиста': ['pop', 'rock']}

        for i in range(0, len(unique_artists_list), 50):

            chunk = unique_artists_list[i:i+50]

            artists_data = sp.artists(chunk)

            for artist in artists_data['artists']:
                artist_genres_map[artist['id']] = artist['genres']

            print(f"Обработано артистов: {min(i + 50, len(unique_artists_list))}")

        # --- ФИНАЛ: Вывод результатов ---

        print("\n" + "=" * 30)
        print("ИТОГОВЫЙ СПИСОК")
        print("=" * 30)

        for idx, item in enumerate(all_tracks, 1):
            track = item['track']

            if not track:
                print(f"{idx}. [Недоступный трек]")
                continue

            track_name = track['name']

            # Данные артиста из объекта трека
            artist_obj = track['artists'][0]
            artist_name = artist_obj['name']
            artist_id = artist_obj['id']

            # Достаем жанры из нашего заранее подготовленного словаря
            # Если жанров нет или артист не нашелся, возвращаем пустой список
            genres = artist_genres_map.get(artist_id, [])

            if genres:
                genres_str = ", ".join(genres)
            else:
                genres_str = "Жанры не указаны"

            print(f"{idx}. {artist_name} - {track_name}")
            print(f"   [{genres_str}]")
            print("-" * 10)



    except Exception as e:
        print_error(e)

    return

if __name__ == "__main__":
    send_welcome()
    while True:
        try:
            uri_raw = input("\nВведите ссылку на плейлист: ")
            handle_message(uri_raw)
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print_error(e)
            time.sleep(15)