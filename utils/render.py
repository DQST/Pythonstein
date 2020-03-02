from dataclasses import dataclass, field
from typing import Tuple, List, Optional

import glm
import numpy as np
from PIL import ImageDraw, ImageColor

from utils.gridmap import GridMap
from utils.hit import Hit
from utils.ray import Ray

COLOR_RED = ImageColor.getrgb('red')
COLOR_GRAY = ImageColor.getrgb('gray')
COLOR_GREEN = ImageColor.getrgb('green')
COLOR_WHITE = ImageColor.getrgb('white')
COLOR_BLACK = ImageColor.getrgb('black')
COLOR_YELLOW = ImageColor.getrgb('yellow')


@dataclass
class Render:
    width: int
    height: int
    background: Tuple[int, ...] = COLOR_BLACK
    help_map_size: glm.ivec2 = glm.ivec2(200, 200)

    _buffer: np.ndarray = field(init=False)
    _back_buffer: np.ndarray = field(init=False)

    def __post_init__(self):
        self._buffer = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        self._back_buffer = np.zeros((self.width, self.height, 3), dtype=np.uint8)

    def swap_buffers(self):
        self._buffer, self._back_buffer = self._back_buffer, self._buffer

    def clear_buffer(self, draw: ImageDraw.ImageDraw, box: Optional[Tuple[int, int, int, int]] = None):
        if not box:
            box = (0, 0, self.width, self.height)
        draw.rectangle(box, self.background)

    def draw_help_map(self,
                      ray_origin: glm.vec2,
                      grid: GridMap,
                      scale: glm.ivec2,
                      hits: List[Hit]):
        scale = scale / grid.size
        for x in range(grid.size.x):
            for y in range(grid.size.y):
                xx, yy = x * scale.x, y * scale.y
                value = chr(grid.get(x, y))
                if value == ' ':
                    continue
                self._back_buffer[yy:yy + scale.y, xx:xx + scale.x] = COLOR_RED

        player = glm.ivec2(glm.floor(ray_origin / grid.cell_size * scale))
        self._back_buffer[player.y - 1:player.y + 1, player.x - 1:player.x + 1] = COLOR_WHITE
        # for hit in hits:
        #     point = hit.point / grid.cell_size * scale
        #     draw.line((*player, *point), COLOR_YELLOW)

    def draw_scene(self,
                   player_radians: float,
                   projection_plane: float,
                   wall_height: int,
                   hits: List[Hit], grid: GridMap):
        min_val = 0
        y = self.height / 2
        max_val = self.height - 1
        precomputed = wall_height * projection_plane
        for x, hit in enumerate(hits):
            correct_distance = hit.length * glm.cos(hit.radians - player_radians)
            column_height = precomputed / correct_distance
            h1, h2 = glm.ivec2(glm.floor(glm.clamp(glm.vec2(y - column_height, y + column_height), min_val, max_val)))
            self._back_buffer[h1:h2, x] = COLOR_GRAY

    def update_state(self, ray: Ray, fov: float, grid: GridMap):
        self._back_buffer[:] = self.background

        hits = grid.ray_casting(self.width, fov, ray)

        self.draw_scene(ray.radians, 277, grid.cell_size, hits, grid)
        # self.draw_help_map(ray.origin, grid, self.help_map_size, hits)

        self.swap_buffers()

    @property
    def size(self):
        return self.width, self.height

    @property
    def buffer(self):
        return self._back_buffer.swapaxes(0, 1)
