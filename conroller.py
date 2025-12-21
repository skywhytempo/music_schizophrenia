import yme
import analysis
import view

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

    ohe_data, all_artists, all_genres = analysis.build_ohe(tracklist, artists_map, genres_map)

    #Формируем центроиду
    median_ohe_vector = analysis.global_cenroid(artists_map, genres_map, all_artists, all_genres)


    # Глобальный анализ - может быть не очень эффективно, ведь,
    # иногда могут возникнуть кластеры, из-за чего
    # коэф. схожести как бы "размажется"
    only_similarity_list = analysis.compute_similarity(ohe_data, median_ohe_vector)
    similarity_list = analysis.sorted_similarity_with_tracks(tracklist, only_similarity_list)

    view.print_global_top_n(similarity_list, 10)

    view.print_global_bottom_n(similarity_list, 10)

    m_s, S2, I = analysis.compute_stats(only_similarity_list)
    view.print_math_stats(m_s, S2, I)

    #ТАРАНИМ КЛАСТЕРИЗАЦИЮ

    print("=" * 80)

    print("ЖАНРОВЫЙ РАЗБОР ПРИ ПОМОЩИ КЛАСТЕРИЗАЦИИ (РУЧНОЙ):")

    indices_by_genre = analysis.genres_idxs(tracklist)
    for genre, idxs in indices_by_genre.items():
        # пропускаем совсем маленькие жанры, если хочешь
        if len(idxs) < 5:
            continue
        sims = analysis.analyze_by_genre(genre,idxs, ohe_data)
        m_s, S2, I = analysis.compute_stats(sims)

        view.print_stats_by_genre(genre, len(idxs), m_s, S2, I)
        # Топ-5 самых типичных треков внутри жанра
        sims_with_tracks = analysis.get_top_tracks(tracklist, sims, idxs)
        sims_artists = analysis.get_top_artists(sims_with_tracks)
        view.print_top_artists_and_tracks_by_genre(sims_artists, sims_with_tracks, 6)

except Exception as e:
    yme.print_error(e)
