import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict

# Импортируем только то, что реально нужно
# Если у тебя логика интерпретации осталась в analysis, импортируй её
from analysis import build_ohe, interpret_centroid, compute_stats, mood_counters_for_tracks


class Analyzer:
    def __init__(self, playlist):
        self.playlist = playlist
        self.df = playlist.df

        # Матрица признаков
        self.X_matrix = None
        self.feature_names = None

        # Центроиды
        self.global_centroid_vec = None

        # Метаданные колонок
        self.artist_cols = []
        self.genre_cols = []

    def build_ohe(self) -> None:
        """Строит матрицу OHE через Pandas"""
        # В analysis.py должна быть функция build_ohe_pandas(df) -> (df_features, artists, genres)
        # или просто df_features
        # Предположим, она возвращает DataFrame признаков:
        features_df = build_ohe(self.df)

        self.X_matrix = features_df.values
        self.feature_names = features_df.columns.tolist()

        # Разделяем колонки для красивого вывода
        # (предполагаем, что жанры начинаются с 'genre_', как договаривались)
        self.genre_cols = [c for c in self.feature_names if c.startswith('genre_')]
        self.artist_cols = [c for c in self.feature_names if not c.startswith('genre_')]

    def compute_global_centroid(self) -> None:
        if self.X_matrix is None:
            raise ValueError("OHE must be built before computing centroid")
        self.global_centroid_vec = np.mean(self.X_matrix, axis=0)

    # --------- ГЛОБАЛЬНЫЙ АНАЛИЗ -------------
    def compute_sims_stats(self) -> Dict:
        if self.global_centroid_vec is None:
            raise ValueError("Centroid needed")

        centroid_2d = self.global_centroid_vec.reshape(1, -1)
        # Считаем косинусную близость (vectorized!)
        sims = cosine_similarity(self.X_matrix, centroid_2d).flatten()

        mean, var, idx = compute_stats(sims)

        # Сразу создаем "обогащенный" DataFrame
        # (копия, чтобы не портить оригинал)
        res_df = self.df.copy()
        res_df["similarity"] = sims

        return {
            "sorted_sims": res_df.sort_values('similarity', ascending=False),
            "mean": mean,
            "var": var,
            "index_I": idx
        }

    def global_taste_dna(self) -> dict:
        return interpret_centroid(self.global_centroid_vec, self.feature_names)

    # ---------- ЖАНРОВЫЙ АНАЛИЗ (Vectorized) ------------
    def analyze_by_genre(self, genre_name):
        """
        Анализ конкретного жанра без idxs, чисто через Pandas.
        """
        # Фильтруем данные
        mask = self.df['genre'] == genre_name
        local_X = self.X_matrix[mask]

        if len(local_X) == 0:
            return None

        # Считаем локальный центроид
        local_centroid = np.mean(local_X, axis=0)

        # Считаем похожесть внутри жанра
        local_sims = cosine_similarity(local_X, local_centroid.reshape(1, -1)).flatten()
        mean, var, idx_i = compute_stats(local_sims)

        # Топ треков этого жанра по "типичности"
        genre_df = self.df[mask].copy()
        genre_df['similarity'] = local_sims
        top_tracks = genre_df.sort_values('similarity', ascending=False).head(5)

        # ДНК жанра (какие артисты там главные)
        top_artists, top_genres = interpret_centroid(local_centroid, self.feature_names)

        # Поджанры внутри жанра (value_counts делает всё сам)
        subgenre_counter = genre_df['subgenre'].value_counts()

        return {
            "mean": mean, "var": var, "index_I": idx_i,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "subgenres": subgenre_counter
        }

    # ------------- ХРОНОЛОГИЧЕСКИЙ АНАЛИЗ (Vectorized) --------------------
    def eras(self):
        """
        Разбивает плейлист на эры автоматически.
        """
        n_eras = round(len(self.df) / 100)
        # Создаем копию с колонкой эры
        res_df = self.df.copy()
        # Разбиваем на равные куски
        res_df['era'] = pd.qcut(res_df.index, q=n_eras, labels=[f"Era {i + 1}" for i in range(n_eras)])

        return res_df

    def analyze_eras_all_at_once(self):
        """
        Считает статистику по всем эрам сразу (groupby).
        """
        df_eras = self.eras()

        stats = {}
        for era_name, group in df_eras.groupby('era', observed=True):
            # Агрегация жанров
            genres = group['genre'].value_counts()

            # Агрегация артистов (сложнее из-за списков, но решаемо)
            artists = group['artists'].str.split(', ').explode().value_counts()

            # Настроение (можно оставить твой старый метод, он нормальный)
            aggr, melanch = mood_counters_for_tracks(group.to_dict('records'))

            stats[era_name] = {
                "genres": genres,
                "artists": artists,
                "mood": (aggr, melanch)
            }
        return stats

    # ------------ КЛАСТЕРИЗАЦИЯ K-MEANS ------------------
    def analyze_clusters(self, n_clusters=4):
        if self.X_matrix is None:
            raise ValueError("OHE needed")

        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(self.X_matrix)
        centroids = km.cluster_centers_

        # Добавляем метки в df
        df_clustered = self.df.copy()
        df_clustered['cluster'] = labels

        reports = []
        for i in range(n_clusters):
            # Интерпретация центра
            top_artists, top_genres = interpret_centroid(centroids[i], self.feature_names)

            # Примеры треков
            examples = df_clustered[df_clustered['cluster'] == i].head(3)

            reports.append({
                "cluster_id": i,
                "count": len(df_clustered[df_clustered['cluster'] == i]),
                "top_artists": top_artists[:3],
                "top_genres": top_genres[:3],
                "examples": examples
            })

        return reports
