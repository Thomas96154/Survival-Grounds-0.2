import tkinter as tk
import ctypes
import math
import random
import time
from PIL import Image, ImageDraw, ImageTk
from config import *
from terrain import generate_heightmap_A, generate_heightmap_B
from enemy import Enemy


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def normalize(x, z):
    length = math.hypot(x, z)
    if length == 0:
        return 0.0, 0.0
    return x / length, z / length


class Game:
    def __init__(self, root):
        self.root = root
        self.window_width = root.winfo_screenwidth()
        self.window_height = root.winfo_screenheight()
        self.canvas = tk.Canvas(root, width=self.window_width, height=self.window_height, bg=SKY_COLOR)
        self.canvas.pack()
        self.root.bind('<KeyPress>', self.key_down)
        self.root.bind('<KeyRelease>', self.key_up)
        self.root.bind('<Motion>', self.mouse_move)
        self.root.bind('<Button-1>', lambda event: self.shoot())
        self.root.bind('<Escape>', lambda e: root.destroy())

        self.keys = set()
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.ignore_mouse_event = False
        self.menu_state = 'map'
        self.menu_active = True
        self.map_options = ['Terrain B (Cliffs)', 'Test Map (No Enemies)']
        self.biome_options = ['Plains', 'Desert    Not Available', 'Mountains    Not Available']
        self.map_index = 0
        self.diff_index = 0
        self.terrain_choice = None
        self.difficulty_choice = None
        self.biome_choice = None
        self.scene_image = None

        self.game_over = False
        self.player_x = BLOCK_SIZE * 2.0
        self.player_z = BLOCK_SIZE * 2.0
        self.player_y = EYE_HEIGHT
        self.yaw = 0.0
        self.pitch = 0.0
        self.velocity_y = 0.0
        self.on_ground = True
        self.last_tick_time = time.perf_counter()

        self.score = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.hit_cooldown = 0
        self.attack_effect = None

        self.world = []
        self.enemies = []

        self.draw_menu()
        self.root.after(FPS_MS, self.tick)

    def key_down(self, event):
        self.keys.add(event.keysym.lower())
        if self.menu_active:
            if event.keysym in ('Up', 'Down', 'Return'):
                self.handle_menu_input(event.keysym)
        elif self.game_over:
            if event.keysym.lower() == 'r':
                self.start_game()
        elif event.keysym.lower() == 'space':
            self.jump()

    def key_up(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys.remove(key)

    def draw_menu(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.window_width, self.window_height, fill=MENU_BG, outline='')
        self.canvas.create_text(self.window_width // 2, 100, text='SURVIVAL GROUNDS 3D', fill=HUD_COLOR, font=('Arial', 40, 'bold'))

        if self.menu_state == 'map':
            self.canvas.create_text(self.window_width // 2, 180, text='Select Map Type', fill=HUD_COLOR, font=('Arial', 26, 'bold'))
            for i, option in enumerate(self.map_options):
                color = HUD_COLOR if i == self.map_index else '#888888'
                self.canvas.create_text(self.window_width // 2, 260 + i * 40, text=option, fill=color, font=('Arial', 22))
        else:
            self.canvas.create_text(self.window_width // 2, 180, text='Select Biome', fill=HUD_COLOR, font=('Arial', 26, 'bold'))
            for i, option in enumerate(self.biome_options):
                color = HUD_COLOR if i == 0 else '#666666'
                self.canvas.create_text(self.window_width // 2, 260 + i * 40, text=option, fill=color, font=('Arial', 22))

        self.canvas.create_text(self.window_width // 2, self.window_height - 80, text='Press Enter to choose.', fill=HUD_COLOR, font=('Arial', 18))
        self.canvas.create_text(self.window_width // 2, self.window_height - 50, text='Move mouse to look around.', fill=HUD_COLOR, font=('Arial', 16))

    def handle_menu_input(self, keysym):
        if self.menu_state == 'map':
            if keysym == 'Up':
                self.map_index = (self.map_index - 1) % len(self.map_options)
                self.draw_menu()
            elif keysym == 'Down':
                self.map_index = (self.map_index + 1) % len(self.map_options)
                self.draw_menu()
            elif keysym == 'Return':
                self.terrain_choice = 'B' if self.map_index == 0 else 'TEST'
                self.menu_state = 'biome'
                self.draw_menu()
        else:
            if keysym == 'Up':
                self.diff_index = 0
            elif keysym == 'Down':
                self.diff_index = 0
            elif keysym == 'Return':
                self.biome_choice = 'plains'
                self.difficulty_choice = 'easy'
                self.menu_active = False
                self.start_game()

    def start_game(self):
        self.canvas.delete('all')
        if self.terrain_choice == 'A':
            self.world = generate_heightmap_A(WORLD_WIDTH, WORLD_DEPTH)
        else:
            self.world = generate_heightmap_B(WORLD_WIDTH, WORLD_DEPTH)

        self.player_x = BLOCK_SIZE * 2.0
        self.player_z = BLOCK_SIZE * 2.0
        self.player_y = self.get_terrain_height(self.player_x, self.player_z) * BLOCK_SIZE + EYE_HEIGHT
        self.yaw = 0.0
        self.pitch = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.root.config(cursor='none')
        self.root.update_idletasks()
        self.center_mouse()
        self.velocity_y = 0.0
        self.on_ground = True
        self.score = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.hit_cooldown = 0
        self.attack_effect = None
        self.game_over = False

        self.enemies.clear()
        if self.terrain_choice == 'TEST':
            grunt_count = 0
            elite_count = 0
        elif self.difficulty_choice == 'easy':
            grunt_count = 5
            elite_count = 1
        else:
            grunt_count = 10
            elite_count = 3

        for _ in range(grunt_count):
            self.spawn_enemy(False)
        for _ in range(elite_count):
            self.spawn_enemy(True)

        self.draw_scene()

    def respawn(self):
        self.start_game()

    def get_terrain_height(self, x, z):
        grid_x = clamp(x / BLOCK_SIZE, 0, WORLD_WIDTH - 1)
        grid_z = clamp(z / BLOCK_SIZE, 0, WORLD_DEPTH - 1)
        x0 = int(grid_x)
        z0 = int(grid_z)
        x1 = min(x0 + 1, WORLD_WIDTH - 1)
        z1 = min(z0 + 1, WORLD_DEPTH - 1)
        tx = grid_x - x0
        tz = grid_z - z0
        top = self.world[x0][z0] * (1 - tx) + self.world[x1][z0] * tx
        bottom = self.world[x0][z1] * (1 - tx) + self.world[x1][z1] * tx
        return top * (1 - tz) + bottom * tz

    def surface_height_at_grid(self, x, z):
        x_indices = {int(clamp(x - 1, 0, WORLD_WIDTH - 1)), int(clamp(x, 0, WORLD_WIDTH - 1))}
        z_indices = {int(clamp(z - 1, 0, WORLD_DEPTH - 1)), int(clamp(z, 0, WORLD_DEPTH - 1))}
        samples = [self.world[sample_x][sample_z] for sample_x in x_indices for sample_z in z_indices]
        return sum(samples) / len(samples) * BLOCK_SIZE

    def spawn_enemy(self, elite):
        attempts = 0
        while attempts < 200:
            x = random.uniform(1.0, (WORLD_WIDTH - 2) * BLOCK_SIZE)
            z = random.uniform(1.0, (WORLD_DEPTH - 2) * BLOCK_SIZE)
            if math.hypot(x - self.player_x, z - self.player_z) > 6.0:
                height = self.get_terrain_height(x, z)
                color = ELITE_COLOR if elite else ENEMY_COLOR
                hp = 3 if elite else 1
                points = 100 if elite else 10
                self.enemies.append(Enemy(x, z, height, color, hp, points, elite=elite))
                return
            attempts += 1

    def shoot(self):
        if self.menu_active or self.game_over:
            return
        sin_yaw = math.sin(self.yaw)
        cos_yaw = math.cos(self.yaw)
        sin_pitch = math.sin(self.pitch)
        cos_pitch = math.cos(self.pitch)
        fx = sin_yaw * cos_pitch
        fy = sin_pitch
        fz = cos_yaw * cos_pitch
        hits = []
        for enemy in self.enemies:
            dx = enemy.x - self.player_x
            dz = enemy.z - self.player_z
            dy = enemy.height * BLOCK_SIZE + 0.45 - self.player_y
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance > SHOOT_RANGE:
                continue
            forward_distance = dx * fx + dy * fy + dz * fz
            if forward_distance <= 0:
                continue
            ray_distance = math.sqrt(max(0.0, distance * distance - forward_distance * forward_distance))
            if ray_distance <= BLOCK_SIZE * 0.75:
                hits.append((forward_distance, enemy))
        effect_distance = SHOOT_RANGE
        if hits:
            hits.sort(key=lambda item: item[0])
            _, target = hits[0]
            effect_distance = math.sqrt(
                (target.x - self.player_x) ** 2
                + (target.height * BLOCK_SIZE + 0.45 - self.player_y) ** 2
                + (target.z - self.player_z) ** 2
            )
            if target.damage(1):
                self.enemies.remove(target)
                self.score += target.points
                self.spawn_enemy(target.elite)
        self.attack_effect = (
            self.player_x + fx * effect_distance,
            self.player_y + fy * effect_distance,
            self.player_z + fz * effect_distance,
            time.perf_counter() + 0.08,
        )

    def jump(self):
        if not self.menu_active and not self.game_over and self.on_ground:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False

    def tick(self):
        frame_start = time.perf_counter()
        elapsed = frame_start - self.last_tick_time
        self.last_tick_time = frame_start
        frame_scale = clamp(elapsed / (FPS_MS / 1000), 0.25, 3.0)
        if not self.menu_active and not self.game_over:
            self.update_game(frame_scale)
        self.draw_scene()
        frame_time_ms = (time.perf_counter() - frame_start) * 1000
        next_frame_ms = max(1, round(FPS_MS - frame_time_ms))
        self.root.after(next_frame_ms, self.tick)

    def update_game(self, frame_scale=1.0):
        self.move_player(frame_scale)
        for enemy in list(self.enemies):
            enemy.move(self.player_x, self.player_z, self.world, frame_scale)
        self.check_collisions()
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def move_player(self, frame_scale=1.0):
        direction_x = 0.0
        direction_z = 0.0
        if 'w' in self.keys:
            direction_x += math.sin(self.yaw)
            direction_z += math.cos(self.yaw)
        if 's' in self.keys:
            direction_x -= math.sin(self.yaw)
            direction_z -= math.cos(self.yaw)
        if 'a' in self.keys:
            direction_x -= math.cos(self.yaw)
            direction_z += math.sin(self.yaw)
        if 'd' in self.keys:
            direction_x += math.cos(self.yaw)
            direction_z -= math.sin(self.yaw)
        if 'left' in self.keys:
            self.yaw -= TURN_SPEED
        if 'right' in self.keys:
            self.yaw += TURN_SPEED

        direction_x, direction_z = normalize(direction_x, direction_z)
        self.player_x += direction_x * MOVE_SPEED * frame_scale
        self.player_z += direction_z * MOVE_SPEED * frame_scale
        self.player_x = clamp(self.player_x, 0.2, (WORLD_WIDTH - 1) * BLOCK_SIZE - 0.2)
        self.player_z = clamp(self.player_z, 0.2, (WORLD_DEPTH - 1) * BLOCK_SIZE - 0.2)

        ground_height = self.get_terrain_height(self.player_x, self.player_z)
        ground_y = ground_height * BLOCK_SIZE + EYE_HEIGHT
        if self.on_ground:
            self.player_y = ground_y
        else:
            self.velocity_y += GRAVITY * frame_scale
            self.player_y += self.velocity_y * frame_scale
            if self.player_y <= ground_y:
                self.player_y = ground_y
                self.velocity_y = 0.0
                self.on_ground = True

    def check_collisions(self):
        for enemy in list(self.enemies):
            distance = math.hypot(enemy.x - self.player_x, enemy.z - self.player_z)
            if distance < 0.8 and self.hit_cooldown <= 0:
                self.player_health -= 1
                self.hit_cooldown = 10
                if self.player_health <= 0:
                    self.game_over = True
                    self.menu_active = False
                    break

    def mouse_move(self, event):
        if self.menu_active or self.game_over:
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            return
        if self.ignore_mouse_event:
            self.ignore_mouse_event = False
            return
        if self.last_mouse_x is None or self.last_mouse_y is None:
            self.center_mouse()
            return
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.yaw += dx * MOUSE_SENSITIVITY
        self.pitch = clamp(self.pitch - dy * MOUSE_SENSITIVITY, -PITCH_LIMIT, PITCH_LIMIT)
        self.center_mouse()

    def center_mouse(self):
        center_x = self.window_width // 2
        center_y = self.window_height // 2
        self.last_mouse_x = center_x
        self.last_mouse_y = center_y
        self.ignore_mouse_event = True
        ctypes.windll.user32.SetCursorPos(
            self.root.winfo_rootx() + center_x,
            self.root.winfo_rooty() + center_y,
        )

    def project(self, x, y, z):
        dx = x - self.player_x
        dz = z - self.player_z
        sin_y = math.sin(self.yaw)
        cos_y = math.cos(self.yaw)
        px = dx * cos_y - dz * sin_y
        horizontal_depth = dx * sin_y + dz * cos_y
        sin_pitch = math.sin(self.pitch)
        cos_pitch = math.cos(self.pitch)
        vertical = (y - self.player_y) * cos_pitch - horizontal_depth * sin_pitch
        pz = horizontal_depth * cos_pitch + (y - self.player_y) * sin_pitch
        if pz <= 0.1:
            return None
        scale = VIEW_DISTANCE / pz
        screen_x = self.window_width / 2 + px * scale
        screen_y = self.window_height / 2 - vertical * scale
        return screen_x, screen_y, pz

    def draw_column_faces(self, x, z, height):
        x0 = x * BLOCK_SIZE
        x1 = x0 + BLOCK_SIZE
        z0 = z * BLOCK_SIZE
        z1 = z0 + BLOCK_SIZE
        y0 = 0
        top_heights = {
            'a': self.surface_height_at_grid(x, z),
            'b': self.surface_height_at_grid(x + 1, z),
            'c': self.surface_height_at_grid(x + 1, z + 1),
            'd': self.surface_height_at_grid(x, z + 1),
        }
        corners = {
            'a': self.project(x0, top_heights['a'], z0),
            'b': self.project(x1, top_heights['b'], z0),
            'c': self.project(x1, top_heights['c'], z1),
            'd': self.project(x0, top_heights['d'], z1),
            'e': self.project(x0, y0, z0),
            'f': self.project(x1, y0, z0),
            'g': self.project(x1, y0, z1),
            'h': self.project(x0, y0, z1),
        }
        if None in corners.values():
            return []
        faces = []
        grass_color = GRASS_COLORS[(x * 17 + z * 31) % len(GRASS_COLORS)]
        faces.append({'points': [corners['a'][:2], corners['b'][:2], corners['c'][:2], corners['d'][:2]], 'depth': (corners['a'][2] + corners['b'][2] + corners['c'][2] + corners['d'][2]) / 4, 'color': grass_color})
        faces.append({'points': [corners['b'][:2], corners['f'][:2], corners['g'][:2], corners['c'][:2]], 'depth': (corners['b'][2] + corners['f'][2] + corners['g'][2] + corners['c'][2]) / 4, 'color': BLOCK_COLOR_DIRT})
        faces.append({'points': [corners['d'][:2], corners['c'][:2], corners['g'][:2], corners['h'][:2]], 'depth': (corners['d'][2] + corners['c'][2] + corners['g'][2] + corners['h'][2]) / 4, 'color': BLOCK_COLOR_STONE})
        return faces

    def draw_enemy_faces(self, enemy):
        size = BLOCK_SIZE * 0.6
        x0 = enemy.x - size / 2
        x1 = enemy.x + size / 2
        z0 = enemy.z - size / 2
        z1 = enemy.z + size / 2
        y0 = enemy.height * BLOCK_SIZE
        y1 = y0 + BLOCK_SIZE * 0.9
        corners = {
            'a': self.project(x0, y1, z0),
            'b': self.project(x1, y1, z0),
            'c': self.project(x1, y1, z1),
            'd': self.project(x0, y1, z1),
            'e': self.project(x0, y0, z0),
            'f': self.project(x1, y0, z0),
            'g': self.project(x1, y0, z1),
            'h': self.project(x0, y0, z1),
        }
        if None in corners.values():
            return []
        return [
            {'points': [corners['a'][:2], corners['b'][:2], corners['c'][:2], corners['d'][:2]], 'depth': (corners['a'][2] + corners['b'][2] + corners['c'][2] + corners['d'][2]) / 4, 'color': enemy.color},
            {'points': [corners['b'][:2], corners['f'][:2], corners['g'][:2], corners['c'][:2]], 'depth': (corners['b'][2] + corners['f'][2] + corners['g'][2] + corners['c'][2]) / 4, 'color': enemy.color},
            {'points': [corners['d'][:2], corners['c'][:2], corners['g'][:2], corners['h'][:2]], 'depth': (corners['d'][2] + corners['c'][2] + corners['g'][2] + corners['h'][2]) / 4, 'color': enemy.color},
        ]

    def draw_scene(self):
        self.canvas.delete('all')
        if self.menu_active:
            self.draw_menu()
            return

        faces = []
        for x in range(WORLD_WIDTH):
            for z in range(WORLD_DEPTH):
                height = self.world[x][z]
                if height > 0:
                    faces.extend(self.draw_column_faces(x, z, height))
        for enemy in self.enemies:
            faces.extend(self.draw_enemy_faces(enemy))

        faces.sort(key=lambda item: item['depth'], reverse=True)
        scene = Image.new('RGB', (self.window_width, self.window_height), SKY_COLOR)
        scene_draw = ImageDraw.Draw(scene)
        for face in faces:
            scene_draw.polygon(face['points'], fill=face['color'])
        self.scene_image = ImageTk.PhotoImage(scene)
        self.canvas.create_image(0, 0, image=self.scene_image, anchor='nw')

        if self.attack_effect is not None:
            effect_x, effect_y, effect_z, effect_end = self.attack_effect
            if time.perf_counter() < effect_end:
                endpoint = self.project(effect_x, effect_y, effect_z)
                if endpoint is not None:
                    center_x = self.window_width // 2
                    center_y = self.window_height // 2
                    origin_y = self.window_height * 0.8
                    self.canvas.create_line(
                        center_x,
                        origin_y,
                        endpoint[0],
                        endpoint[1],
                        fill='#FBC02D',
                        width=10,
                    )
                    self.canvas.create_line(
                        center_x,
                        origin_y,
                        endpoint[0],
                        endpoint[1],
                        fill='#FFFDE7',
                        width=4,
                    )
            else:
                self.attack_effect = None

        center_x = self.window_width // 2
        center_y = self.window_height // 2
        self.canvas.create_line(center_x - 10, center_y, center_x + 10, center_y, fill=HUD_COLOR, width=2)
        self.canvas.create_line(center_x, center_y - 10, center_x, center_y + 10, fill=HUD_COLOR, width=2)

        hud = f'HP: {self.player_health}   Score: {self.score}   W/A/S/D move, mouse look, Space jump, Left click attack'
        self.canvas.create_text(20, 20, text=hud, fill=HUD_COLOR, anchor='nw', font=('Arial', 16, 'bold'))
        if self.game_over:
            self.canvas.create_text(self.window_width // 2, self.window_height // 2, text='GAME OVER', fill='red', font=('Arial', 44, 'bold'))
            self.canvas.create_text(self.window_width // 2, self.window_height // 2 + 50, text='Press R to restart', fill=HUD_COLOR, font=('Arial', 20))

    def draw_column_faces(self, x, z, height):
        x0 = x * BLOCK_SIZE
        x1 = x0 + BLOCK_SIZE
        z0 = z * BLOCK_SIZE
        z1 = z0 + BLOCK_SIZE
        y0 = 0
        y1 = height * BLOCK_SIZE
        corners = {
            'a': self.project(x0, y1, z0),
            'b': self.project(x1, y1, z0),
            'c': self.project(x1, y1, z1),
            'd': self.project(x0, y1, z1),
            'e': self.project(x0, y0, z0),
            'f': self.project(x1, y0, z0),
            'g': self.project(x1, y0, z1),
            'h': self.project(x0, y0, z1),
        }
        if any(value is None for value in corners.values()):
            return []
        faces = []
        grass_color = GRASS_COLORS[(x * 17 + z * 31) % len(GRASS_COLORS)]
        faces.append({'points': [corners['a'][:2], corners['b'][:2], corners['c'][:2], corners['d'][:2]], 'depth': sum(c[2] for c in (corners['a'], corners['b'], corners['c'], corners['d'])) / 4, 'color': grass_color})
        faces.append({'points': [corners['b'][:2], corners['f'][:2], corners['g'][:2], corners['c'][:2]], 'depth': sum(c[2] for c in (corners['b'], corners['f'], corners['g'], corners['c'])) / 4, 'color': BLOCK_COLOR_DIRT})
        faces.append({'points': [corners['d'][:2], corners['c'][:2], corners['g'][:2], corners['h'][:2]], 'depth': sum(c[2] for c in (corners['d'], corners['c'], corners['g'], corners['h'])) / 4, 'color': BLOCK_COLOR_STONE})
        return faces

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
        
    def draw_enemy_faces(self, enemy):
        size = BLOCK_SIZE * 0.6
        x0 = enemy.x - size / 2
        x1 = enemy.x + size / 2
        z0 = enemy.z - size / 2
        z1 = enemy.z + size / 2
        y0 = enemy.height * BLOCK_SIZE
        y1 = y0 + BLOCK_SIZE * 0.9
        corners = {
            'a': self.project(x0, y1, z0),
            'b': self.project(x1, y1, z0),
            'c': self.project(x1, y1, z1),
            'd': self.project(x0, y1, z1),
            'e': self.project(x0, y0, z0),
            'f': self.project(x1, y0, z0),
            'g': self.project(x1, y0, z1),
            'h': self.project(x0, y0, z1),
        }
        if any(value is None for value in corners.values()):
            return []
        return [
            {'points': [corners['a'][:2], corners['b'][:2], corners['c'][:2], corners['d'][:2]], 'depth': sum(c[2] for c in (corners['a'], corners['b'], corners['c'], corners['d'])) / 4, 'color': enemy.color},
            {'points': [corners['b'][:2], corners['f'][:2], corners['g'][:2], corners['c'][:2]], 'depth': sum(c[2] for c in (corners['b'], corners['f'], corners['g'], corners['c'])) / 4, 'color': enemy.color},
            {'points': [corners['d'][:2], corners['c'][:2], corners['g'][:2], corners['h'][:2]], 'depth': sum(c[2] for c in (corners['d'], corners['c'], corners['g'], corners['h'])) / 4, 'color': enemy.color},
        ]
