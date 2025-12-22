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

def print_taste_dna(top_artists, top_genres, track_count, n):
    print("=" * 80)
    print("🧬 РАСШИФРОВКА ТВОЕГО ВКУСОВОГО ДНК ВНУТРИ КЛАСТЕРА")

    print(f"\n🎧 КОЛИЧЕСТВО ТРЕКОВ В КЛАСТЕРЕ: {track_count} треков")

    print("\n🎸 Доминирующие жанры:")
    for genre, weight in top_genres[:n]:
        print(f"  • {genre}: {weight * 100:.1f}% кластера")

    print("\n🎤 Ключевые исполнители:")
    for artist, weight in top_artists[:n]:
        print(f"  • {artist}: {weight * 100:.1f}% кластера")

    # Шуточный вывод
    main_genre = top_genres[0][0]
    main_artist = top_artists[0][0]
    print(f"\n💡 Твой «сферический трек в вакууме»: {main_genre} в исполнении {main_artist}.")

def show_menu():
    print("Выберите режим анализа:")
    print("[1] 📊 Общий анализ (Total Stats)")
    print("[2] 🚀 Анализ эволюции (Evolution Timeline)")
    print("[0] ❌ Выход")
    return input(">> ")

def print_era_genre_stats(era_index, genre_counter, top_n=5):
    print("=" * 80)
    labels = ["THE ROOTS (Начало)", "THE SHIFT (Переход)", "CURRENT ERA (Настоящее)"][::-1]
    title = labels[era_index] if era_index < len(labels) else f"ЭПОХА {era_index}"
    #title = f"ЭПОХА {era_index}"
    print(f"🎸 ЭРА {title}: жанровой профиль")
    data_string = "=" * 80
    data_string += f"\n🎸 ЭРА {title}: жанровой профиль"
    total = sum(genre_counter.values())
    for genre, cnt in genre_counter.most_common(top_n):
        perc = cnt / total * 100 if total > 0 else 0
        print(f"  • {genre}: {cnt} трек(ов), {perc:.1f}%")
        data_string += f"\n  • {genre}: {cnt} трек(ов), {perc:.1f}%"
    return  data_string

def print_era_artist_stats(era_index, artist_counter, top_n=5):
    labels = ["THE ROOTS (Начало)", "THE SHIFT (Переход)", "CURRENT ERA (Настоящее)"][::-1]
    title = labels[era_index] if era_index < len(labels) else f"ЭПОХА {era_index}"
    #title = f"ЭПОХА {era_index}"
    print(f"\n🎤 ЭРА {title}: основные артисты")
    data_string = f"\n\n🎤 ЭРА {title}: основные артисты"
    total = sum(artist_counter.values())
    for artist, cnt in artist_counter.most_common(top_n):
        perc = cnt / total * 100 if total > 0 else 0
        print(f"  • {artist}: {cnt} трек(ов), {perc:.1f}% эры")
        data_string += f"\n  • {artist}: {cnt} трек(ов), {perc:.1f}% эры"
    return data_string

def print_era_mood_stats(era_index, aggr_count, melanch_count):
    labels = ["THE ROOTS (Начало)", "THE SHIFT (Переход)", "CURRENT ERA (Настоящее)"][::-1]
    title = labels[era_index] if era_index < len(labels) else f"ЭПОХА {era_index}"

    #title = f"ЭПОХА {era_index}"
    data_string = (f"\n\n🤍 ЭРА {title}: условное «настроение» по названиям треков"
                   + f"\n  Индекс энергичности: {aggr_count}"
                   + f"\n  Индекс меланхолии:    {melanch_count}")
    print(f"\n🤍 ЭРА {title}: условное «настроение» по названиям треков")
    print(f"  Индекс энергичности: {aggr_count}")
    print(f"  Индекс меланхолии:    {melanch_count}")
    if aggr_count > melanch_count:
        print("  → Эра больше тяготеет к агрессивному/энергичному настроению.")
        data_string += "\n  → Эра больше тяготеет к агрессивному/энергичному настроению.\n"
    elif melanch_count > aggr_count:
        print("  → Эра больше тяготеет к меланхоличному настроению.")
        data_string += "\n  → Эра больше тяготеет к меланхоличному настроению.\n"
    else:
        print("  → Баланс между агрессией и меланхолией.")
        data_string += "\n  → Баланс между агрессией и меланхолией\n."
    print("=" * 80)

    return data_string