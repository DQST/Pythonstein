from dataclasses import dataclass
from typing import ClassVar, Dict, List

import numpy as np
from PIL import Image


@dataclass
class TextureAtlas:
    _textures: List['Texture']

    def __len__(self):
        return len(self._textures)

    def __getitem__(self, item) -> 'Texture':
        return self._textures[item]


@dataclass
class Texture:
    data: np.ndarray
    width: int
    height: int

    def slice(self, x: int, y: int, w: int, h: int) -> 'Texture':
        data = self.data[y: h, x: w]
        h, w = data.shape[:2]
        return Texture(data, w, h)

    def to_atlas(self, offset: int) -> TextureAtlas:
        textures = []
        for y in range(0, self.height, offset):
            for x in range(0, self.width, offset):
                width = x + offset
                height = y + offset
                texture = self.slice(x, y, width, height)
                textures.append(texture)
        return TextureAtlas(textures)

    def rescale_column(self, column: int, new_height: int):
        data = self.data[:, column]
        y_ration = int((self.height << 16) / new_height) + 1
        return np.array([data[(i * y_ration) >> 16] for i in range(new_height)], dtype=np.uint8)


@dataclass
class TextureLoader:
    _data: ClassVar[Dict[str, Texture]] = dict()

    @classmethod
    def load(cls, path: str) -> Texture:
        if path not in cls._data:
            data = np.array(Image.open(path), dtype=np.uint8)
            height, width = data.shape[:2]
            cls._data[path] = Texture(data, width, height)
        return cls._data[path]
