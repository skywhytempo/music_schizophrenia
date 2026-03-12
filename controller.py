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

                            # Передаем во View
                            file_data += view.print_era_genre_stats(len(eras_stats) - i, Counter(genre_counter), total, top_n=5)
                            file_data += view.print_era_artist_stats(len(eras_stats) - i, Counter(artist_counter), total, top_n=5)
                            file_data += "\n"
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

        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            yme.print_error(e)

if __name__ == "__main__":
    run()