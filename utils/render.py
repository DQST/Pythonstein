from dataclasses import dataclass, field
from typing import Tuple, List

import glm
from PIL import Image, ImageDraw, ImageColor

from utils.gridmap import GridMap
from utils.hit import Hit
from utils.player import Player


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

    _buffer: Image.Image = field(init=False)
    _back_buffer: Image.Image = field(init=False)
    _min_map: Image.Image = field(init=False)

    def __post_init__(self):
        self._buffer = Image.new('RGB', (self.width, self.height), self.background)
        self._back_buffer = Image.new('RGB', (self.width, self.height), self.background)
        self._min_map = Image.new('RGB', (self.width, self.height), self.background)

    def _swap_buffers(self):
        self._buffer, self._back_buffer = self._back_buffer, self._buffer

    def _clear_buffer(self, draw: ImageDraw.ImageDraw):
        draw.rectangle((0, 0, self.width, self.height), self.background)

    def _draw_line(self, x1, y1, x2, y2, color):
        data = self._back_buffer.load()
        for y in range(y1, y2):
            data[x1, y] = color

    @staticmethod
    def _draw_help_map(draw: ImageDraw.ImageDraw,
                       ray_origin: glm.vec2,
                       grid: GridMap,
                       scale: glm.ivec2,
                       points: List[glm.vec2]):
        scale = scale / grid.size
        for x in range(grid.size.x):
            for y in range(grid.size.y):
                xx, yy = x * scale.x, y * scale.y
                if grid.get(x, y) == ord('#'):
                    draw.rectangle((xx, yy, xx + scale.x, yy + scale.y), fill=COLOR_RED)
                else:
                    draw.rectangle((xx, yy, xx + scale.x, yy + scale.y), outline=COLOR_GREEN)

        player = ray_origin / grid.cell_size * scale
        draw.rectangle((*(player - 1), *(player + 1)), COLOR_WHITE)
        for point in points:
            point = point / grid.cell_size * scale
            draw.line((*player, *point), COLOR_YELLOW)

    def _draw_scene(self, draw: ImageDraw.ImageDraw, ray_radians, wall_height: int, hits: List[Hit]):
        for x, hit in enumerate(hits):
            if hit is not None:
                correct_distance = hit.length * glm.cos(hit.radians - ray_radians)
                column_height = wall_height / correct_distance * 277
                y1 = self.height / 2 - column_height / 2
                draw.line((x, y1, x, y1 + column_height), COLOR_GRAY)

    def update_state(self, ray: Player, fov: float, grid: GridMap):
        draw = ImageDraw.Draw(self._back_buffer)
        self._clear_buffer(draw)

        hits = grid.ray_casting(self.width, fov, ray)

        self._draw_scene(draw, ray.radians, grid.cell_size, hits)
        self._draw_help_map(draw, ray.origin, grid, glm.ivec2(200, 200), [i.point for i in hits])

        self._swap_buffers()

    @property
    def buffer(self):
        return self._buffer
