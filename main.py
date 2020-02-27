import glm
import pygame

from utils import Ray, GridMap, Render


def mouse_motion(ray: Ray, event: glm.ivec2):
    ray.angle_degrees += event.x


def key_pressed(player_ray: Ray, grid: GridMap, speed: float, keys: dict):
    new_pos = glm.vec2(player_ray.origin)

    if keys[pygame.K_w]:
        new_pos += speed * player_ray.direction
    elif keys[pygame.K_s]:
        new_pos -= speed * player_ray.direction

    if keys[pygame.K_a]:
        player_ray.angle_degrees += -1
    elif keys[pygame.K_d]:
        player_ray.angle_degrees += 1

    tile_x, tile_y = new_pos / grid.cell_size
    if grid.get(int(tile_x), int(tile_y)) != grid.stop_when:
        player_ray.origin = new_pos


def display_buffer(display, buffer):
    img = pygame.image.fromstring(buffer.tobytes(), buffer.size, buffer.mode)
    display.blit(img, (0, 0))


def main(width: int, height: int):
    running = True
    player_speed = 2.0
    player_fov = glm.radians(60)
    player_ray = Ray(glm.vec2(200, 200), glm.radians(0))
    game_map = GridMap.from_file('assets/maps/10x10map.txt', 64)
    render = Render(width, height)

    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    fps_font = pygame.font.SysFont('Comic Sans MS', 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_motion(player_ray, glm.ivec2(event.rel))

        key_pressed(player_ray, game_map, player_speed, pygame.key.get_pressed())
        render.update_state(player_ray, player_fov, game_map)
        display_buffer(display, render.buffer)
        fps_overlay = fps_font.render(f'FPS {clock.get_fps():.1f}', True, pygame.Color('white'))
        display.blit(fps_overlay, (width - 90, 10))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main(640, 640)
