import random
from enemy import Enemy
from config import *


def spawn_enemy(game, kind):
    px1, py1, px2, py2 = game.canvas.coords(game.player)
    player_center = (px1 + px2) / 2

    attempts = 0
    while attempts < 1000:
        col = random.randint(0, WORLD_WIDTH - 1)
        ground_y = 0
        for y in range(WORLD_HEIGHT):
            if game.world[y][col] != "air":
                ground_y = y - 1
                break

        x = col * TILE_SIZE
        y = ground_y * TILE_SIZE

        if abs(x - player_center) > 300:
            break
        attempts += 1

    if attempts >= 1000:
        # Fallback to a distant edge if a safe spawn can't be found.
        if player_center < WORLD_WIDTH * TILE_SIZE / 2:
            col = WORLD_WIDTH - 1
        else:
            col = 0

        ground_y = 0
        for y in range(WORLD_HEIGHT):
            if game.world[y][col] != "air":
                ground_y = y - 1
                break
        x = col * TILE_SIZE
        y = ground_y * TILE_SIZE

    if kind == "grunt":
        return Enemy(game.canvas, x, y, "red", 1, 10, can_jump=True)
    else:
        return Enemy(game.canvas, x, y, ELITE_COLOR, 3, 100)


def enemy_collision(game):
    px1, py1, px2, py2 = game.canvas.coords(game.player)
    for enemy in game.grunts + game.elites:
        ex1, ey1, ex2, ey2 = enemy.coords()
        if not (px2 < ex1 or px1 > ex2 or py2 < ey1 or py1 > ey2):
            game.player_hp -= 1
            game.canvas.itemconfig(game.hp_text, text=f"HP: {game.player_hp}")
            if game.player_hp <= 0:
                game.game_over_text = game.canvas.create_text(
                    VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2,
                    text="GAME OVER", fill="red", font=("Courier", 48, "bold")
                )
                game.game_over = True
            return
