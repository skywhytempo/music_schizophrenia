import yme
import analysis
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

@dataclass
class PlayList:

    tracklist: List[tuple]
    artists_map: Dict[str, int]
    genres_map: Dict[str, int]
    title: str

    @property
    def track_count(self) -> int:
        return len(self.tracklist)

    @property
    def artists_count(self) -> int:
        return len(self.artists_map)

    @property
    def genres_count(self) -> int:
        return len(self.genres_map)

    def __init__(self, tracklist, artists_map, genres_map, title):
        self.tracklist = tracklist
        self.artists_map = artists_map
        self.genres_map = genres_map
        self.title = title


    def __str__(self):
        top_genres_string = ""

        top_genres_string += "🎸 ТОП 5 ЖАНРОВ (ПО КОЛИЧЕСТВУ ТРЕКОВ)\n"

        top_genres = list(self.genres_map.keys())[:5]

        for genre in top_genres:
            top_genres_string += f" {genre}: {self.genres_map[genre]} трек(а/ов)\n"

        top_artists_string = ""

        top_artists_string += "🎤 ТОП 5 АРТИСТОВ (ПО КОЛИЧЕСТВУ ТРЕКОВ)\n"

        top_artists = list(self.artists_map.keys())[:5]

        for artist in top_artists:
            top_artists_string += f" {artist}: {self.artists_map[artist]} трек(а/ов)\n"

        return (f"Плейлист {self.title}, Число трек(а/ов): {self.track_count}\n"
                f"Число уникальных артистов: {self.artists_count}\n"
                f"Число уникальных жанров: {self.genres_count}\n"
                f"\n{top_genres_string}\n"
                f"{top_artists_string}\n"
                )