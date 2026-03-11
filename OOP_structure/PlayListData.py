import pandas as pd
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PlayList:
    df: pd.DataFrame
    title: str

    # Кэшируем карты, чтобы не считать каждый раз (опционально)
    _artists_map: Dict[str, int] = field(default=None, init=False, repr=False)
    _genres_map: Dict[str, int] = field(default=None, init=False, repr=False)

    @property
    def track_count(self) -> int:
        return len(self.df)

    @property
    def artists_map(self) -> Dict[str, int]:
        if self._artists_map is None:
            # Магия Pandas: разбиваем строки "Art1, Art2" и считаем
            self._artists_map = (
                self.df['artists']
                .str.split(', ')
                .explode()
                .value_counts()
                .to_dict()
            )
        return self._artists_map

    @property
    def genres_map(self) -> Dict[str, int]:
        if self._genres_map is None:
            self._genres_map = self.df['genre'].value_counts().to_dict()
        return self._genres_map

    @property
    def artists_count(self) -> int:
        return len(self.artists_map)

    @property
    def genres_count(self) -> int:
        return len(self.genres_map)

    def __str__(self):
        # Используем pandas для красивого вывода топов
        top_genres = list(self.genres_map.items())[:5]
        top_artists = list(self.artists_map.items())[:5]

        # Формируем строки (можно сделать красивее, но пока сохраним логику)
        tg_str = "\n".join([f" {g}: {c}" for g, c in top_genres])
        ta_str = "\n".join([f" {a}: {c}" for a, c in top_artists])

        return (
            f"Плейлист {self.title}\n"
            f"Треков: {self.track_count}\n"
            f"Артистов: {self.artists_count}\n"
            f"Жанров: {self.genres_count}\n\n"
            f"🎸 ТОП ЖАНРОВ:\n{tg_str}\n\n"
            f"🎤 ТОП АРТИСТОВ:\n{ta_str}\n"
        )
