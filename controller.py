import yme
import analysis
import view
import comparison
from OOP_structure.Analyzer import Analyzer
from OOP_structure.PlayListData import PlayList


def run():

    yme.send_welcome()

    while True:

        try:

            uri_raw = input("\nВведите ссылку на плейлист: ")

            music_data = yme.handle_message(uri_raw)

            playlist = PlayList(*music_data)
            analyzer = Analyzer(playlist)

            track_count = playlist.track_count

            #yme.print_results(music_data)

            #print(playlist)

            #ohe_data, all_artists, all_genres = analysis.build_ohe(tracklist, artists_map, genres_map)

            analyzer.build_ohe()

            analyzer.compute_global_centroid()


            while True:

                choice = view.show_menu()


                match choice:
                    case "1":
                        stats = analyzer.compute_sims_stats()
                        top_stats = analyzer.global_taste_dna()

                        global_top_artists = top_stats["top_artists"]
                        global_top_genres = top_stats["top_genres"]

                        view.print_taste_dna(global_top_artists, global_top_genres, track_count, 5)

                    case "2":
                        print("🎧 ЖАНРОВЫЙ РАЗБОР ПРИ ПОМОЩИ КЛАСТЕРИЗАЦИИ (РУЧНОЙ):")

                        indices_by_genre = analyzer.genre_indices()
                        for genre, idxs in indices_by_genre.items():
                            # пропускаем совсем маленькие жанры, если хочешь
                            if len(idxs) < 5:
                                continue

                            '''sims, local_centroid = analysis.analyze_by_genre(genre, idxs, ohe_data)
        
                            local_top_artists, local_top_genres = analysis.interpret_centroid(local_centroid, all_artists,
                                                                                              all_genres)
        
                            m_s, S2, I = analysis.compute_stats(sims)'''

                            genre_stats = analyzer.analyze_by_genre(genre, idxs)

                            subgenres_stats = genre_stats["subgenres"]

                            subgenres_stats = [(subgenre, subgenres_stats[subgenre] / len(idxs)) for subgenre in
                                               subgenres_stats]

                            subgenres_stats = sorted(subgenres_stats, key=lambda x: x[1], reverse=True)

                            local_top_artists = genre_stats["top_artists"]

                            m_s = genre_stats["mean"]
                            S2 = genre_stats["var"]
                            I = genre_stats["index_I"]

                            # view.print_stats_by_genre(genre, len(idxs), m_s, S2, I)

                            view.print_taste_genre_dna(genre, local_top_artists, subgenres_stats, len(idxs), 5)

                    case "3":
                        # ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ

                        print("⌚ ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ")

                        eras = analyzer.eras()
                        filename = f"analyse_data/{playlist.title}_chron_analysis.txt"

                        file_data = "⌚ ХРОНОЛОГИЕЧСКИЙ АНАЛИЗ\n"

                        for era_idx, (era_tracks, era_vectors) in enumerate(eras):
                            era_stats = analyzer.analyze_era(era_tracks)
                            genre_counter = era_stats["genre_counter"]
                            genre_data = view.print_era_genre_stats(era_idx, genre_counter, top_n=5)
                            file_data += genre_data

                            artist_counter = era_stats["artist_counter"]
                            artists_data = view.print_era_artist_stats(era_idx, artist_counter, top_n=5)
                            file_data += artists_data

                            aggr = era_stats["aggressive_words"]
                            melanch = era_stats["melancholic_words"]
                            mood_data = view.print_era_mood_stats(era_idx, aggr, melanch)
                            file_data += mood_data
                        file_data += '=' * 80
                        with open(filename, "w", encoding='utf_8') as file:
                            file.write(file_data)

                    case "4":
                        other_playlist_url = input("\nВведите ссылку на плейлист: ")

                        other_music_data = yme.handle_message(other_playlist_url)

                        other_playlist = PlayList(*other_music_data)

                        result = comparison.compare_playlists(playlist, other_playlist)
                        view.print_playlist_comparison(result, playlist.title, other_playlist.title)

                    case "0":
                        break

                    case _:
                        print("Неверный ввод!\n")




            # Формируем центроиду
            #median_ohe_vector = analysis.global_centroid(artists_map, genres_map, all_artists, all_genres, track_count)

            # Глобальный анализ - может быть не очень эффективно, ведь,
            # иногда могут возникнуть кластеры, из-за чего
            # коэф. схожести как бы "размажется"

            '''only_similarity_list = analysis.compute_similarity(ohe_data, median_ohe_vector)
            similarity_list = analysis.sorted_similarity_with_tracks(tracklist, only_similarity_list)

            view.print_global_top_n(similarity_list, 10)

            view.print_global_bottom_n(similarity_list, 10)

            m_s, S2, I = analysis.compute_stats(only_similarity_list)
            view.print_math_stats(m_s, S2, I)

            global_top_artists, global_top_genres = analysis.interpret_centroid(median_ohe_vector, all_artists,
                                                                                all_genres)'''

            '''stats = analyzer.compute_sims_stats()
            top_stats = analyzer.global_taste_dna()

            global_top_artists = top_stats["top_artists"]
            global_top_genres = top_stats["top_genres"]

            view.print_taste_dna(global_top_artists, global_top_genres, track_count, 5)'''

            # ТАРАНИМ КЛАСТЕРИЗАЦИЮ

            '''print("=" * 80)

            print("🎧 ЖАНРОВЫЙ РАЗБОР ПРИ ПОМОЩИ КЛАСТЕРИЗАЦИИ (РУЧНОЙ):")

            indices_by_genre = analyzer.genre_indices()
            for genre, idxs in indices_by_genre.items():
                # пропускаем совсем маленькие жанры, если хочешь
                if len(idxs) < 5:
                    continue
                sims, local_centroid = analysis.analyze_by_genre(genre, idxs, ohe_data)

                local_top_artists, local_top_genres = analysis.interpret_centroid(local_centroid, all_artists,
                                                                                  all_genres)

                m_s, S2, I = analysis.compute_stats(sims)

                genre_stats = analyzer.analyze_by_genre(genre, idxs)

                subgenres_stats = genre_stats["subgenres"]

                subgenres_stats = [(subgenre, subgenres_stats[subgenre]/len(idxs)) for subgenre in subgenres_stats]

                subgenres_stats = sorted(subgenres_stats, key=lambda x: x[1], reverse=True)

                local_top_artists = genre_stats["top_artists"]

                m_s = genre_stats["mean"]
                S2 = genre_stats["var"]
                I = genre_stats["index_I"]


                #view.print_stats_by_genre(genre, len(idxs), m_s, S2, I)

                view.print_taste_genre_dna(genre, local_top_artists, subgenres_stats, len(idxs), 5)'''


                # Топ-5 самых типичных треков внутри жанра
                #sims_with_tracks = analysis.get_top_tracks(tracklist, sims, idxs)
                #sims_artists = analysis.get_top_artists(sims_with_tracks)
                # view.print_top_artists_and_tracks_by_genre(sims_artists, sims_with_tracks, 5)

            #ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ

            '''print("⌚ ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ")

            eras = analyzer.eras()
            filename = f"analyse_data/{playlist.title}_chron_analysis.txt"

            file_data = "⌚ ХРОНОЛОГИЕЧСКИЙ АНАЛИЗ\n"

            for era_idx, (era_tracks, era_vectors) in enumerate(eras):
                era_stats = analyzer.analyze_era(era_tracks)
                genre_counter = era_stats["genre_counter"]
                genre_data = view.print_era_genre_stats(era_idx, genre_counter, top_n=5)
                file_data += genre_data


                artist_counter = era_stats["artist_counter"]
                artists_data = view.print_era_artist_stats(era_idx, artist_counter, top_n=5)
                file_data += artists_data

                aggr = era_stats["aggressive_words"]
                melanch = era_stats["melancholic_words"]
                mood_data = view.print_era_mood_stats(era_idx, aggr, melanch)
                file_data += mood_data
            file_data += '=' * 80
            with open(filename, "w", encoding='utf_8') as file:
                file.write(file_data)'''

            

        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            yme.print_error(e)

if __name__ == "__main__":
    run()