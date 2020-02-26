from dataclasses import dataclass, field

import glm
import numpy as np

from utils.hit import Hit
from utils.player import Player


@dataclass
class GridMap:
    size: glm.ivec2
    cell_size: int
    stop_when: int = ord('#')
    __data: np.ndarray = field(init=False)

    def __post_init__(self):
        self.__data = np.full(self.size, fill_value=0, dtype=np.int)

    def get(self, x: int, y: int) -> int:
        return self.__data[y, x]

    def set(self, x: int, y: int, value: int):
        self.__data[y, x] = value

    @classmethod
    def from_array(cls, array, cell_size: int) -> 'GridMap':
        width, height = len(array[0]), len(array)
        obj = cls(glm.ivec2(width, height), cell_size)
        obj.__data = np.array(array, dtype=np.int)
        return obj

    @classmethod
    def from_file(cls, path: str, cell_size: int) -> 'GridMap':
        with open(path) as file:
            array = [[ord(i) for i in line.strip()] for line in file if len(line) > 1]
            return cls.from_array(array, cell_size)

    def _is_out_of_range(self, x: float, y: float):
        width, height = self.size
        return x >= width or x < 0 or y >= height or y < 0

    def _to_tile_coords(self, x: float, y: float) -> glm.ivec2:
        x = glm.floor(x / self.cell_size)
        y = glm.floor(y / self.cell_size)
        return glm.ivec2(x, y)

    @staticmethod
    def _box_ray_intersection(ray: 'Player', box_min: glm.vec2, box_max: glm.vec2):
        inv_dir = ray.inverse_direction
        lo = inv_dir.x * (box_min.x - ray.origin.x)
        hi = inv_dir.x * (box_max.x - ray.origin.x)
        # t_min = min(lo, hi)
        t_max = max(lo, hi)
        lo1 = inv_dir.y * (box_min.y - ray.origin.y)
        hi1 = inv_dir.y * (box_max.y - ray.origin.y)
        # t_min = max(t_min, min(lo1, hi1))
        t_max = min(t_max, max(lo1, hi1))

        return t_max + 1

    def ray_travers(self, ray: 'Player') -> Hit:
        current = ray.origin
        while True:
            tile = self._to_tile_coords(*current)
            box_min = tile * self.cell_size
            box_max = box_min + self.cell_size
            t = self._box_ray_intersection(ray, box_min, box_max)

            if self._is_out_of_range(*tile) or self.get(*tile) == self.stop_when:
                length = glm.distance(current, ray.origin)
                return Hit(length, ray.radians, current)
            current = ray.origin + t * ray.direction

    def ray_casting(self, width: int, fov: float, ray: Player):
        start_angle = ray.radians - fov / 2
        return [self.ray_travers(Player(ray.origin, start_angle + fov * x / width)) for x in range(width)]

    def __iter__(self):
        return np.nditer(self.__data)
