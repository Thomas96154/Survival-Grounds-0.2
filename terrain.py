import random
from config import WORLD_WIDTH, WORLD_HEIGHT

# -----------------------------
# TERRAIN GENERATION
# -----------------------------
def generate_terrain_A(width, height):
    """Flat-ish hills"""
    world = []
    base = height // 2
    variation = 0
    heights = []

    for x in range(width):
        variation += random.choice([-1, 0, 1])
        variation = max(-3, min(3, variation))
        h = base + variation
        h = max(3, min(height - 4, h))
        heights.append(h)

    for y in range(height):
        row = []
        for x in range(width):
            ground = heights[x]
            if y < ground:
                row.append("air")
            elif y == ground:
                row.append("grass")
            elif y <= ground + 2:
                row.append("dirt")
            else:
                row.append("stone")
        world.append(row)
    return world


def generate_terrain_B(width, height):
    """Cliffs and drops (hard)"""
    world = []
    base = height // 2
    heights = []
    h = base

    for x in range(width):
        h += random.choice([-3, -2, -1, 0, 1, 2, 3])
        h = max(3, min(height - 4, h))
        heights.append(h)

    for y in range(height):
        row = []
        for x in range(width):
            ground = heights[x]
            if y < ground:
                row.append("air")
            elif y == ground:
                row.append("grass")
            elif y <= ground + 3:
                row.append("dirt")
            else:
                row.append("stone")
        world.append(row)
    return world