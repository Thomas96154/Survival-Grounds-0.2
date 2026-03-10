import random
from config import TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT, GRAVITY, JUMP_STRENGTH

# -----------------------------
# ENEMY CLASS
# -----------------------------
class Enemy:
    def __init__(self, canvas, x, y, color, hp, points, can_jump=False):
        self.canvas = canvas
        self.hp = hp
        self.max_hp = hp
        self.points = points
        self.vy = 0
        self.speed = 3
        self.id = canvas.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE, fill=color)
        self.dir = random.choice([-1, 1])
        self.follow_range = 600
        self.can_jump = can_jump
        self.jump_cooldown = 0

    def coords(self):
        return self.canvas.coords(self.id)

    def on_ground(self, world):
        x1, y1, x2, y2 = self.coords()
        bottom = int((y2 + 2) // TILE_SIZE)
        left = int(x1 // TILE_SIZE)
        right = int(x2 // TILE_SIZE)

        if bottom >= WORLD_HEIGHT:
            return True

        for tx in range(left, right + 1):
            if world[bottom][tx] != "air":
                return True
        return False

    def move(self, world, player_x):
        x1, y1, x2, y2 = self.coords()
        center = (x1 + x2) / 2

        # FOLLOW PLAYER
        if abs(center - player_x) < self.follow_range:
            self.dir = 1 if player_x > center else -1

        dx = self.dir * self.speed

        # HORIZONTAL COLLISION
        new_x1 = x1 + dx
        new_x2 = x2 + dx
        old_left = int(x1 // TILE_SIZE)
        old_right = int(x2 // TILE_SIZE)
        new_left = int(new_x1 // TILE_SIZE)
        new_right = int(new_x2 // TILE_SIZE)
        top_tile = int(y1 // TILE_SIZE)
        bottom_tile = int(y2 // TILE_SIZE)

        blocked = False
        if dx > 0:
            # Only check tiles we're moving INTO
            if new_right >= WORLD_WIDTH:
                blocked = True
            elif new_right > old_right:
                for ty in range(top_tile, bottom_tile + 1):
                    if world[ty][new_right] != "air":
                        blocked = True
                        break
        else:
            # Only check tiles we're moving INTO
            if new_left < 0:
                blocked = True
            elif new_left < old_left:
                for ty in range(top_tile, bottom_tile + 1):
                    if world[ty][new_left] != "air":
                        blocked = True
                        break

        if blocked:
            dx = 0
            self.dir *= -1

        self.canvas.move(self.id, dx, 0)

        # JUMPING (for grunts)
        self.jump_cooldown = max(0, self.jump_cooldown -1)
        if self.can_jump and self.on_ground(world) and self.jump_cooldown == 0:
            if random.random() < 0.02:  # 2% chance each frame
                self.vy = JUMP_STRENGTH
                self.jump_cooldown = 30  # cooldown so they don't spam jump

        # VERTICAL COLLISION + GRAVITY
        self.vy += GRAVITY
        dy = self.vy

        x1, y1, x2, y2 = self.coords()
        new_y1 = y1 + dy
        new_y2 = y2 + dy
        left_tile = int(x1 // TILE_SIZE)
        right_tile = int(x2 // TILE_SIZE)
        top_tile = int(new_y1 // TILE_SIZE)
        bottom_tile = int(new_y2 // TILE_SIZE)

        blocked = False
        if dy > 0:
            if bottom_tile >= WORLD_HEIGHT:
                blocked = True
            else:
                for tx in range(left_tile, right_tile + 1):
                    if world[bottom_tile][tx] != "air":
                        blocked = True
                        break
        else:
            if top_tile < 0:
                blocked = True
            else:
                for tx in range(left_tile, right_tile + 1):
                    if world[top_tile][tx] != "air":
                        blocked = True
                        break

        if blocked:
            dy = 0
            self.vy = 0

        self.canvas.move(self.id, 0, dy)

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.canvas.delete(self.id)
            return True
        return False