from typing import List, Dict, Any, Tuple
import numpy as np

from OOP_structure.PlayListData import PlayList
from analysis import global_centroid


def cosine(a, b) -> float:
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    num = np.dot(a, b)
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if den == 0 else num / den

def build_joint_data(
    tracklist1: List[tuple],
    artists_map1: Dict[str, int],
    genres_map1: Dict[str, int],
    tracklist2: List[tuple],
    artists_map2: Dict[str, int],
    genres_map2: Dict[str, int],
):
    all_artists = set(artists_map1.keys()) | set(artists_map2.keys())
    all_genres = set(genres_map1.keys()) | set(genres_map2.keys())

    artist_to_idx = {artist: i for i, artist in enumerate(all_artists)}
    genre_to_idx = {genre: i for i, genre in enumerate(all_genres)}

    def build_ohe_with_vocab(tracklist):
        artists_count = len(artist_to_idx)
        genres_count = len(genre_to_idx)
        ohe_data = []

        for track in tracklist:
            artists_str = track[0]
            grouped_genre = track[2]  # укрупнённый жанр

            split_artists = [s.strip() for s in artists_str.split(",")]

            ohe_artist = [0] * artists_count
            ohe_genre = [0] * genres_count

            for artist in split_artists:
                idx = artist_to_idx.get(artist)
                if idx is not None:
                    ohe_artist[idx] = 1

            gidx = genre_to_idx.get(grouped_genre)
            if gidx is not None:
                ohe_genre[gidx] = 1

            ohe_track = ohe_artist + ohe_genre
            ohe_data.append(ohe_track)

        return ohe_data

    ohe1 = build_ohe_with_vocab(tracklist1)
    ohe2 = build_ohe_with_vocab(tracklist2)

    return all_artists, all_genres, ohe1, ohe2

def compare_playlists(pl1: PlayList, pl2: PlayList) -> Dict[str, Any]:
    """
    Возвращает словарь с:
      - taste_cosine: косинусное сходство глобальных центроидов
      - common_artists, jaccard_artists
      - common_genres, jaccard_genres
    """
    all_artists, all_genres, ohe1, ohe2 = build_joint_data(
        pl1.tracklist, pl1.artists_map, pl1.genres_map,
        pl2.tracklist, pl2.artists_map, pl2.genres_map,
    )

    # посчитаем центроиды в общем пространстве
    track_count1 = len(pl1.tracklist)
    track_count2 = len(pl2.tracklist)

    # расширяем карты до общего словаря (отсутствующие → 0)
    artists_map1 = {a: pl1.artists_map.get(a, 0) for a in all_artists}
    genres_map1 = {g: pl1.genres_map.get(g, 0) for g in all_genres}

    artists_map2 = {a: pl2.artists_map.get(a, 0) for a in all_artists}
    genres_map2 = {g: pl2.genres_map.get(g, 0) for g in all_genres}

    centroid1 = global_centroid(artists_map1, genres_map1, all_artists, all_genres, track_count1)
    centroid2 = global_centroid(artists_map2, genres_map2, all_artists, all_genres, track_count2)

    taste_sim = cosine(centroid1, centroid2)

    # пересечение артистов/жанров (по исходным картам)
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
        "taste_cosine": taste_sim,
        "centroid1": centroid1,
        "centroid2": centroid2,
        "common_artists": common_artists,
        "jaccard_artists": jaccard_artists,
        "common_genres": common_genres,
        "jaccard_genres": jaccard_genres,
    }

