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
        print(f"Трек: {track_string}, схожесть с выборочным средним: {(similarity * 100):.1f}%")

def print_global_bottom_n(similarity_list, n):
    print("=" * 80)

    print("Список 10 треков, наименее схожих с выборочным средним:")

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

def print_taste_dna(top_artists, top_genres, track_count, n):
    print("=" * 80)
    print("🧬 РАСШИФРОВКА ТВОЕГО ВКУСОВОГО ДНК (ГЛОБАЛЬНО)")

    print(f"\n🎧 КОЛИЧЕСТВО ТРЕКОВ В ПЛЕЙЛИСТЕ: {track_count} треков")

    print("\n🎸 Доминирующие жанры:")
    for genre, weight in top_genres[:n]:
        print(f"  • {genre}: {weight * 100:.1f}% плейлиста")

    print("\n🎤 Ключевые исполнители:")
    for artist, weight in top_artists[:n]:
        print(f"  • {artist}: {weight * 100:.1f}% плейлиста")

    # Шуточный вывод
    main_genre = top_genres[0][0]
    main_artist = top_artists[0][0]
    print(f"\n💡 Твой «сферический трек в вакууме»: {main_genre} в исполнении {main_artist}.")

def show_menu():
    print("Выберите режим анализа:")
    print("[1] 📊 Общий анализ (Total Stats)")
    print("[2] 🎧 Жанровый анализ (Genres Stats)")
    print("[3] 🚀 Анализ эволюции (Evolution Timeline)")
    print("[4] 🧠 Автоматический кластеризированный анализ")
    print("[5] 👀 Сравнить ваш плейлист с другим плейлистом")
    print("[0] ❌ Выход")
    return input(">> ")

def print_era_genre_stats(era_index, genre_counter, track_count, top_n=5):
    print("=" * 80)
    title = f"ЭПОХА {era_index}"
    print(f"🎸 {title}: жанровой профиль")
    data_string = "=" * 80
    data_string += f"\n🎸 ЭРА {title}: жанровой профиль"

    for genre, cnt in genre_counter.most_common(top_n):
        perc = cnt / track_count * 100 if track_count > 0 else 0
        print(f"  • {genre}: {cnt} трек(ов), {perc:.1f}%")
        data_string += f"\n  • {genre}: {cnt} трек(ов), {perc:.1f}%"
    return  data_string

def print_era_artist_stats(era_index, artist_counter, track_count, top_n=5):
    title = f"ЭПОХА {era_index}"
    print(f"\n🎤 {title}: основные артисты")
    data_string = f"\n\n🎤 ЭРА {title}: основные артисты"
    for artist, cnt in artist_counter.most_common(top_n):
        perc = cnt / track_count * 100 if track_count > 0 else 0
        print(f"  • {artist}: {cnt} трек(ов), {perc:.1f}% эры")
        data_string += f"\n  • {artist}: {cnt} трек(ов), {perc:.1f}% эры"
    return data_string


def print_taste_genre_dna(genre, top_artists, top_genres, track_count, n):
    print("=" * 80)
    print(f"🧬 РАСШИФРОВКА ТВОЕГО ВКУСОВОГО ДНК ВНУТРИ КЛАСТЕРА ЖАНРА {genre}")

    print(f"\n🎧 КОЛИЧЕСТВО ТРЕКОВ В КЛАСТЕРЕ: {track_count} треков")

    print("\n🎸 Доминирующие поджанры:")
    for genre, weight, count in top_genres[:n]:
        print(f"  • {genre}: {count} треков, {weight * 100:.1f}% кластера")

    print("\n🎤 Ключевые исполнители:")
    for artist, weight in top_artists[:n]:
        print(f"  • {artist}: {weight * 100:.1f}% кластера")

    # Шуточный вывод
    main_genre = top_genres[0][0]
    main_artist = top_artists[0][0]
    print(f"\n💡 Твой «сферический трек в вакууме»: {main_genre} в исполнении {main_artist}.")

def print_playlist_comparison(result, name1, name2):
    print("=" * 80)
    print(f"👀 СРАВНЕНИЕ ПЛЕЙЛИСТОВ: {name1} vs {name2}")
    print(f"\n📱 Сходство «вкусовых центроидов» (cosine): {result['taste_cosine']*100:.1f}%")

    print("\n🎤 Артисты:")
    print(f" 📊 Jaccard-пересечение: {result['jaccard_artists']*100:.1f}%")
    if result["common_artists"]:
        print(" 🎙️ Общие исполнители:")
        for a in list(result["common_artists"])[:5]:
            print(f"    • {a}")
    else:
        print("  Общих исполнителей нет.")

    print("\n🎸 Жанры:")
    print(f" 📊 Jaccard-пересечение: {result['jaccard_genres']*100:.1f}%")
    if result["common_genres"]:
        print(" 🎧 Общие жанры:")
        for g in list(result["common_genres"])[:5]:
            print(f"    • {g}")
    else:
        print("  Общих жанров нет.")

def print_kmeans_clusters(cluster_reports):
    print("=" * 80)
    print("🧠 АВТОМАТИЧЕСКАЯ КЛАСТЕРИЗАЦИЯ ВКУСА (K-MEANS)")

    for report in cluster_reports:
        print(f"\n🏷️  КЛАСТЕР #{report['cluster_id']} (Треков: {report['count']})")

        # Собираем описание
        genres_str = ", ".join([f"{g[0]} ({g[1] * 100:.0f}%)" for g in report['top_genres']])
        artists_str = ", ".join([f"{a[0]}" for a in report['top_artists']])

        print(f"   Жанровый профиль: {genres_str}")
        print(f"   Ядро артистов:    {artists_str}")







