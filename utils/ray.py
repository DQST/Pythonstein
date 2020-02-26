from dataclasses import dataclass

import glm


@dataclass
class Ray:
    origin: glm.vec2
    radians: float

    @property
    def direction(self):
        v = self.origin + 1 * glm.vec2(glm.cos(self.radians), glm.sin(self.radians))
        return glm.normalize(v - self.origin)

    @property
    def inverse_direction(self):
        return 1 / self.direction

    @property
    def angle_degrees(self):
        return glm.degrees(float(self.radians))

    @angle_degrees.setter
    def angle_degrees(self, value):
        if self.angle_degrees > 360:
            value = 0
        if value < 0:
            value = 360
        self.radians = glm.radians(value)
