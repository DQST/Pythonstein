from dataclasses import dataclass, field
from typing import Tuple, List, Optional

import glm
from PIL import Image, ImageDraw, ImageColor

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

    _buffer: Image.Image = field(init=False)
    _back_buffer: Image.Image = field(init=False)

    def __post_init__(self):
        self._buffer = Image.new('RGB', (self.width, self.height), self.background)
        self._back_buffer = Image.new('RGB', (self.width, self.height), self.background)

    def swap_buffers(self):
        self._buffer, self._back_buffer = self._back_buffer, self._buffer

    def clear_buffer(self, draw: ImageDraw.ImageDraw, box: Optional[Tuple[int, int, int, int]] = None):
        if not box:
            box = (0, 0, self.width, self.height)
        draw.rectangle(box, self.background)

    def draw_help_map(self,
                      draw: ImageDraw.ImageDraw,
                      ray_origin: glm.vec2,
                      grid: GridMap,
                      scale: glm.ivec2,
                      hits: List[Hit]):
        self.clear_buffer(draw, (0, 0, scale.x, scale.y))
        scale = scale / grid.size
        for x in range(grid.size.x):
            for y in range(grid.size.y):
                xx, yy = x * scale.x, y * scale.y
                value = grid.get(x, y)
                if value == ord(' '):
                    draw.rectangle((xx, yy, xx + scale.x, yy + scale.y), outline=COLOR_GREEN)
                else:
                    color = COLOR_RED
                    if value < len(grid.texture_atlas):
                        texture = grid.texture_atlas[value]
                        color = tuple(texture.data[0, 0])
                    draw.rectangle((xx, yy, xx + scale.x, yy + scale.y), fill=color)

        player = ray_origin / grid.cell_size * scale
        draw.rectangle((*(player - 1), *(player + 1)), COLOR_WHITE)
        for hit in hits:
            point = hit.point / grid.cell_size * scale
            draw.line((*player, *point), COLOR_YELLOW)

    def draw_scene(self,
                   draw: ImageDraw.ImageDraw,
                   player_radians: float,
                   projection_plane: float,
                   wall_height: int,
                   hits: List[Hit]):
        y = self.height / 2
        precomputed = wall_height * projection_plane
        for x, hit in enumerate(hits):
            correct_distance = hit.length * glm.cos(hit.radians - player_radians)
            column_height = precomputed / correct_distance
            draw.line((x, y - column_height, x, y + column_height), COLOR_GRAY)

    @property
    def draw(self):
        return ImageDraw.Draw(self._back_buffer)

    def update_state(self, ray: Ray, fov: float, grid: GridMap):
        draw = self.draw
        self.clear_buffer(draw)

        hits = grid.ray_casting(self.width, fov, ray)

        self.draw_scene(draw, ray.radians, 277, grid.cell_size, hits)
        self.draw_help_map(draw, ray.origin, grid, self.help_map_size, hits)

        self.swap_buffers()

    @property
    def buffer(self):
        return self._buffer
