import pygame
import sys
import math
import random
import json
import os

# --- Game Setup ---
pygame.init()
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stug.io Tank Game Prototype")
CLOCK = pygame.time.Clock()
FPS = 60

# --- Colors ---
BG_COLOR = (36, 37, 46)
TANK_COLOR = (80, 200, 120)
TANK_FRONT_COLOR = (130, 230, 180)
TURRET_COLOR = (100, 230, 160)
BULLET_COLOR = (245, 245, 80)
WALL_COLOR = (60, 70, 80)
BUTTON_COLOR = (70, 80, 120)
BUTTON_HOVER_COLOR = (100, 120, 170)
BUTTON_TEXT_COLOR = (255, 255, 255)

# --- Tank Settings ---
TANK_SIZE = (40, 30)
TANK_SPEED = 4
TANK_ROT_SPEED = 3.2
TURRET_LENGTH = 32

# --- Bullet Settings ---
BULLET_RADIUS = 6
BULLET_SPEED = 10

# --- Arena Walls ---
WALLS = [
    pygame.Rect(0, 0, WIDTH, 20),
    pygame.Rect(0, 0, 20, HEIGHT),
    pygame.Rect(WIDTH-20, 0, 20, HEIGHT),
    pygame.Rect(0, HEIGHT-20, WIDTH, 20)
]

# --- Button Class ---
class Button:
    def __init__(self, rect, text, onclick, font_size=36):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.font = pygame.font.SysFont(None, font_size)
        self.hovered = False
        self.clicked = False

    def draw(self, surf):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        txt_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surf.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.hovered and event.button == 1 and self.clicked:
                self.onclick()
            self.clicked = False

# --- Game Classes ---
class RicochetEffect:
    def __init__(self, pos, size, opacity, duration):
        self.pos = pos
        self.size = size
        self.opacity = opacity
        self.duration = duration
        self.timer = 0

    def update(self, dt):
        self.timer += dt

    def draw(self, surf):
        alpha = int(self.opacity * 255 * max(0, 1 - self.timer / self.duration))
        if alpha <= 0:
            return
        effect_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(effect_surf, (255, 140, 40, alpha), (self.size // 2, self.size // 2), self.size // 2)
        surf.blit(effect_surf, (self.pos[0] - self.size // 2, self.pos[1] - self.size // 2))

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.turret_angle = 0
        self.width, self.height = TANK_SIZE
        self.speed = 0

    def move(self, keys):
        if keys[pygame.K_w]:
            self.speed = TANK_SPEED
        elif keys[pygame.K_s]:
            self.speed = -TANK_SPEED
        else:
            self.speed = 0
        if keys[pygame.K_a]:
            self.angle -= TANK_ROT_SPEED
        if keys[pygame.K_d]:
            self.angle += TANK_ROT_SPEED
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.x += dx
        self.y += dy
        self.x = max(20, min(self.x, WIDTH - 20))
        self.y = max(20, min(self.y, HEIGHT - 20))

    def get_center(self):
        return (int(self.x), int(self.y))

    def update_turret(self, mouse_pos):
        cx, cy = self.get_center()
        mx, my = mouse_pos
        self.turret_angle = math.atan2(my - cy, mx - cx)

    def draw(self, surf):
        hull = pygame.Surface(TANK_SIZE, pygame.SRCALPHA)
        hull.fill(TANK_COLOR)
        pygame.draw.rect(hull, TANK_FRONT_COLOR, (self.width - 10, 5, 10, self.height - 10), border_radius=4)
        hull = pygame.transform.rotate(hull, -self.angle)
        rect = hull.get_rect(center=self.get_center())
        surf.blit(hull, rect.topleft)
        cx, cy = self.get_center()
        tx = cx + math.cos(self.turret_angle) * TURRET_LENGTH
        ty = cy + math.sin(self.turret_angle) * TURRET_LENGTH
        pygame.draw.line(surf, TURRET_COLOR, (cx, cy), (tx, ty), 8)
        pygame.draw.circle(surf, TURRET_COLOR, (int(cx), int(cy)), 10)

class Bullet:
    def __init__(self, pos, angle):
        self.x, self.y = pos
        self.angle = angle
        self.speed = BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.active = True
        self.bounce_count = 0
        self.ricochet_modifier = 2.0
        self.death_effect_triggered = False

    def move(self):
        if not self.active:
            return
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        wall_normal = None
        if next_x - self.radius <= 20:
            wall_normal = (1, 0)
            next_x = 20 + self.radius
        elif next_x + self.radius >= WIDTH - 20:
            wall_normal = (-1, 0)
            next_x = WIDTH - 20 - self.radius
        if next_y - self.radius <= 20:
            wall_normal = (0, 1)
            next_y = 20 + self.radius
        elif next_y + self.radius >= HEIGHT - 20:
            wall_normal = (0, -1)
            next_y = HEIGHT - 20 - self.radius

        if wall_normal:
            v_len = math.hypot(self.dx, self.dy)
            if v_len == 0:
                v_len = 1e-6
            v = (self.dx / v_len, self.dy / v_len)
            wn = wall_normal
            dot = v[0] * wn[0] + v[1] * wn[1]
            angle = math.acos(max(-1, min(1, dot)))
            base_percent = abs(math.sin(angle))
            ricochet_percent = min(1.0, base_percent * self.ricochet_modifier)
            if random.random() < ricochet_percent:
                dot2 = v[0] * wn[0] + v[1] * wn[1]
                rx = v[0] - 2 * dot2 * wn[0]
                ry = v[1] - 2 * dot2 * wn[1]
                self.dx = rx * self.speed
                self.dy = ry * self.speed
                self.speed *= 1.2
                self.bounce_count += 1
                if self.ricochet_modifier > 1.0:
                    self.ricochet_modifier = 0.8
                else:
                    self.ricochet_modifier *= 0.8
            else:
                self.active = False
        self.x = next_x
        self.y = next_y

    def predict_ricochet(self):
        px, py = self.x, self.y
        vx, vy = self.dx, self.dy
        min_t = float('inf')
        hit_normal = None
        wall_hit_point = (px, py)
        walls = [
            (20 + self.radius, 1, 0),
            (WIDTH - 20 - self.radius, -1, 0),
            (20 + self.radius, 0, 1),
            (HEIGHT - 20 - self.radius, 0, -1),
        ]
        for wall in walls:
            if wall[1] != 0:
                if vx == 0:
                    continue
                t = (wall[0] - px) / vx
                if t > 0 and t < min_t:
                    min_t = t
                    wall_hit_point = (px + vx * t, py + vy * t)
                    hit_normal = (wall[1], wall[2])
            else:
                if vy == 0:
                    continue
                t = (wall[0] - py) / vy
                if t > 0 and t < min_t:
                    min_t = t
                    wall_hit_point = (px + vx * t, py + vy * t)
                    hit_normal = (wall[1], wall[2])
        ricochet_percent = 0.0
        if hit_normal:
            v_len = math.hypot(vx, vy)
            if v_len == 0:
                v_len = 1e-6
            v = (vx / v_len, vy / v_len)
            wn = hit_normal
            dot = v[0] * wn[0] + v[1] * wn[1]
            angle = math.acos(max(-1, min(1, dot)))
            base_percent = abs(math.sin(angle))
            ricochet_percent = min(1.0, base_percent * self.ricochet_modifier)
        return ricochet_percent, wall_hit_point

    def draw(self, surf):
        if self.active:
            pygame.draw.circle(surf, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)
            font = pygame.font.SysFont(None, 20)
            chance, pred_pt = self.predict_ricochet()
            txt = font.render(f"{int(chance * 100)}%", True, (255, 255, 255))
            surf.blit(txt, (self.x - 10, self.y - 25))
            pygame.draw.line(surf, (200, 200, 255), (self.x, self.y), pred_pt, 2)

# --- Menu and Navigation ---
def main_menu():
    maps = ["Empty", "Map 1", "Map 2", "Map 3", "Randomized"]
    
    def pick_map():
        pick_running = True
        selected = 0
        font = pygame.font.SysFont(None, 48)
        button_width = 200
        button_height = 50
        spacing = 20
        total_height = len(maps) * (button_height + spacing) - spacing
        start_y = HEIGHT // 2 - total_height // 2

        map_buttons = [
            Button(
                (WIDTH // 2 - button_width // 2, start_y + i * (button_height + spacing), button_width, button_height),
                maps[i],
                lambda i=i: selected.__setitem__(0, i) or setattr(pick_map, 'pick_running', False)
            )
            for i in range(len(maps))
        ]

        back_button = Button(
            (WIDTH // 2 - button_width // 2, start_y + total_height + spacing, button_width, button_height),
            "Back",
            lambda: setattr(pick_map, 'pick_running', False)
        )

        while pick_running:
            SCREEN.fill(BG_COLOR)
            title_font = pygame.font.SysFont(None, 56)
            t = title_font.render("Select Map", True, (255, 255, 255))
            SCREEN.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 6))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for btn in map_buttons + [back_button]:
                    btn.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(maps)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(maps)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        pick_running = False
                    elif event.key == pygame.K_ESCAPE:
                        return None

            for i, btn in enumerate(map_buttons):
                btn.hovered = (i == selected) or btn.hovered
                btn.draw(SCREEN)
            back_button.draw(SCREEN)
            pygame.display.flip()
            CLOCK.tick(FPS)
        return selected if pick_running else None

    running = True
    menu_result = [None]

    def start_game():
        map_id = pick_map()
        if map_id is not None:
            menu_result[0] = map_id
            nonlocal running
            running = False

    def map_creator():
        menu_result[0] = 'map_creator'
        nonlocal running
        running = False

    def options():
        menu_result[0] = 'options'
        nonlocal running
        running = False

    def quit_game():
        pygame.quit()
        sys.exit()

    button_width = 340
    button_height = 70
    spacing = 30
    total_height = 4 * (button_height + spacing) - spacing
    start_y = HEIGHT // 2 - total_height // 2

    buttons = [
        Button(
            (WIDTH // 2 - button_width // 2, start_y + i * (button_height + spacing), button_width, button_height),
            label, action
        )
        for i, (label, action) in enumerate([
            ("Start", start_game),
            ("Map Creator", map_creator),
            ("Options", options),
            ("Quit", quit_game),
        ])
    ]

    while running:
        SCREEN.fill(BG_COLOR)
        title_font = pygame.font.SysFont(None, 64)
        title_surf = title_font.render("Stug.io Tank Game", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        SCREEN.blit(title_surf, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            for btn in buttons:
                btn.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = buttons.index(next(btn for btn in buttons if btn.hovered)) if any(btn.hovered for btn in buttons) else 0
                    selected = (selected + 1) % len(buttons)
                    for i, btn in enumerate(buttons):
                        btn.hovered = (i == selected)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    selected = buttons.index(next(btn for btn in buttons if btn.hovered)) if any(btn.hovered for btn in buttons) else 0
                    selected = (selected - 1) % len(buttons)
                    for i, btn in enumerate(buttons):
                        btn.hovered = (i == selected)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    for btn in buttons:
                        if btn.hovered:
                            btn.onclick()
                            break

        for btn in buttons:
            btn.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(FPS)
    return menu_result[0]

# --- Map Management ---
def save_map(shapes, filename):
    data = [
        {
            'type': s.shape_type,
            'x': s.x,
            'y': s.y,
            'size': s.size,
            'angle': s.angle
        }
        for s in shapes
    ]
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_map(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        shapes = []
        for s in data:
            shape = MapShape(s['type'], s['x'], s['y'])
            shape.size = s['size']
            shape.angle = s['angle']
            shapes.append(shape)
        return shapes
    except Exception:
        return []

def random_map():
    random.seed()
    shapes = []
    for _ in range(random.randint(6, 14)):
        t = random.choice(['circle', 'square', 'triangle'])
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        size = random.randint(30, 120)
        angle = random.randint(0, 359)
        shape = MapShape(t, x, y)
        shape.size = size
        shape.angle = angle
        shapes.append(shape)
    return shapes

class MapShape:
    def __init__(self, shape_type, x, y):
        self.shape_type = shape_type
        self.x = x
        self.y = y
        self.size = 60
        self.angle = 0

    def point_inside(self, px, py):
        if self.shape_type == 'circle':
            return math.hypot(px - self.x, py - self.y) < self.size // 2
        else:
            return (self.x - self.size // 2 <= px <= self.x + self.size // 2 and
                    self.y - self.size // 2 <= py <= self.y + self.size // 2)

    def draw(self, surf, selected=False):
        color = (220, 220, 70) if selected else (180, 180, 180)
        if self.shape_type == 'circle':
            pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.size // 2, 0)
            pygame.draw.circle(surf, (80, 80, 80), (int(self.x), int(self.y)), self.size // 2, 2)
        elif self.shape_type == 'square':
            s = self.size
            rect = pygame.Rect(self.x - s // 2, self.y - s // 2, s, s)
            shape_surf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, color, (0, 0, s, s))
            pygame.draw.rect(shape_surf, (80, 80, 80), (0, 0, s, s), 2)
            shape_surf = pygame.transform.rotate(shape_surf, self.angle)
            surf.blit(shape_surf, shape_surf.get_rect(center=(self.x, self.y)))
        elif self.shape_type == 'triangle':
            s = self.size
            points = [(-s // 2, s // 2), (0, -s // 2), (s // 2, s // 2)]
            rot_points = []
            a = math.radians(self.angle)
            for px, py in points:
                rx = px * math.cos(a) - py * math.sin(a)
                ry = px * math.sin(a) + py * math.cos(a)
                rot_points.append((self.x + rx, self.y + ry))
            pygame.draw.polygon(surf, color, rot_points)
            pygame.draw.polygon(surf, (80, 80, 80), rot_points, 2)

def map_creator_screen():
    shapes = []
    shape_type = 'square'
    selected_idx = None
    dragging = False
    drag_offset = (0, 0)

    info_font = pygame.font.SysFont(None, 28)
    btn_font = pygame.font.SysFont(None, 26)

    class UI_Button:
        def __init__(self, x, y, w, h, text, callback, key=None):
            self.rect = pygame.Rect(x, y, w, h)
            self.text = text
            self.callback = callback
            self.key = key
            self.hovered = False
            self.clicked = False

        def draw(self, surf):
            color = (120, 170, 100) if self.hovered else (60, 80, 110)
            pygame.draw.rect(surf, color, self.rect, border_radius=7)
            txt = btn_font.render(self.text, True, (255, 255, 255))
            surf.blit(txt, txt.get_rect(center=self.rect.center))

        def handle(self, event):
            if event.type == pygame.MOUSEMOTION:
                self.hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.hovered and event.button == 1:
                    self.clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.hovered and event.button == 1 and self.clicked:
                    self.callback()
                self.clicked = False

    def cb_save1(): save_map(shapes, 'map1.json')
    def cb_save2(): save_map(shapes, 'map2.json')
    def cb_save3(): save_map(shapes, 'map3.json')
   

    def cb_load1(): 
        nonlocal shapes
        shapes.clear()
        shapes.extend(load_map('map1.json'))

    def cb_load2(): 
        nonlocal shapes
        shapes.clear()
        shapes.extend(load_map('map2.json'))

    def cb_load3(): 
        nonlocal shapes
        shapes.clear()
        shapes.extend(load_map('map3.json'))

    def cb_clear(): shapes.clear()

    def cb_random(): 
        nonlocal shapes
        shapes.clear()
        shapes.extend(random_map())

    def cb_delete():
        nonlocal selected_idx
        if selected_idx is not None:
            del shapes[selected_idx]
            selected_idx = None

    buttons = []
    btn_w = 88
    btn_h = 38
    x0 = 30
    y0 = 52
    gap = 6
    buttons.extend([
        UI_Button(x0, y0, btn_w, btn_h, 'Save 1 [S]', cb_save1, pygame.K_s),
        UI_Button(x0 + btn_w + gap, y0, btn_w, btn_h, 'Save 2 [F2]', cb_save2, pygame.K_F2),
        UI_Button(x0 + 2 * (btn_w + gap), y0, btn_w, btn_h, 'Save 3 [F3]', cb_save3, pygame.K_F3),
        UI_Button(x0, y0 + btn_h + gap, btn_w, btn_h, 'Load 1 [L]', cb_load1, pygame.K_l),
        UI_Button(x0 + btn_w + gap, y0 + btn_h + gap, btn_w, btn_h, 'Load 2 [F5]', cb_load2, pygame.K_F5),
        UI_Button(x0 + 2 * (btn_w + gap), y0 + btn_h + gap, btn_w, btn_h, 'Load 3 [F6]', cb_load3, pygame.K_F6),
        UI_Button(x0, y0 + 2 * (btn_h + gap), btn_w, btn_h, 'Random [R]', cb_random, pygame.K_r),
        UI_Button(x0 + btn_w + gap, y0 + 2 * (btn_h + gap), btn_w, btn_h, 'Clear [C]', cb_clear, pygame.K_c),
        UI_Button(x0 + 2 * (btn_w + gap), y0 + 2 * (btn_h + gap), btn_w, btn_h, 'Delete [DEL]', cb_delete, pygame.K_DELETE)
    ])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for btn in buttons:
                btn.handle(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    shape_type = 'circle'
                elif event.key == pygame.K_2:
                    shape_type = 'square'
                elif event.key == pygame.K_3:
                    shape_type = 'triangle'
                elif selected_idx is not None:
                    shape = shapes[selected_idx]
                    if event.key == pygame.K_q:
                        shape.angle = (shape.angle - 15) % 360
                    elif event.key == pygame.K_e:
                        shape.angle = (shape.angle + 15) % 360
                    elif event.key == pygame.K_z:
                        shape.size = max(20, shape.size - 10)
                    elif event.key == pygame.K_x:
                        shape.size = min(200, shape.size + 10)
                for btn in buttons:
                    if btn.key and event.key == btn.key:
                        btn.callback()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    for i, shape in enumerate(shapes):
                        if shape.point_inside(mx, my):
                            selected_idx = i
                            dragging = True
                            drag_offset = (shape.x - mx, shape.y - my)
                            break
                    else:
                        shapes.append(MapShape(shape_type, mx, my))
                        selected_idx = len(shapes) - 1
                        dragging = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging and selected_idx is not None:
                mx, my = event.pos
                shapes[selected_idx].x = mx + drag_offset[0]
                shapes[selected_idx].y = my + drag_offset[1]

        SCREEN.fill((60, 70, 80))
        for btn in buttons:
            btn.draw(SCREEN)
        for i, shape in enumerate(shapes):
            shape.draw(SCREEN, selected=(i == selected_idx))
        txt = info_font.render(
            '1:Circle 2:Square 3:Triangle  Q/E:Rotate  Z/X:Resize  ESC:Back',
            True, (255, 255, 255))
        SCREEN.blit(txt, (30, 10))
        pygame.display.flip()
        CLOCK.tick(FPS)

def options_screen():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        SCREEN.fill((70, 80, 120))
        font = pygame.font.SysFont(None, 40)
        txt = font.render("Options - Press ESC to return", True, (255, 255, 255))
        SCREEN.blit(txt, (60, HEIGHT // 2))
        pygame.display.flip()
        CLOCK.tick(FPS)

def circle_collide(cx, cy, r, ox, oy, osize):
    return math.hypot(cx - ox, cy - oy) < r + osize / 2

def square_collide(cx, cy, r, ox, oy, osize, oangle):
    s = osize / 2
    sin_a = math.sin(math.radians(-oangle))
    cos_a = math.cos(math.radians(-oangle))
    dx = cx - ox
    dy = cy - oy
    rx = dx * cos_a - dy * sin_a
    ry = dx * sin_a + dy * cos_a
    return abs(rx) < s + r and abs(ry) < s + r

def tri_collide(cx, cy, r, ox, oy, osize, oangle):
    s = osize
    points = [(-s // 2, s // 2), (0, -s // 2), (s // 2, s // 2)]
    a = math.radians(oangle)
    rot_points = []
    for px, py in points:
        rx = px * math.cos(a) - py * math.sin(a)
        ry = px * math.sin(a) + py * math.cos(a)
        rot_points.append((ox + rx, oy + ry))
    xs = [p[0] for p in rot_points]
    ys = [p[1] for p in rot_points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    return (minx - r < cx < maxx + r) and (miny - r < cy < maxy + r)

def tank_game(map_id=None):
    obstacles = []
    if map_id == 1:
        obstacles = load_map('map1.json')
    elif map_id == 2:
        obstacles = load_map('map2.json')
    elif map_id == 3:
        obstacles = load_map('map3.json')
    elif map_id == 4:
        obstacles = random_map()
    tank = Tank(20 + 50, HEIGHT // 2)
    bullets = []
    ricochet_effects = []
    shoot_cooldown = 0
    latest_bullet = None
    running = True
    while running:
        dt = CLOCK.tick(FPS) / 1000.0
        last_x, last_y = tank.x, tank.y
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and shoot_cooldown == 0:
                    cx, cy = tank.get_center()
                    spread = math.radians(random.uniform(-5, 5))
                    angle = tank.turret_angle + spread
                    bx = cx + math.cos(angle) * TURRET_LENGTH
                    by = cy + math.sin(angle) * TURRET_LENGTH
                    bullets.append(Bullet((bx, by), angle))
                    latest_bullet = bullets[-1]
                    shoot_cooldown = 8
        keys = pygame.key.get_pressed()
        tank.move(keys)
        tank.update_turret(pygame.mouse.get_pos())

        tx, ty = tank.get_center()
        for ob in obstacles:
            if ob.shape_type == 'circle':
                if circle_collide(tx, ty, max(tank.width, tank.height) // 2, ob.x, ob.y, ob.size):
                    tank.x, tank.y = last_x, last_y
            elif ob.shape_type == 'square':
                if square_collide(tx, ty, max(tank.width, tank.height) // 2, ob.x, ob.y, ob.size, ob.angle):
                    tank.x, tank.y = last_x, last_y
            elif ob.shape_type == 'triangle':
                if tri_collide(tx, ty, max(tank.width, tank.height) // 2, ob.x, ob.y, ob.size, ob.angle):
                    tank.x, tank.y = last_x, last_y

        for bullet in bullets:
            bx, by = bullet.x, bullet.y
            for ob in obstacles:
                hit = False
                if ob.shape_type == 'circle':
                    hit = circle_collide(bx, by, bullet.radius, ob.x, ob.y, ob.size)
                elif ob.shape_type == 'square':
                    hit = square_collide(bx, by, bullet.radius, ob.x, ob.y, ob.size, ob.angle)
                elif ob.shape_type == 'triangle':
                    hit = tri_collide(bx, by, bullet.radius, ob.x, ob.y, ob.size, ob.angle)
                if hit:
                    bullet.active = False
                    break

        bullets = [b for b in bullets if b.active]

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        SCREEN.fill(BG_COLOR)
        for wall in WALLS:
            pygame.draw.rect(SCREEN, WALL_COLOR, wall)
        for ob in obstacles:
            ob.draw(SCREEN)
        tank.draw(SCREEN)
        for bullet in bullets:
            bullet.draw(SCREEN)

        if latest_bullet and latest_bullet.active:
            font = pygame.font.SysFont(None, 28)
            chance, _ = latest_bullet.predict_ricochet()
            txt = font.render(f"Latest Bullet Ricochet Chance: {int(chance * 100)}%", True, (255, 255, 255))
            SCREEN.blit(txt, (50, 10))

        if bullets:
            fastest_speed = max(bullet.speed for bullet in bullets if bullet.active)
            font = pygame.font.SysFont(None, 28)
            speed_txt = font.render(f"Fastest Bullet Speed: {fastest_speed:.1f}", True, (255, 255, 255))
            text_rect = speed_txt.get_rect(topright=(WIDTH - 50, 10))
            SCREEN.blit(speed_txt, text_rect)

        pygame.display.flip()

def main():
    while True:
        result = main_menu()
        if isinstance(result, int):
            tank_game(result)
        elif result == "map_creator":
            map_creator_screen()
        elif result == "options":
            options_screen()
        else:
            break

if __name__ == "__main__":
    main()
