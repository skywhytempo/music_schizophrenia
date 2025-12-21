import yme
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


#Приводим трек к строке
def string_track(tuple_track: tuple):
    track_data = f"{tuple_track[0]} - {tuple_track[1]}, Жанр: {tuple_track[2]}"
    return track_data

def get_similarity_to_median(vector, median_vector):
    scalar = np.dot(vector, median_vector)
    norms = np.linalg.norm(vector) * np.linalg.norm(median_vector)
    sim_coef = scalar / norms

    return round(sim_coef, 4)


def cosine(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    num = np.dot(a, b)
    den = np.linalg.norm(a) * np.linalg.norm(b)
    if den == 0:
        return 0.0
    return num / den

def centroid(vectors):
    return np.mean(np.array(vectors, dtype=float), axis=0)



yme.send_welcome()
uri_raw = input("\nВведите ссылку на плейлист: ")

try:
    music_data = yme.handle_message(uri_raw)
    tracklist, artists_map, genres_map = music_data

    yme.print_results(music_data)

    artists_count = len(artists_map)
    all_artists = list(artists_map.keys())

    genres_count = len(genres_map)
    all_genres = list(genres_map.keys())

    ohe_data = []

    #Формируем центроиду
    median_ohe_artist = [artists_map[artist]/artists_count for artist in all_artists]
    median_ohe_genre = [genres_map[genre]/genres_count for genre in all_genres]

    median_ohe_vector = median_ohe_artist + median_ohe_genre

    for track in tracklist:
        track_artists = track[0]
        track_genre = track[2]
        split_artists = track_artists.split(",")
        split_artists = list(map(lambda string: string.strip(), split_artists))
        ohe_artist = [0] * artists_count
        ohe_genre = [0] * genres_count

        for artist in split_artists:
            artist_idx = all_artists.index(artist)
            ohe_artist[artist_idx] = 1

        genre_idx = all_genres.index(track_genre)
        ohe_genre[genre_idx] = 1

        ohe_track = ohe_artist + ohe_genre

        ohe_data.append(ohe_track)

    similarity_list = []

    for i in range(len(ohe_data)):
        track_vector = ohe_data[i]
        track_string = string_track(tracklist[i])
        similarity_coef = get_similarity_to_median(track_vector, median_ohe_vector)
        similarity_list.append((tracklist[i], similarity_coef))
        #print(f"Трек: {track_string}, схожесть со средним: {similarity_coef}%")

    similarity_list = sorted(similarity_list, key=lambda x:x[1], reverse=True)
    only_similarity_list = [sim[1] for sim in similarity_list]


    print("=" * 80)

    print("Список 10 треков, наиболее схожих с выборочным средним:")



    for track, similarity in similarity_list[:10]:
        track_string = string_track(track)
        print(f"Трек: {track_string}, схожесть с выборочным средним: {similarity * 100}%")

    print("=" * 80)

    print("Список 10 треков, наименее схожих с выборочным средним:")
    for track, similarity in list(reversed(similarity_list))[:10]:
        track_string = string_track(track)
        print(f"Трек: {track_string}, схожесть с выборочным средним: {100 * similarity}%")

    print("=" * 80)

    m_s = (1/len(similarity_list)) * sum(s_i for s_i in only_similarity_list)

    S2 = (1/(len(similarity_list) - 1)) * sum((s_i - m_s)**2 for s_i in only_similarity_list)

    print(f"Выборочный средний коэффициент сходства треков: {m_s:.2f}")
    print(f"Выборочная дисперсия сходства треков: {S2:.2f}")

    I = (1 - m_s) * (S2**0.5)

    print(f"Значение метрики «индекс разнообразия вкуса»: {I:.2f}")

    #ТАРАНИМ КЛАСТЕРИЗАЦИЮ

    print("=" * 80)

    print("ЖАНРОВЫЙ РАЗБОР ПРИ ПОМОЩИ КЛАСТЕРИЗАЦИИ (РУЧНОЙ):")

    indices_by_genre = defaultdict(list)
    for i, track in enumerate(tracklist):
        genre = track[2]  # уже сгруппированный жанр из handle_message
        indices_by_genre[genre].append(i)


    for genre, idxs in indices_by_genre.items():
        # пропускаем совсем маленькие жанры, если хочешь
        if len(idxs) < 5:
            continue

        genre_vecs = [ohe_data[i] for i in idxs]
        genre_centroid = centroid(genre_vecs)

        sims = [cosine(ohe_data[i], genre_centroid) for i in idxs]

        m_s = sum(sims) / len(sims)
        if len(sims) > 1:
            S2 = sum((s - m_s) ** 2 for s in sims) / (len(sims) - 1)
        else:
            S2 = 0.0
        I = (1 - m_s) * (S2 ** 0.5)

        print("\n" + "-" * 40)
        print(f"Жанр: {genre}")
        print(f"  Треков в жанре: {len(idxs)}")
        print(f"  Среднее сходство внутри жанра: {m_s:.2f}")
        print(f"  Дисперсия внутри жанра: {S2:.2f}")
        print(f"  Индекс разнообразия внутри жанра: {I:.2f}")


        # Топ-5 самых типичных треков внутри жанра
        sims_with_tracks = [(tracklist[i], sims[k]) for k, i in enumerate(idxs)]
        sims_with_tracks.sort(key=lambda x: x[1], reverse=True)

        sims_artists = {}

        for track, s in sims_with_tracks:
            split_artist = track[0].split(",")
            for artist in split_artist:
                artist = artist.strip()
                sims_artists[artist] = sims_artists.get(artist, 0) + 1


        sort_sims_artists = {}
        for key in sorted(sims_artists, key=sims_artists.get):
            sort_sims_artists[key] = sims_artists[key]

        sims_sort_artists = dict(reversed(sort_sims_artists.items()))

        print("ТОП 5 АРТИСТОВ ЖАНРА (ПО КОЛИЧЕСТВУ ТРЕКОВ)")

        top_artists = list(sims_sort_artists.keys())[:5]

        for artist in top_artists:
            print(f"    {artist}: {sims_sort_artists[artist]}")

        print("  Топ-5 самых типичных треков:")
        for track, s in sims_with_tracks[:5]:
            print(f"    {string_track(track)} | схожесть: {s * 100:.1f}%")




    #Гистограмма
    '''plt.figure(figsize=(8, 4))
    plt.hist(
        only_similarity_list,
        bins=10,  # 10 интервалов: 0.0–0.1, 0.1–0.2, ... 0.9–1.0
        range=(0, 1),
        edgecolor='black'
    )

    plt.xlabel('Cosine similarity to taste centroid')
    plt.ylabel('Number of tracks')
    plt.title('Distribution of track similarity')

    plt.tight_layout()
    plt.show()'''

except Exception as e:
    yme.print_error(e)
