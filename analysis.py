import numpy as np
from collections import defaultdict
from collections import Counter

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

def build_ohe(df):

    genre_dummies = pd.get_dummies(df["genre"]).add_prefix('genre_')
    all_genres = genre_dummies.columns.tolist()

    artists_series = df['artists'].str.split(', ')
    mlb = MultiLabelBinarizer()
    artists_matrix = mlb.fit_transform(artists_series)
    all_artists = mlb.classes_.tolist()
    artists_df = pd.DataFrame(artists_matrix, columns=all_artists)

    ohe_data = pd.concat([artists_df, genre_dummies], axis=1)
    return ohe_data

def get_similarity_to_median(vector, median_vector):
    scalar = np.dot(vector, median_vector)
    norms = np.linalg.norm(vector) * np.linalg.norm(median_vector)
    sim_coef = scalar / norms

    return round(sim_coef, 4)

def cosine(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    num = np.dot(a, b)
    den = np.linalg.norm(a) * np.linalg.norm(b)
    if den == 0:
        return 0.0
    return num / den

def centroid(vectors):
    return np.mean(np.array(vectors, dtype=float), axis=0)

def global_centroid(artists_map, genres_map, all_artists, all_genres, track_count):
    median_ohe_artist = [artists_map[artist] / track_count for artist in all_artists]
    median_ohe_genre = [genres_map[genre] / track_count for genre in all_genres]

    median_ohe_vector = median_ohe_artist + median_ohe_genre
    return median_ohe_vector

def compute_similarity(ohe_data, median_ohe_vector):
    sim_list = []
    for i in range(len(ohe_data)):
        track_vector = ohe_data[i]
        sim_coef = get_similarity_to_median(track_vector, median_ohe_vector)
        sim_list.append(sim_coef)
    return sim_list

def compute_stats(sim_list):
    mean = sum(sim_list) / len(sim_list)
    if len(sim_list) > 1:
        var = sum((s - mean) ** 2 for s in sim_list) / (len(sim_list) - 1)
    else:
        var = 0.0
    index_I = (1 - mean) * (var)**0.5
    return mean, var, index_I

def sorted_similarity_with_tracks(tracklist, sims_list):
    sorted_arr = []
    for i in range(len(tracklist)):
        track = tracklist[i]
        sim = sims_list[i]
        sorted_arr.append((track, sim))
    sorted_arr = sorted(sorted_arr, key=lambda x: x[1], reverse=True)
    return sorted_arr

def genres_idxs(tracklist):
    indices_by_genre = defaultdict(list)
    for i, track in enumerate(tracklist):
        genre = track[2]  # уже сгруппированный жанр из handle_message
        indices_by_genre[genre].append(i)
    return indices_by_genre

def analyze_by_genre(genre, idxs, ohe_data):

    genre_vecs = [ohe_data[i] for i in idxs]
    genre_centroid = centroid(genre_vecs)

    sims = [cosine(ohe_data[i], genre_centroid) for i in idxs]

    return sims, genre_centroid

def subgenre_freq_for_cluster(tracklist, idxs):
    counter = Counter()
    for i in idxs:
        track = tracklist[i]
        raw_genre = track[3]  # сырой жанр
        counter[raw_genre] += 1
    return counter

def get_top_tracks(tracklist, sim_list, idxs):
    sim_tracks = [(tracklist[i], sim_list[k]) for k, i in enumerate(idxs)]
    sim_tracks.sort(key=lambda x: x[1], reverse=True)
    return sim_tracks

def get_top_artists(sim_tracks):
    sims_artists = {}

    for track, s in sim_tracks:
        split_artist = track[0].split(",")
        for artist in split_artist:
            artist = artist.strip()
            sims_artists[artist] = sims_artists.get(artist, 0) + 1

    sort_sims_artists = {}
    for key in sorted(sims_artists, key=sims_artists.get):
        sort_sims_artists[key] = sims_artists[key]

    sims_sort_artists = dict(reversed(sort_sims_artists.items()))

    return sims_sort_artists

def interpret_centroid(median_vector, feature_names):
    all_genres = [c for c in feature_names if c.startswith('genre_')]
    all_artists = [c for c in feature_names if not c.startswith('genre_')]
    # Разделяем вектор
    n_artists = len(all_artists)
    artist_weights = median_vector[:n_artists]
    genre_weights = median_vector[n_artists:]

    # Собираем пары (Имя, Вес)
    artists_with_weights = []
    for i, weight in enumerate(artist_weights):
        if weight > 0:
            artists_with_weights.append((all_artists[i], weight))

    genres_with_weights = []
    for i, weight in enumerate(genre_weights):
        if weight > 0:
            genres_with_weights.append((all_genres[i], weight))

    # Сортируем
    top_artists = sorted(artists_with_weights, key=lambda x: x[1], reverse=True)
    top_genres = sorted(genres_with_weights, key=lambda x: x[1], reverse=True)

    return top_artists, top_genres

def split_into_eras(tracklist, ohe_data):
    n = len(tracklist)
    #n_eras = n // 100
    n_eras = 3
    era_size = n // n_eras
    eras = []

    for era_idx in range(n_eras):
        start = era_idx * era_size
        end = (era_idx + 1) * era_size if era_idx < n_eras - 1 else n
        era_tracks = tracklist[start:end]
        era_vectors = ohe_data[start:end]
        eras.append((era_tracks, era_vectors))
    return eras

def genre_freq_for_tracks(era_tracks):
    counter = Counter()
    for track in era_tracks:
        genre = track[2]
        counter[genre] += 1
    return counter

def artist_freq_for_tracks(era_tracks):
    counter = Counter()
    for track in era_tracks:
        artists_str = track[0]  # "Artist1, Artist2"
        artists = [a.strip() for a in artists_str.split(",")]
        for artist in artists:
            if artist:
                counter[artist] += 1
    return counter




