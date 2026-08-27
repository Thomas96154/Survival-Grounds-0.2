from terrain import generate_terrain_A, generate_terrain_B
from config import *


def generate_terrain(game, choice: str):
    if choice == "A":
        return generate_terrain_A(WORLD_WIDTH, WORLD_HEIGHT)
    return generate_terrain_B(WORLD_WIDTH, WORLD_HEIGHT)


def draw_world(game) -> None:
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            block = game.world[y][x]
            if block != "air":
                game.canvas.create_rectangle(
                    x * TILE_SIZE, y * TILE_SIZE,
                    (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE,
                    fill=BLOCK_COLOR[block], outline="black"
                )
