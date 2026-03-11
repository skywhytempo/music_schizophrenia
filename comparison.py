import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from analysis import build_ohe


def compare_playlists(pl1, pl2):
    """
    Сравнивает два плейлиста (PlayList objects) в едином векторном пространстве.
    """
    # 1. Объединяем данные, чтобы создать общее пространство признаков
    # (иначе у одного будет колонка 'Artist A', а у другого нет, и векторы не совпадут)
    df1 = pl1.df.copy()
    df2 = pl2.df.copy()

    # Метки не обязательны для OHE, но удобны для разделения
    # Просто конкатенируем
    df_joint = pd.concat([df1, df2], ignore_index=True)

    # 2. Строим OHE для объединенного плейлиста
    # Теперь у нас есть колонки для всех артистов из обоих плейлистов
    features_joint = build_ohe(df_joint)

    # 3. Разделяем обратно
    n1 = len(df1)
    X1 = features_joint.iloc[:n1].values
    X2 = features_joint.iloc[n1:].values

    # 4. Считаем глобальные центроиды (вкусовые профили)
    centroid1 = np.mean(X1, axis=0).reshape(1, -1)
    centroid2 = np.mean(X2, axis=0).reshape(1, -1)

    # 5. Косинусное сходство вкусов
    # cosine_similarity возвращает матрицу [[sim]], берем [0][0]
    taste_cosine = cosine_similarity(centroid1, centroid2)[0][0]

    # 6. Jaccard (множества) - старая добрая логика, она работает отлично
    artists1 = set(pl1.artists_map.keys())
    artists2 = set(pl2.artists_map.keys())

    common_artists = artists1 & artists2
    union_artists = artists1 | artists2
    jaccard_artists = len(common_artists) / len(union_artists) if union_artists else 0.0

    genres1 = set(pl1.genres_map.keys())
    genres2 = set(pl2.genres_map.keys())

    common_genres = genres1 & genres2
    union_genres = genres1 | genres2
    jaccard_genres = len(common_genres) / len(union_genres) if union_genres else 0.0

    return {
        "taste_cosine": taste_cosine,
        "common_artists": common_artists,
        "jaccard_artists": jaccard_artists,
        "common_genres": common_genres,
        "jaccard_genres": jaccard_genres
    }
