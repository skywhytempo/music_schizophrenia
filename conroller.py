import yme
import analysis
import view

def run():
    yme.send_welcome()

    while True:

        uri_raw = input("\nВведите ссылку на плейлист: ")

        try:
            music_data = yme.handle_message(uri_raw)

            tracklist, artists_map, genres_map, playlist_title = music_data

            print(playlist_title)

            track_count = len(tracklist)

            yme.print_results(music_data)

            ohe_data, all_artists, all_genres = analysis.build_ohe(tracklist, artists_map, genres_map)

            # Формируем центроиду
            median_ohe_vector = analysis.global_centroid(artists_map, genres_map, all_artists, all_genres, track_count)

            # Глобальный анализ - может быть не очень эффективно, ведь,
            # иногда могут возникнуть кластеры, из-за чего
            # коэф. схожести как бы "размажется"

            only_similarity_list = analysis.compute_similarity(ohe_data, median_ohe_vector)
            similarity_list = analysis.sorted_similarity_with_tracks(tracklist, only_similarity_list)

            '''view.print_global_top_n(similarity_list, 10)

            view.print_global_bottom_n(similarity_list, 10)'''

            m_s, S2, I = analysis.compute_stats(only_similarity_list)
            view.print_math_stats(m_s, S2, I)

            global_top_artists, global_top_genres = analysis.interpret_centroid(median_ohe_vector, all_artists,
                                                                                all_genres)

            view.print_taste_dna(global_top_artists, global_top_genres, track_count, 5)

            # ТАРАНИМ КЛАСТЕРИЗАЦИЮ

            print("=" * 80)

            print("🎧 ЖАНРОВЫЙ РАЗБОР ПРИ ПОМОЩИ КЛАСТЕРИЗАЦИИ (РУЧНОЙ):")

            indices_by_genre = analysis.genres_idxs(tracklist)
            for genre, idxs in indices_by_genre.items():
                # пропускаем совсем маленькие жанры, если хочешь
                if len(idxs) < 5:
                    continue
                sims, local_centroid = analysis.analyze_by_genre(genre, idxs, ohe_data)

                local_top_artists, local_top_genres = analysis.interpret_centroid(local_centroid, all_artists,
                                                                                  all_genres)

                m_s, S2, I = analysis.compute_stats(sims)

                view.print_stats_by_genre(genre, len(idxs), m_s, S2, I)

                view.print_taste_dna(local_top_artists, local_top_genres, len(idxs), 5)

                # Топ-5 самых типичных треков внутри жанра
                sims_with_tracks = analysis.get_top_tracks(tracklist, sims, idxs)
                sims_artists = analysis.get_top_artists(sims_with_tracks)
                # view.print_top_artists_and_tracks_by_genre(sims_artists, sims_with_tracks, 5)

            #ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ

            print("⌚ ХРОНОЛОГИЕЧСКИЙ АНАЛИЗ")

            eras = analysis.split_into_eras(tracklist, ohe_data)

            filename = f"analyse_data/{playlist_title}_chron_analysis.txt"

            file_data = "⌚ ХРОНОЛОГИЕЧСКИЙ АНАЛИЗ\n"

            for era_idx, (era_tracks, era_vectors) in enumerate(eras):
                genre_counter = analysis.genre_freq_for_tracks(era_tracks)
                genre_data = view.print_era_genre_stats(era_idx, genre_counter, top_n=5)
                file_data += genre_data


                artist_counter = analysis.artist_freq_for_tracks(era_tracks)
                artists_data = view.print_era_artist_stats(era_idx, artist_counter, top_n=5)
                file_data += artists_data

                aggr, melanch = analysis.mood_counters_for_tracks(era_tracks)
                mood_data = view.print_era_mood_stats(era_idx, aggr, melanch)
                file_data += mood_data
            file_data += '=' * 80
            with open(filename, "w", encoding='utf_8') as file:
                file.write(file_data)

        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            yme.print_error(e)


if __name__ == "__main__":
    run()