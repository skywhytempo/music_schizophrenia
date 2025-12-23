import analysis
from typing import List, Tuple, Dict, Any

class Analyzer:
    def __init__(self, playlist):
        self.playlist = playlist
        self.ohe_data: List[List[float]] | None = None
        self.all_artists: List[str] | None = None
        self.all_genres: List[str] | None = None
        self.global_centroid_vec: List[float] | None = None

    def artist_set(self):
        return set(self.all_artists)

    def genre_set(self):
        return set(self.all_genres)

    #---------ПОДГОТОКА ДАННЫХ, ВЫЧИСЛЕНИЕ МАТ.ПАРАМЕТРОВ-----------------

    #Огромный OHE-вектор плейлиста
    def build_ohe(self) -> None:
        ohe_data, all_artists, all_genres = analysis.build_ohe(
            self.playlist.tracklist,
            self.playlist.artists_map,
            self.playlist.genres_map
        )

        self.ohe_data = ohe_data
        self.all_artists = all_artists
        self.all_genres = all_genres

    #Выборочный средний OHE-вектор плейлиста
    def compute_global_centroid(self) -> None:
        if self.all_artists is None or self.all_genres is None:
            raise ValueError("OHE must be built before computing centroid")

        self.global_centroid_vec = analysis.global_centroid(
            self.playlist.artists_map,
            self.playlist.genres_map,
            self.all_artists,
            self.all_genres,
            self.playlist.track_count
        )
    #---------ГЛОБААЛЬНЫЙ АНАЛИЗ-------------

    def compute_sims_stats(self) -> Dict:
        if self.ohe_data is None or self.global_centroid_vec is None:
            raise ValueError("OHE and centroid must be computed first")

        sims = analysis.compute_similarity(self.ohe_data, self.global_centroid_vec)
        sorted_sims = analysis.sorted_similarity_with_tracks(self.playlist.tracklist, sims)
        mean, var, idx = analysis.compute_stats(sims)

        return {
            "sorted_sims": sorted_sims,
            "sims": sims,
            "mean": mean,
            "var": var,
            "index_I": idx
        }

    def global_taste_dna(self) -> dict:
        """
        Топ-артисты и жанры для глобальной центроиды.
        """
        if self.global_centroid_vec is None or self.all_artists is None or self.all_genres is None:
            raise ValueError("Centroid and OHE metadata must be ready")

        top_artists, top_genres = analysis.interpret_centroid(
            self.global_centroid_vec,
            self.all_artists,
            self.all_genres,
        )
        return {
            "top_artists": top_artists,
            "top_genres": top_genres,
        }

    #----------ЖАНРОВЫЙ АНАЛИЗ------------

    def genre_indices(self):
        return analysis.genres_idxs(self.playlist.tracklist)

    def analyze_by_genre(self, genre, idxs):
        if self.ohe_data is None:
            raise ValueError("OHE must be built before genre analysis")
        sims, genre_centroid = analysis.analyze_by_genre(genre, idxs, self.ohe_data)
        mean, var, idx = analysis.compute_stats(sims)
        sim_tracks = analysis.get_top_tracks(self.playlist.tracklist, sims, idxs)
        top_artists, top_genres = analysis.interpret_centroid(genre_centroid, self.all_artists, self.all_genres)
        subgenre_counter = analysis.subgenre_freq_for_cluster(self.playlist.tracklist, idxs)


        return {
            "genre": genre,
            "indices": idxs,
            "sims": sims,
            "mean": mean,
            "var": var,
            "index_I": idx,
            "centroid": genre_centroid,
            "top_tracks": sim_tracks,
            "top_artists": top_artists,
            "top_genres": top_genres,
            "subgenres": subgenre_counter
        }

    #-------------ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ--------------------

    def eras(self):
        """
               Возвращает список эра-данных: [(era_tracks, era_vectors), ...]
               """
        if self.ohe_data is None:
            raise ValueError("OHE must be built before era analysis")

        # analysis.split_into_eras пока зашит на 3 эры,
        # при желании можно туда добавить параметр n_eras.
        return analysis.split_into_eras(self.playlist.tracklist, self.ohe_data)

    def analyze_era(self, era_tracks):
        """
                Анализ одной эры: жанры, артисты, настроение.
                """
        genre_counter = analysis.genre_freq_for_tracks(era_tracks)
        artist_counter = analysis.artist_freq_for_tracks(era_tracks)
        aggr, melanch = analysis.mood_counters_for_tracks(era_tracks)

        return {
            "genre_counter": genre_counter,
            "artist_counter": artist_counter,
            "aggressive_words": aggr,
            "melancholic_words": melanch,
        }











