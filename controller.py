import yme
import analysis
import view
import comparison
from OOP_structure.Analyzer import Analyzer
from OOP_structure.PlayListData import PlayList
from collections import Counter


def run():

    yme.send_welcome()

    while True:

        try:

            uri_raw = input("\nВведите ссылку на плейлист: ")

            df, title = yme.handle_message(uri_raw)

            playlist = PlayList(df, title)
            analyzer = Analyzer(playlist)

            analyzer.build_ohe()

            analyzer.compute_global_centroid()


            while True:

                choice = view.show_menu()


                match choice:
                    case "1":
                        stats = analyzer.compute_sims_stats()

                        # 2. Получаем "ДНК вкуса"
                        top_stats = analyzer.global_taste_dna()
                        global_top_artists = top_stats[0] # interpret_centroid возвращает (artists, genres)
                        global_top_genres = top_stats[1]

                        # 3. Адаптируем данные для View
                        # View ждет список кортежей треков.
                        # stats["sorted_sims"] - это DataFrame. Превратим его в список кортежей (Artist, Title, Genre)
                        top_tracks_df = stats["sorted_sims"].head(10)
                        # Важно: View ждет (track, sim), где track=(art, tit, gen).
                        # Соберем это вручную:
                        sim_list_for_view = []
                        for _, row in top_tracks_df.iterrows():
                            track_tuple = (row['artists'], row['title'], row['genre'])
                            sim_list_for_view.append((track_tuple, row['similarity']))

                        # Выводим
                        view.print_taste_dna(global_top_artists, global_top_genres, playlist.track_count, 5)

                        # Можно добавить вывод топа треков, если View это умеет
                        view.print_global_top_n(sim_list_for_view, 10)

                        view.print_math_stats(stats["mean"], stats["var"], stats["index_I"])

                    case "2":
                        print("🎧 ЖАНРОВЫЙ РАЗБОР (PANDAS VERSION):")

                        # Получаем все уникальные жанры из DF
                        unique_genres = playlist.df['genre'].unique()

                        for genre in unique_genres:
                            # Пропускаем совсем редкие жанры (меньше 5 треков)
                            genre_count = len(playlist.df[playlist.df['genre'] == genre])
                            if genre_count < 5:
                                continue

                            # Вызываем анализ (теперь это быстро!)
                            g_stats = analyzer.analyze_by_genre(genre)
                            if not g_stats: continue

                            # Достаем данные
                            m_s = g_stats["mean"]
                            S2 = g_stats["var"]
                            I = g_stats["index_I"]
                            local_top_artists = g_stats["top_artists"]

                            # Поджанры: это Series, превратим в список кортежей для View
                            # (Subgenre, Count) -> нужно (Subgenre, Frequency)
                            sub_series = g_stats["subgenres"]  # Series
                            subgenres_list = []
                            total_in_genre = sub_series.sum()
                            for subg, count in sub_series.items():
                                subgenres_list.append((subg, count / total_in_genre, count))

                            # Сортируем
                            subgenres_list.sort(key=lambda x: x[1], reverse=True)

                            # Вывод
                            view.print_stats_by_genre(genre, genre_count, m_s, S2, I)
                            view.print_taste_genre_dna(genre, local_top_artists, subgenres_list, genre_count, 5)

                    case "3":
                        # ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ
                        print("⌚ ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ")

                        # Используем новый метод, который считает всё сразу
                        eras_stats = analyzer.analyze_eras_all_at_once()




                        filename = f"analyse_data/{playlist.title}_chron_analysis.txt"
                        file_data = "⌚ ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ\n"

                        # eras_stats это словарь { "Era 1": {...}, ... }
                        for i, (era_name, data) in enumerate(eras_stats.items()):
                            # View ждет Counter, а у нас Series.
                            # Series.to_dict() отлично подходит как замена Counter!
                            genre_counter = data["genres"].to_dict()  # {Genre: Count}
                            total = sum(genre_counter.values())
                            artist_counter = data["artists"].to_dict()
                            #aggr, melanch = data["mood"]

                            # Передаем во View
                            file_data += view.print_era_genre_stats(len(eras_stats) - i, Counter(genre_counter), total, top_n=5)
                            file_data += view.print_era_artist_stats(len(eras_stats) - i, Counter(artist_counter), total, top_n=5)
                            file_data += "\n"
                            #file_data += view.print_era_mood_stats(i, aggr, melanch)
                            file_data += '=' * 80

                        with open(filename, "w", encoding='utf_8') as file:
                            file.write(file_data)
                        print(f"Данные сохранены в {filename}")

                    case "4":

                        clusters_data = analyzer.analyze_clusters(4)

                        view.print_kmeans_clusters(clusters_data)

                    case "5":
                        other_playlist_url = input("\nВведите ссылку на плейлист: ")

                        other_music_data, title = yme.handle_message(other_playlist_url)

                        other_playlist = PlayList(other_music_data, title)

                        result = comparison.compare_playlists(playlist, other_playlist)

                        view.print_playlist_comparison(result, playlist.title, other_playlist.title)

                    case "0":
                        return

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