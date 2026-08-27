from config import *


def update_camera(game):
    px1, py1, px2, py2 = game.player_coords()
    center_x = (px1 + px2) / 2
    center_y = (py1 + py2) / 2

    target_x = center_x - VISIBLE_WIDTH / 2
    target_y = center_y - VISIBLE_HEIGHT / 2

    max_x = WORLD_WIDTH * TILE_SIZE - VISIBLE_WIDTH
    max_y = WORLD_HEIGHT * TILE_SIZE - VISIBLE_HEIGHT

    if max_x < 0:
        max_x = 0
    if max_y < 0:
        max_y = 0

    target_x = max(0, min(max_x, target_x))
    target_y = max(0, min(max_y, target_y))

    game.cam_x += (target_x - game.cam_x) * 0.1
    game.cam_y += (target_y - game.cam_y) * 0.1

    total_w = WORLD_WIDTH * TILE_SIZE
    total_h = WORLD_HEIGHT * TILE_SIZE

    if total_w > 0:
        game.canvas.xview_moveto(game.cam_x / total_w)
    if total_h > 0:
        game.canvas.yview_moveto(game.cam_y / total_h)
