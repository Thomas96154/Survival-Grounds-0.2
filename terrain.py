import random
from config import WORLD_WIDTH, WORLD_DEPTH, MAX_HEIGHT

# -----------------------------
# HEIGHTMAP GENERATION
# -----------------------------

def generate_heightmap_A(width, depth):
    base = MAX_HEIGHT // 2 + 1
    heights = [[base for _ in range(depth)] for _ in range(width)]

    for x in range(width):
        for z in range(depth):
            if x == 0:
                heights[x][z] = max(1, min(MAX_HEIGHT, base + random.choice([-1, 0, 0, 0, 1])))
            else:
                previous = heights[x - 1][z]
                heights[x][z] = max(1, min(MAX_HEIGHT, previous + random.choice([-1, 0, 0, 0, 1])))

    for _ in range(2):
        smoothed = [row[:] for row in heights]
        for x in range(width):
            for z in range(depth):
                neighbors = [heights[x][z]]
                if x > 0:
                    neighbors.append(heights[x - 1][z])
                if x < width - 1:
                    neighbors.append(heights[x + 1][z])
                if z > 0:
                    neighbors.append(heights[x][z - 1])
                if z < depth - 1:
                    neighbors.append(heights[x][z + 1])
                smoothed[x][z] = round(sum(neighbors) / len(neighbors))
        heights = smoothed

    return heights


def generate_heightmap_B(width, depth):
    base = MAX_HEIGHT // 2 + 1
    heights = [[base for _ in range(depth)] for _ in range(width)]

    for x in range(width):
        for z in range(depth):
            previous = heights[x - 1][z] if x > 0 else base
            delta = random.choice([-1, 0, 0, 0, 1])
            heights[x][z] = max(1, min(MAX_HEIGHT, previous + delta))

        if random.random() < 0.08:
            z = random.randint(0, depth - 1)
            heights[x][z] = max(1, min(MAX_HEIGHT, heights[x][z] + random.choice([-1, 1])))

    for _ in range(2):
        smoothed = [row[:] for row in heights]
        for x in range(width):
            for z in range(depth):
                neighbors = [heights[x][z]]
                if x > 0:
                    neighbors.append(heights[x - 1][z])
                if x < width - 1:
                    neighbors.append(heights[x + 1][z])
                if z > 0:
                    neighbors.append(heights[x][z - 1])
                if z < depth - 1:
                    neighbors.append(heights[x][z + 1])
                smoothed[x][z] = round(sum(neighbors) / len(neighbors))
        heights = smoothed

    return heights
