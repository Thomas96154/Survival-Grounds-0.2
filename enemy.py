import math
import random
from config import BLOCK_SIZE, ENEMY_FOLLOW_RANGE, ENEMY_SPEED, ELITE_SPEED


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def terrain_height_at(x, z, terrain):
    grid_x = clamp(x / BLOCK_SIZE, 0, len(terrain) - 1)
    grid_z = clamp(z / BLOCK_SIZE, 0, len(terrain[0]) - 1)
    x0 = int(grid_x)
    z0 = int(grid_z)
    x1 = min(x0 + 1, len(terrain) - 1)
    z1 = min(z0 + 1, len(terrain[0]) - 1)
    tx = grid_x - x0
    tz = grid_z - z0
    top = terrain[x0][z0] * (1 - tx) + terrain[x1][z0] * tx
    bottom = terrain[x0][z1] * (1 - tx) + terrain[x1][z1] * tx
    return top * (1 - tz) + bottom * tz


class Enemy:
    def __init__(self, x, z, terrain_height, color, hp, points, elite=False):
        self.x = x
        self.z = z
        self.height = terrain_height
        self.y = self.height * BLOCK_SIZE + 0.4
        self.color = color
        self.hp = hp
        self.points = points
        self.elite = elite
        self.speed = ELITE_SPEED if elite else ENEMY_SPEED
        self.follow_range = ENEMY_FOLLOW_RANGE
        self.wander_angle = random.random() * 2 * math.pi
        self.wander_timer = random.uniform(1.0, 2.5)

    def move(self, target_x, target_z, terrain, frame_scale=1.0):
        dx = target_x - self.x
        dz = target_z - self.z
        distance = math.hypot(dx, dz)

        if distance < self.follow_range:
            direction_x = dx / max(distance, 0.0001)
            direction_z = dz / max(distance, 0.0001)
        else:
            self.wander_timer -= frame_scale
            if self.wander_timer <= 0.0 or distance < 0.5:
                self.wander_angle += random.uniform(-1.5, 1.5)
                self.wander_timer = random.uniform(20, 40)
            direction_x = math.cos(self.wander_angle)
            direction_z = math.sin(self.wander_angle)

        self.x += direction_x * self.speed * frame_scale
        self.z += direction_z * self.speed * frame_scale
        self.x = clamp(self.x, 0.2, (len(terrain) - 1) * BLOCK_SIZE - 0.2)
        self.z = clamp(self.z, 0.2, (len(terrain[0]) - 1) * BLOCK_SIZE - 0.2)

        self.height = terrain_height_at(self.x, self.z, terrain)
        self.y = self.height * BLOCK_SIZE + 0.4

    def damage(self, amount):
        self.hp -= amount
        return self.hp <= 0
