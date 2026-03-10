import tkinter as tk
import random
from config import *
from terrain import generate_terrain_A, generate_terrain_B
from enemy import Enemy

# -----------------------------
# GAME CLASS
# -----------------------------
class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=VISIBLE_WIDTH, height=VISIBLE_HEIGHT, bg="skyblue")
        self.canvas.pack()
        self.canvas.focus_set()  # so key presses work

        # camera
        self.cam_x = 0
        self.cam_y = 0

        self.keys = set()
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        self.menu_state = "map"  # "map" -> "difficulty" -> "game"
        self.menu_active = True
        self.map_options = ["Terrain A (Hills)", "Terrain B (Cliffs)"]
        self.diff_options = ["Easy Mode", "Normal Mode"]
        self.map_index = 0
        self.diff_index = 0
        self.terrain_choice = None
        self.difficulty_choice = None

        self.menu_items = []
        self.draw_menu()

    # -----------------------------
    # INPUT
    # -----------------------------
    def key_down(self, e):
        key = e.keysym.lower()
        self.keys.add(key)

        if self.menu_active:
            if key in ("up", "down", "return"):
                self.handle_menu_input(key)

    def key_up(self, e):
        key = e.keysym.lower()
        if key in self.keys:
            self.keys.remove(key)

    # -----------------------------
    # MENU
    # -----------------------------
    def draw_menu(self):
        self.canvas.delete("all")
        self.menu_items.clear()

        title = self.canvas.create_text(
            VISIBLE_WIDTH // 2, 120,
            text="SURVIVAL GROUNDS",
            fill="white",
            font=("Courier", 48, "bold")
        )
        self.menu_items.append(title)

        if self.menu_state == "map":
            subtitle = self.canvas.create_text(
                VISIBLE_WIDTH // 2, 220,
                text="Select Map Type",
                fill="white",
                font=("Courier", 32, "bold")
            )
            self.menu_items.append(subtitle)

            for i, text in enumerate(self.map_options):
                color = HIGHLIGHT_COLOR if i == self.map_index else NORMAL_COLOR
                item = self.canvas.create_text(
                    VISIBLE_WIDTH // 2, 320 + i * 60,
                    text=text,
                    fill=color,
                    font=("Courier", 28, "bold")
                )
                self.menu_items.append(item)

        elif self.menu_state == "difficulty":
            subtitle = self.canvas.create_text(
                VISIBLE_WIDTH // 2, 220,
                text="Select Difficulty",
                fill="white",
                font=("Courier", 32, "bold")
            )
            self.menu_items.append(subtitle)

            for i, text in enumerate(self.diff_options):
                color = HIGHLIGHT_COLOR if i == self.diff_index else NORMAL_COLOR
                item = self.canvas.create_text(
                    VISIBLE_WIDTH // 2, 320 + i * 60,
                    text=text,
                    fill=color,
                    font=("Courier", 28, "bold")
                )
                self.menu_items.append(item)

    def handle_menu_input(self, key):
        if self.menu_state == "map":
            if key == "up":
                self.map_index = (self.map_index - 1) % len(self.map_options)
                self.draw_menu()
            elif key == "down":
                self.map_index = (self.map_index + 1) % len(self.map_options)
                self.draw_menu()
            elif key == "return":
                self.terrain_choice = "A" if self.map_index == 0 else "B"
                self.menu_state = "difficulty"
                self.draw_menu()

        elif self.menu_state == "difficulty":
            if key == "up":
                self.diff_index = (self.diff_index - 1) % len(self.diff_options)
                self.draw_menu()
            elif key == "down":
                self.diff_index = (self.diff_index + 1) % len(self.diff_options)
                self.draw_menu()
            elif key == "return":
                self.difficulty_choice = "easy" if self.diff_index == 0 else "normal"
                self.menu_active = False
                self.start_game()

    # -----------------------------
    # GAME START
    # -----------------------------
    def start_game(self):
        self.canvas.delete("all")

        if self.terrain_choice == "A":
            self.world = generate_terrain_A(WORLD_WIDTH, WORLD_HEIGHT)
        else:
            self.world = generate_terrain_B(WORLD_WIDTH, WORLD_HEIGHT)

        self.draw_world()

        # scroll region for camera
        self.canvas.config(
            scrollregion=(
                0,
                0,
                WORLD_WIDTH * TILE_SIZE,
                WORLD_HEIGHT * TILE_SIZE,
            )
        )

        # spawn near the left so you can see the player
        spawn_col = 5
        ground_y = 0
        for y in range(WORLD_HEIGHT):
            if self.world[y][spawn_col] != "air":
                ground_y = y - 1
                break

        self.player = self.canvas.create_rectangle(
            spawn_col * TILE_SIZE,
            ground_y * TILE_SIZE,
            spawn_col * TILE_SIZE + TILE_SIZE,
            ground_y * TILE_SIZE + TILE_SIZE,
            fill="blue"
        )

        self.vy = 0
        self.player_hp = 1
        self.kills = 0
        self.score = 0

        self.hp_text = self.canvas.create_text(20, 20, anchor="nw", fill="white", text="HP: 1")
        self.kills_text = self.canvas.create_text(20, 60, anchor="nw", fill="white", text="Kills: 0")
        self.score_text = self.canvas.create_text(VISIBLE_WIDTH - 20, 20, anchor="ne", fill="white", text="Score: 0")

        if self.difficulty_choice == "easy":
            grunt_count = 10
            elite_count = 2
        else:
            grunt_count = 20
            elite_count = 5

        self.grunts = []
        self.elites = []

        for _ in range(grunt_count):
            self.grunts.append(self.spawn_enemy("grunt"))
        for _ in range(elite_count):
            self.elites.append(self.spawn_enemy("elite"))

        # initial camera position
        self.update_camera()
        self.tick()

    # -----------------------------
    # WORLD DRAWING
    # -----------------------------
    def draw_world(self):
        for y in range(WORLD_HEIGHT):
            for x in range(WORLD_WIDTH):
                block = self.world[y][x]
                if block != "air":
                    self.canvas.create_rectangle(
                        x * TILE_SIZE, y * TILE_SIZE,
                        (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE,
                        fill=BLOCK_COLOR[block], outline="black"
                    )

    # -----------------------------
    # ENEMY SPAWNING
    # -----------------------------
    def spawn_enemy(self, kind):
        while True:
            col = random.randint(0, WORLD_WIDTH - 1)
            ground_y = 0
            for y in range(WORLD_HEIGHT):
                if self.world[y][col] != "air":
                    ground_y = y - 1
                    break

            x = col * TILE_SIZE
            y = ground_y * TILE_SIZE

            px1, py1, px2, py2 = self.canvas.coords(self.player)
            player_center = (px1 + px2) / 2

            if abs(x - player_center) > 300:
                break

        if kind == "grunt":
            return Enemy(self.canvas, x, y, "red", 1, 10, can_jump=True)
        else:
            return Enemy(self.canvas, x, y, ELITE_COLOR, 3, 100)

    # -----------------------------
    # PLAYER HELPERS
    # -----------------------------
    def player_coords(self):
        return self.canvas.coords(self.player)

    def on_ground(self):
        x1, y1, x2, y2 = self.player_coords()
        bottom = int((y2 + 2) // TILE_SIZE)
        left = int(x1 // TILE_SIZE)
        right = int(x2 // TILE_SIZE)

        if bottom >= WORLD_HEIGHT:
            return True

        for tx in range(left, right + 1):
            if self.world[bottom][tx] != "air":
                return True
        return False

    # -----------------------------
    # COLLISION
    # -----------------------------
    def collide(self, dx, dy):
        x1, y1, x2, y2 = self.player_coords()

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
                # Only check tiles we're moving INTO
                if new_right >= WORLD_WIDTH:
                    blocked = True
                elif new_right > old_right:
                    for ty in range(top_tile, bottom_tile + 1):
                        if self.world[ty][new_right] != "air":
                            blocked = True
                            break
            else:
                # Only check tiles we're moving INTO
                if new_left < 0:
                    blocked = True
                elif new_left < old_left:
                    for ty in range(top_tile, bottom_tile + 1):
                        if self.world[ty][new_left] != "air":
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
                    if self.world[bottom_tile][tx] != "air":
                        blocked = True
                        break
            else:
                for tx in range(left_tile, right_tile + 1):
                    if self.world[top_tile][tx] != "air":
                        blocked = True
                        break

            if blocked:
                dy = 0
                self.vy = 0

        return dx, dy

    # -----------------------------
    # COMBAT
    # -----------------------------
    def attack(self):
        px1, py1, px2, py2 = self.player_coords()
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
                        self.kills += 1
                        self.score += enemy.points
                        self.canvas.itemconfig(self.kills_text, text=f"Kills: {self.kills}")
                        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    return

        hit(self.grunts, lambda: self.spawn_enemy("grunt"))
        hit(self.elites, lambda: self.spawn_enemy("elite"))

    # -----------------------------
    # ENEMY COLLISION
    # -----------------------------
    def enemy_collision(self):
        px1, py1, px2, py2 = self.player_coords()
        for enemy in self.grunts + self.elites:
            ex1, ey1, ex2, ey2 = enemy.coords()
            if not (px2 < ex1 or px1 > ex2 or py2 < ey1 or py1 > ey2):
                self.player_hp -= 1
                self.canvas.itemconfig(self.hp_text, text=f"HP: {self.player_hp}")
                if self.player_hp <= 0:
                    self.canvas.create_text(
                        VISIBLE_WIDTH // 2, VISIBLE_HEIGHT // 2,
                        text="GAME OVER", fill="red", font=("Courier", 48, "bold")
                    )
                return

    # -----------------------------
    # CAMERA
    # -----------------------------
    def update_camera(self):
        px1, py1, px2, py2 = self.player_coords()
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

        # smooth camera
        self.cam_x += (target_x - self.cam_x) * 0.1
        self.cam_y += (target_y - self.cam_y) * 0.1

        total_w = WORLD_WIDTH * TILE_SIZE
        total_h = WORLD_HEIGHT * TILE_SIZE

        if total_w > 0:
            self.canvas.xview_moveto(self.cam_x / total_w)
        if total_h > 0:
            self.canvas.yview_moveto(self.cam_y / total_h)

    # -----------------------------
    # MAIN LOOP
    # -----------------------------
    def tick(self):
        if not self.menu_active and self.player_hp > 0:
            dx = 0
            if "a" in self.keys:
                dx -= MOVE_SPEED
            if "d" in self.keys:
                dx += MOVE_SPEED
            if "w" in self.keys and self.on_ground():
                self.vy = JUMP_STRENGTH
            if "space" in self.keys:
                self.attack()

            self.vy += GRAVITY
            dy = self.vy

            dx, dy = self.collide(dx, dy)
            self.canvas.move(self.player, dx, dy)

            px1, py1, px2, py2 = self.player_coords()
            player_center_x = (px1 + px2) / 2

            for enemy in self.grunts + self.elites:
                enemy.move(self.world, player_center_x)

            for enemy_list in (self.grunts, self.elites):
                for enemy in list(enemy_list):
                    x1, y1, x2, y2 = enemy.coords()
                    if y1 > WORLD_HEIGHT * TILE_SIZE + 200:
                        enemy_list.remove(enemy)
                        if enemy_list is self.grunts:
                            enemy_list.append(self.spawn_enemy("grunt"))
                        else:
                            enemy_list.append(self.spawn_enemy("elite"))

            self.enemy_collision()
            self.update_camera()

        self.root.after(FPS_MS, self.tick)