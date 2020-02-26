from dataclasses import dataclass

import glm


@dataclass
class Hit:
    length: float
    radians: float
    point: glm.vec2
