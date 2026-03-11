import requests
import json
import time
from datetime import datetime
import os
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

#Группировка по усредненным жанрам
GENRE_MAP = {
    # rock / metal
    "rusrock": "rock",
    "rock": "rock",
    "punk": "rock",
    "postpunk": "rock",
    "folkrock": "rock",
    "classicmetal": "rock",
    "metal": "rock",
    "numetal": "rock",
    "allrock": "rock",
    "alternativemetal": "rock",
    "posthardcore": "rock",
    "hardrock": "rock",
    "industrial": "rock",
    "epicmetal": "rock",
    "j-rock": "rock",


    # pop
    "pop": "pop",
    "ruspop": "pop",
    "kpop": "pop",
    "hyperpopgenre": "pop",
    "japanesepop": "pop",
    "modern": "pop",

    # rap
    "rusrap": "rap",
    "rap": "rap",
    "foreignrap": "rap",

    # electronic / dance
    "electronics": "electronic_dance",
    "dance": "electronic_dance",
    "edmgenre": "electronic_dance",
    "bassgenre": "electronic_dance",
    "phonkgenre": "electronic_dance",

    # indie / alt

    "indie": "indie_alt",
    "local-indie": "indie_alt",
    "alternative": "indie_alt",

    # folk / ethno
    "latinfolk": "folk_ethno",
    "folk": "folk_ethno",
    "eurofolk": "folk_ethno",
    "folkmetal": "folk_ethno",
    "folkgenre": "folk_ethno",
    "country": "folk_ethno",
    "caucasian": "folk_ethno",

    # jazz / soul / rnb
    "rnb": "jazz_soul_rnb",
    "soul": "jazz_soul_rnb",
    "smoothjazz": "jazz_soul_rnb",
    "vocaljazz": "jazz_soul_rnb",

    # classical / score
    "classical": "classical_score",
    "classicalmasterpieces": "classical_score",
    "soundtrack": "classical_score",
    "films": "classical_score",

    # media
    "videogame": "media",
    "animemusic": "media",
    "animated": "media",
    "sport": "media",

    # retro / disco
    "disco": "retro_dance",
    "newwave": "retro_dance",

    # bard / estrada / shanson
    "rusestrada": "bard_estrada",
    "foreignbard": "bard_estrada",
    "shanson": "bard_estrada",

    # reggae / ska
    "reggae": "reggae_ska",
    "ska": "reggae_ska",

    # chill / vocal
    "relax": "chill_vocal",
    "vocal": "chill_vocal",
}

def print_error(e):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", ">>>", e)

def send_welcome():
    print("=== Экспорт Яндекс Музыки === \n\n" +
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

#Вся та же группировка
def normalize_genre(raw_genre: str) -> str:
    g = raw_genre.strip().lower()
    return GENRE_MAP.get(g, "other")


def save_to_file(file_string, title, holder):
    # Запись данных в файл
    if not os.path.isdir("analyse_data"):
        os.mkdir("analyse_data")

    if title == "Мне нравится":
        title += f"_{holder}"

    filename = f"analyse_data/{title}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(file_string)


def handle_message(uri_raw):
    try:
        #Обрабатываем и разбираем ссылку на части
        uri_raw = uri_raw.strip()
        uri_parts = uri_raw.split('?')[0].split('/')

        owner = uri_parts[4]
        kinds = uri_parts[6]

        #Генерируем ссылку, по которой будем обращаться к внутреннему API яндекса,
        # увы - с открытым меня послали
        uri = f"https://music.yandex.ru/handlers/playlist.jsx?owner={owner}&kinds={kinds}"
        response = requests.get(uri)
        response.raise_for_status()

        #Получаем ответ и парсим JSON
        data = response.json()
        playlist_title = f"{data['playlist']['title']}_{owner}"
        tracks = data['playlist']['tracks']


        print(f"Название плейлиста: {playlist_title}")
        print(f"Число треков: {len(tracks)}")


        #Собираем данные для DataFrame
        all_tracks = []

        for track in tracks:
            artists_names = ", ".join(artist['name'] for artist in track['artists'])
            title = track['title']

            album = track['albums'][0]
            try:
                genre = album.get('genre', "Не указан")
            except IndexError:  # Бывает трек без альбома
                genre = "Не указан"

            normalized_genre = normalize_genre(genre)
            tuple_track = (artists_names, title, normalized_genre, genre)
            all_tracks.append(tuple_track)

            '''genres[normalized_genre] = genres.get(normalized_genre, 0) + 1
            full_track = f"{artists_names} - {track['title']}, Жанр: {normalized_genre}\n"
            all_file += full_track
            split_artist = artists_names.split(",")
            for artist in split_artist:
                artist = artist.strip()
                artists_for_me[artist] = artists_for_me.get(artist, 0) + 1'''

        df = pd.DataFrame(all_tracks, columns=["artists", "title", "genre", "subgenre"])


        top_genres_series = df['genre'].value_counts().head(5)

        top_artists_series = df['artists'].str.split(', ').explode().value_counts().head(5)

        lines = df['artists'] + " - " + df['title'] + ", Жанр: " + df['genre']

        file_content = "\n".join(lines)

        '''sort_genres = {}
        sort_artists = {}

        for key in sorted(genres, key=genres.get):
            sort_genres[key] = genres[key]

        for key in sorted(artists_for_me, key=artists_for_me.get):
            sort_artists[key] = artists_for_me[key]


        sort_genres = dict(reversed(sort_genres.items()))
        sort_artists = dict(reversed(sort_artists.items()))

        top_genres = list(sort_genres.items())[:5]
        top_genres = [genre[0] for genre in top_genres]

        top_artists = list(sort_artists.items())[:5]
        top_artists = [artist[0] for artist in top_artists]'''

        stats = "\n" + "=" * 60 + "\n" + "ТОП ЖАНРОВ (ПО КОЛИЧЕСТВУ ТРЕКОВ)\n"



        for genre, count in top_genres_series.items():
            stats += f"{genre}: {count}\n"

        stats += "=" * 60 + "\n" + "ТОП АРТИСТОВ (ПО КОЛИЧЕСТВУ ТРЕКОВ) \n"

        for artist, count in top_artists_series.items():
            stats += f"{artist}: {count}\n"

        stats += "=" * 60 +"\n"

        file_content += stats

        #Запись данных в файл

        save_to_file(file_content, playlist_title, owner)

        df.to_csv(f"{playlist_title}.csv")


        return df, playlist_title

    except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
        print_error(e)
        print("Ошибка! Несуществующий плейлист или временный бан от Яндекса. Проверьте ссылку " +
              "и попробуйте еще раз через некоторое время или на другом устройстве.\n\n" +
              f"Дополнительная информация: {e}")
    except IndexError as e:
        print_error(e)
        print("Ошибка! Вероятно, некорректная ссылка. Проверьте, чтобы она была вида " +
              "https://music.yandex.ru/users/USERNAME/playlists/PLAYLIST_ID. Попробуйте еще раз.\n\n" +
              f"Дополнительная информация: {e}")

    except Exception as e:
        print_error(e)
        print("Ошибка! Проверьте правильность ссылки и попробуйте еще раз. " +
              "Также учтите, что из-за большого количества запросов может последовать временный " +
              "бан от Яндекса. В таком случае попробуйте с другого устройства или на сайте " +
              "https://files.u-pov.ru/programs/YandexMusicExport.\n\n" +
              f"Дополнительная информация: {e}")

if __name__ == "__main__":
    send_welcome()
    while True:
        try:
            uri_raw = input("\nВведите ссылку на плейлист: ")
            playlist_data = handle_message(uri_raw)
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print_error(e)
            time.sleep(15)