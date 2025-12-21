import matplotlib.pyplot as plt


def string_track(tuple_track: tuple):
    track_data = f"{tuple_track[0]} - {tuple_track[1]}, Жанр: {tuple_track[2]}"
    return track_data

def print_global_top_n(similarity_list, n):
    print("=" * 80)

    print("Список 10 треков, наиболее схожих с выборочным средним:")

    # Глобальный анализ - может быть не очень эффективно, ведь,
    # иногда могут возникнуть кластеры, из-за чего
    # коэф. схожести как бы "размажется"

    for track, similarity in similarity_list[:n]:
        track_string = string_track(track)
        print(f"Трек: {track_string}, схожесть с выборочным средним: {similarity * 100}%")

def print_global_bottom_n(similarity_list, n):
    print("=" * 80)

    print("Список 10 треков, наиболее схожих с выборочным средним:")

    # Глобальный анализ - может быть не очень эффективно, ведь,
    # иногда могут возникнуть кластеры, из-за чего
    # коэф. схожести как бы "размажется"

    for track, similarity in list(reversed(similarity_list))[:n]:
        track_string = string_track(track)
        print(f"Трек: {track_string}, схожесть с выборочным средним: {similarity * 100}%")

def print_math_stats(mean, var, idx):
    print("=" * 80)
    print(f"Выборочный средний коэффициент сходства треков: {mean:.2f}")
    print(f"Выборочная дисперсия сходства треков: {var:.2f}")
    print(f"Значение метрики «индекс разнообразия вкуса»: {idx:.2f}")

def print_stats_by_genre(genre, track_count, mean, var, idx):
    print("\n" + "-" * 40)
    print(f"Жанр: {genre}")
    print(f"  Треков в жанре: {track_count}")
    print(f"  Среднее сходство внутри жанра: {mean:.2f}")
    print(f"  Дисперсия внутри жанра: {var:.2f}")
    print(f"  Индекс разнообразия внутри жанра: {idx:.2f}")

def print_top_artists_and_tracks_by_genre(artists_list, sim_tracks, n):
    print(f"ТОП {n} АРТИСТОВ ЖАНРА (ПО КОЛИЧЕСТВУ ТРЕКОВ)")

    top_artists = list(artists_list.keys())[:n]

    for artist in top_artists:
        print(f"  {artist}: {artists_list[artist]}")

    print(f"Топ-{n} самых типичных треков:")
    for track, s in sim_tracks[:n]:
        print(f"  {string_track(track)} | схожесть: {s * 100:.1f}%")

def plot_hist(sim_list, genre):
    plt.figure(figsize=(6, 3))
    plt.hist(
        sim_list,
        bins=10,  # 10 интервалов: 0.0–0.1, 0.1–0.2, ... 0.9–1.0
        range=(0, 1),
        edgecolor='black'
    )

    plt.xlabel(f'Cosine similarity to taste centroid for {genre}')
    plt.ylabel('Number of tracks')
    plt.title('Distribution of track similarity')

    plt.tight_layout()
    plt.show()

