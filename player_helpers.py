from config import *


def player_coords(game):
    return game.canvas.coords(game.player)


def on_ground(game):
    x1, y1, x2, y2 = player_coords(game)
    bottom = int((y2 + 2) // TILE_SIZE)
    left = int(x1 // TILE_SIZE)
    right = int(x2 // TILE_SIZE)

    if bottom >= WORLD_HEIGHT:
        return True

    for tx in range(left, right + 1):
        if game.world[bottom][tx] != "air":
            return True
    return False


def collide(game, dx, dy):
    x1, y1, x2, y2 = player_coords(game)

    # Horizontal
    if dx != 0:
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
            if new_right >= WORLD_WIDTH:
                blocked = True
            elif new_right > old_right:
                for ty in range(top_tile, bottom_tile + 1):
                    if game.world[ty][new_right] != "air":
                        blocked = True
                        break
        else:
            if new_left < 0:
                blocked = True
            elif new_left < old_left:
                for ty in range(top_tile, bottom_tile + 1):
                    if game.world[ty][new_left] != "air":
                        blocked = True
                        break

        if blocked:
            dx = 0

    # Vertical
    if dy != 0:
        new_y1 = y1 + dy
        new_y2 = y2 + dy
        left_tile = int(x1 // TILE_SIZE)
        right_tile = int(x2 // TILE_SIZE)
        top_tile = int(new_y1 // TILE_SIZE)
        bottom_tile = int(new_y2 // TILE_SIZE)

        blocked = False
        if dy > 0:
            for tx in range(left_tile, right_tile + 1):
                if game.world[bottom_tile][tx] != "air":
                    blocked = True
                    break
        else:
            for tx in range(left_tile, right_tile + 1):
                if game.world[top_tile][tx] != "air":
                    blocked = True
                    break

        if blocked:
            dy = 0
            game.vy = 0

    return dx, dy


def attack(game):
    px1, py1, px2, py2 = player_coords(game)
    center_x = (px1 + px2) / 2

    def hit(enemies, respawn):
        for enemy in list(enemies):
            ex1, ey1, ex2, ey2 = enemy.coords()
            enemy_center = (ex1 + ex2) / 2

            if abs(enemy_center - center_x) <= ATTACK_RANGE:
                dead = enemy.damage(1)
                if dead:
                    enemies.remove(enemy)
                    enemies.append(respawn())
                    game.kills += 1
                    game.score += enemy.points
                    game.canvas.itemconfig(game.kills_text, text=f"Kills: {game.kills}")
                    game.canvas.itemconfig(game.score_text, text=f"Score: {game.score}")
                return

    hit(game.grunts, lambda: game.spawn_enemy("grunt"))
    hit(game.elites, lambda: game.spawn_enemy("elite"))
