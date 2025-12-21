import numpy as np
from collections import defaultdict

def build_ohe(tracklist, artists_map, genres_map):
    artists_count = len(artists_map)
    all_artists = list(artists_map.keys())

    genres_count = len(genres_map)
    all_genres = list(genres_map.keys())

    artist_to_idx = {artist: i for i, artist in enumerate(all_artists)}
    genre_to_idx = {genre: i for i, genre in enumerate(all_genres)}

    ohe_data = []

    for track in tracklist:
        track_artists = track[0]
        track_genre = track[2]
        split_artists = [s.strip() for s in track_artists.split(",")]

        ohe_artist = [0] * artists_count
        ohe_genre = [0] * genres_count

        for artist in split_artists:
            artist_idx = artist_to_idx[artist]
            ohe_artist[artist_idx] = 1

        genre_idx = genre_to_idx[track_genre]
        ohe_genre[genre_idx] = 1

        ohe_track = ohe_artist + ohe_genre
        ohe_data.append(ohe_track)

    return ohe_data, all_artists, all_genres

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

def global_cenroid(artists_map, genres_map, all_artists, all_genres):
    artists_count = len(artists_map)
    genres_count = len(genres_map)
    median_ohe_artist = [artists_map[artist] / artists_count for artist in all_artists]
    median_ohe_genre = [genres_map[genre] / genres_count for genre in all_genres]

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

    return sims

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

