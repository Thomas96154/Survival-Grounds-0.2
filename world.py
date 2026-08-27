from config import *


def draw_world(game):
    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            block = game.world[y][x]
            if block != "air":
                game.canvas.create_rectangle(
                    x * TILE_SIZE, y * TILE_SIZE,
                    (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE,
                    fill=BLOCK_COLOR[block], outline="black"
                )
