import pygame
import os
import sys
import random
import math
import graphics
import copy
import characters
from collections import deque
from PIL import Image, ImageDraw, ImageFont
import io
import re
# --- IMPORT CHECK ---
try:
    from search import Dijkstra
except ImportError:
    Dijkstra = None
    pass

# --- LANGUAGE SYSTEM ---
CURRENT_LANGUAGE = "English"  # Default language

TRANSLATIONS = {
    "English": {
        "login": "LOGIN",
        "register": "REGISTER",
        "username": "Username:",
        "password": "Password:",
        "enter_username": "Enter username...",
        "enter_password": "Enter password...",
        "switch_login": "Switch to LOGIN",
        "switch_register": "Switch to REGISTER",
        "skip": "SKIP >>",
        "processing": "Processing...",
        "login_register": "LOGIN / REGISTER",
        "mummy_maze": "MUMMY MAZE DELUXE",
        "select_map": "SELECT MAP",
        "random_map": "RANDOM MAP",
        "load_game": "LOAD GAME",
        "logout": "LOGOUT",
        "save_game": "SAVE GAME",
        "save_name": "Save name:",
        "enter_save_name": "Enter save name...",
        "save": "SAVE",
        "cancel": "CANCEL",
        "settings": "SETTINGS",
        "language": "Language",
        "english": "English",
        "vietnamese": "Vietnamese",
        "nav_save": "SAVE",
        "nav_undo": "UNDO",
        "nav_reset": "RESET",
        "nav_exit": "EXIT",
        "you_escaped": "YOU ESCAPED!",
        "again": "AGAIN",
        "home": "HOME",
        "next": "NEXT >>",
        "you_lose": "YOU LOSE",
        "try_again": "TRY AGAIN",
        "solution": "SOLUTION",
        "no_ai": "NO AI",
        "back": "BACK",
    },
    "Vietnamese": {
        "login": "ĐĂNG NHẬP",
        "register": "ĐĂNG KÝ",
        "username": "Tên người dùng:",
        "password": "Mật khẩu:",
        "enter_username": "Nhập tên người dùng...",
        "enter_password": "Nhập mật khẩu...",
        "switch_login": "Chuyển sang ĐĂNG NHẬP",
        "switch_register": "Chuyển sang ĐĂNG KÝ",
        "skip": "BỎ QUA >>",
        "processing": "Đang xử lý...",
        "login_register": "ĐĂNG NHẬP / ĐĂNG KÝ",
        "mummy_maze": "MUMMY MAZE DELUXE",
        "select_map": "CHỌN BẢN ĐỒ",
        "random_map": "BẢN ĐỒ NGẪU NHIÊN",
        "load_game": "TẢI TRÒ CHƠI",
        "logout": "ĐĂNG XUẤT",
        "save_game": "LƯU TRÒ CHƠI",
        "save_name": "Tên tiến trình :",
        "enter_save_name": "Nhập tên tiến trình cần lưu",
        "save": "LƯU",
        "cancel": "HỦY",
        "settings": "CÀI ĐẶT",
        "language": "Ngôn ngữ",
        "english": "Tiếng Anh",
        "vietnamese": "Tiếng Việt",
        "nav_save": "LƯU",
        "nav_undo": "HOÀN TÁC",
        "nav_reset": "ĐẶT LẠI",
        "nav_exit": "THOÁT",
        "you_escaped": "BẠN ĐÃ THOÁT!",
        "again": "CHƠI LẠI",
        "home": "TRANG CHỦ",
        "next": "TIẾP THEO >>",
        "you_lose": "BẠN ĐÃ THUA",
        "try_again": "THỬ LẠI",
        "solution": "HƯỚNG DẪN",
        "no_ai": "KHÔNG CÓ AI",
        "back": "QUAY LẠI",
    }
}

def t(key):
    """Translate a key to the current language"""
    return TRANSLATIONS.get(CURRENT_LANGUAGE, TRANSLATIONS["English"]).get(key, key)

# --- PATHS ---
project_path = os.getcwd()
map_path = os.path.join(project_path, "map")
maze_path = os.path.join(map_path, "maze")
object_path = os.path.join(map_path, "agents")

# --- CONFIG ---
GAME_W = 494
GAME_H = 480
COLOR_BG = (30, 30, 30)
COLOR_BTN = (60, 60, 60)
COLOR_BTN_HOVER = (100, 100, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_TITLE = (255, 215, 0)
COLOR_LOSE = (200, 50, 50)
COLOR_WIN = (50, 200, 50)
COLOR_OVERLAY = (0, 0, 0, 180)

# --- GLOBAL VARS ---
window = None
canvas = None
scale_ratio = 1.0
current_nav_bar = None  # Store navigation bar for drawing on every frame
current_mouse_pos = (0, 0)  # Store mouse position for nav bar drawing

# --- DISPLAY HOOK ---
_orig_flip = pygame.display.flip
def _smart_flip():
    global current_nav_bar, current_mouse_pos
    if window and canvas:
        # Draw navigation bar before flipping if it exists
        if current_nav_bar:
            current_nav_bar.draw(canvas, current_mouse_pos)
        
        win_w, win_h = window.get_size()
        scale_w = win_w / GAME_W
        scale_h = win_h / GAME_H
        scale_ratio = min(scale_w, scale_h)
        new_w = int(GAME_W * scale_ratio)
        new_h = int(GAME_H * scale_ratio)
        offset_x = (win_w - new_w) // 2
        offset_y = (win_h - new_h) // 2
        window.fill((0,0,0))
        scaled = pygame.transform.scale(canvas, (new_w, new_h))
        window.blit(scaled, (offset_x, offset_y))
        _orig_flip()
    else:
        _orig_flip()

pygame.display.flip = _smart_flip
pygame.display.update = _smart_flip

def init_display():
    global window, canvas
    pygame.init()
    info = pygame.display.Info()
    w, h = info.current_w - 50, info.current_h - 80
    window = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption("Mummy Maze")
    canvas = pygame.Surface((GAME_W, GAME_H))
    _smart_flip()

def get_mouse_pos():
    global current_mouse_pos
    mx, my = pygame.mouse.get_pos()
    win_w, win_h = window.get_size()
    s = min(win_w/GAME_W, win_h/GAME_H)
    ox = (win_w - GAME_W*s)//2
    oy = (win_h - GAME_H*s)//2
    current_mouse_pos = ((mx - ox) / s, (my - oy) / s)
    return current_mouse_pos

def set_nav_bar(nav_bar):
    """Set the navigation bar for display on every frame"""
    global current_nav_bar
    current_nav_bar = nav_bar

def clear_nav_bar():
    """Clear the navigation bar - called when exiting the game"""
    global current_nav_bar
    current_nav_bar = None

# --- GUI HELPERS ---
def draw_text(surface, text, size, x, y, color=COLOR_TEXT):
    """Draw text with Vietnamese support using PIL"""
    try:
        # Try to find a system font that supports Vietnamese
        font_names = ["arial", "segoe ui", "tahoma", "verdana", "times new roman"]
        pil_font = None
        
        for font_name in font_names:
            try:
                pil_font = ImageFont.truetype(f"C:\\Windows\\Fonts\\{font_name.replace(' ', '')}.ttf", size)
                break
            except:
                pass
        
        if pil_font is None:
            # Fallback: use PIL's default font
            pil_font = ImageFont.load_default()
        
        # Create a PIL image with enough space for the text
        # Use a larger temporary size to accurately measure text
        temp_img = Image.new('RGBA', (500, 100), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=pil_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding to ensure text isn't cut off
        padding = 8
        img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw the text with proper padding (accounting for bbox offset)
        draw.text((padding - bbox[0], padding - bbox[1]), text, font=pil_font, fill=color)
        
        # Convert PIL image to pygame surface
        pygame_img = pygame.image.fromstring(img.tobytes(), img.size, 'RGBA')
        
        # Get the rect and center it at the requested position
        rect = pygame_img.get_rect(center=(x, y))
        surface.blit(pygame_img, rect)
    except Exception as e:
        # Fallback to pygame rendering if PIL fails
        try: 
            font = pygame.font.SysFont("arial", size, bold=True)
        except: 
            font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        rect = label.get_rect(center=(x, y))
        surface.blit(label, rect)

def draw_eye_open(surface, x, y, size=15, color=(200, 200, 200)):
    """Draw an open eye icon"""
    # Outer eye shape (oval)
    pygame.draw.ellipse(surface, color, pygame.Rect(x - size, y - size//2, size*2, size))
    # Inner iris (circle)
    pygame.draw.circle(surface, (100, 150, 200), (x, y), size//3)
    # Pupil (small dark circle)
    pygame.draw.circle(surface, (20, 20, 20), (x + size//6, y), size//5)

def draw_eye_closed(surface, x, y, size=15, color=(200, 200, 200)):
    """Draw a closed eye icon (with slash)"""
    # Outer eye shape (oval)
    pygame.draw.ellipse(surface, color, pygame.Rect(x - size, y - size//2, size*2, size))
    # Diagonal slash through the eye
    pygame.draw.line(surface, color, (x - size - 2, y - size//2 - 2), (x + size + 2, y + size//2 + 2), 2)

def draw_button(surface, rect, text, hover=False, bg_color=None):
    c = bg_color if bg_color else (COLOR_BTN_HOVER if hover else COLOR_BTN)
    pygame.draw.rect(surface, c, rect)
    pygame.draw.rect(surface, (200, 200, 200), rect, 1)
    draw_text(surface, text, 16, rect.centerx, rect.centery)

def draw_gear_icon(surface, x, y, size=20, color=(200, 200, 200)):
    """Draw a simple gear icon"""
    # Outer circle (gear body)
    pygame.draw.circle(surface, color, (x, y), size, 3)
    
    # Teeth (small rectangles around the gear)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        tooth_x = x + (size + 8) * math.cos(rad)
        tooth_y = y + (size + 8) * math.sin(rad)
        pygame.draw.circle(surface, color, (int(tooth_x), int(tooth_y)), 4)
    
    # Center dot
    pygame.draw.circle(surface, color, (x, y), 3)

def settings_menu():
    """Menu to select language"""
    global CURRENT_LANGUAGE
    
    while True:
        canvas.fill(COLOR_BG)
        draw_text(canvas, t("settings"), 32, GAME_W//2, 80, COLOR_TITLE)
        
        mx, my = get_mouse_pos()
        
        # Language option
        draw_text(canvas, t("language") + ":", 24, GAME_W//2, 160, COLOR_TEXT)
        
        english_rect = pygame.Rect(GAME_W//2 - 120, 220, 100, 40)
        vietnamese_rect = pygame.Rect(GAME_W//2 + 20, 220, 100, 40)
        back_rect = pygame.Rect(GAME_W//2 - 60, 300, 120, 40)
        
        # Highlight selected language
        english_color = (100, 200, 100) if CURRENT_LANGUAGE == "English" else None
        vietnamese_color = (100, 200, 100) if CURRENT_LANGUAGE == "Vietnamese" else None
        
        draw_button(canvas, english_rect, t("english"), english_rect.collidepoint((mx, my)), english_color)
        draw_button(canvas, vietnamese_rect, t("vietnamese"), vietnamese_rect.collidepoint((mx, my)), vietnamese_color)
        draw_button(canvas, back_rect, t("back"), back_rect.collidepoint((mx, my)))
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN: click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
        
        if click:
            if english_rect.collidepoint((mx, my)):
                CURRENT_LANGUAGE = "English"
            elif vietnamese_rect.collidepoint((mx, my)):
                CURRENT_LANGUAGE = "Vietnamese"
            elif back_rect.collidepoint((mx, my)):
                return
        
        pygame.display.flip()

# ==================================================================================
# === NAVIGATION BAR ===
# ==================================================================================
class NavigationBar:
    """In-game navigation bar for player controls"""
    def __init__(self, game_width=GAME_W):
        self.bar_height = 40
        self.bar_y = 0
        self.button_width = 90
        self.button_height = 35
        self.button_spacing = 5
        self.game_width = game_width
        
        # Calculate button positions (centered at top)
        total_width = (self.button_width * 4) + (self.button_spacing * 3)
        start_x = (game_width - total_width) // 2
        
        self.save_btn = pygame.Rect(start_x, 2, self.button_width, self.button_height)
        self.undo_btn = pygame.Rect(start_x + self.button_width + self.button_spacing, 2, self.button_width, self.button_height)
        self.reset_btn = pygame.Rect(start_x + (self.button_width * 2) + (self.button_spacing * 2), 2, self.button_width, self.button_height)
        self.exit_btn = pygame.Rect(start_x + (self.button_width * 3) + (self.button_spacing * 3), 2, self.button_width, self.button_height)
    
    def draw(self, surface, mouse_pos):
        """Draw the navigation bar with buttons"""
        # Draw bar background
        pygame.draw.rect(surface, (40, 40, 40), pygame.Rect(0, 0, self.game_width, self.bar_height))
        pygame.draw.line(surface, (100, 100, 100), (0, self.bar_height), (self.game_width, self.bar_height), 2)
        
        # Draw buttons
        save_hover = self.save_btn.collidepoint(mouse_pos)
        undo_hover = self.undo_btn.collidepoint(mouse_pos)
        reset_hover = self.reset_btn.collidepoint(mouse_pos)
        exit_hover = self.exit_btn.collidepoint(mouse_pos)
        
        draw_button(surface, self.save_btn, t("nav_save"), save_hover, (50, 100, 50) if save_hover else (40, 80, 40))
        draw_button(surface, self.undo_btn, t("nav_undo"), undo_hover, (100, 100, 100) if undo_hover else (80, 80, 80))
        draw_button(surface, self.reset_btn, t("nav_reset"), reset_hover, (100, 80, 50) if reset_hover else (80, 60, 40))
        draw_button(surface, self.exit_btn, t("nav_exit"), exit_hover, (100, 50, 50) if exit_hover else (80, 40, 40))
    
    def get_clicked_button(self, mouse_pos):
        """Return which button was clicked, or None"""
        if self.save_btn.collidepoint(mouse_pos):
            return "save"
        elif self.undo_btn.collidepoint(mouse_pos):
            return "undo"
        elif self.reset_btn.collidepoint(mouse_pos):
            return "reset"
        elif self.exit_btn.collidepoint(mouse_pos):
            return "exit"
        return None
    
    def is_in_nav_bar(self, mouse_pos):
        """Check if mouse is in navigation bar area"""
        return mouse_pos[1] < self.bar_height

# ==================================================================================
# === MAZE GENERATION (DSU + WALL REDUCTION + AI VALIDATION) ===
# ==================================================================================

class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    def find(self, i):
        if self.parent[i] != i: self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    def union(self, i, j):
        root_i = self.find(i); root_j = self.find(j)
        if root_i == root_j: return False
        if self.rank[root_i] > self.rank[root_j]: self.parent[root_j] = root_i
        elif self.rank[root_j] > self.rank[root_i]: self.parent[root_i] = root_j
        else: self.parent[root_i] = root_j; self.rank[root_j] += 1
        return True

def generate_random_maze_algo(cols, rows):
    walls_h = [[1 for _ in range(cols)] for _ in range(rows + 1)]
    walls_v = [[1 for _ in range(cols + 1)] for _ in range(rows)]
    edges = []
    for r in range(rows - 1):
        for c in range(cols): edges.append(('H', r, c, r * cols + c, (r + 1) * cols + c))
    for r in range(rows):
        for c in range(cols - 1): edges.append(('V', r, c, r * cols + c, r * cols + (c + 1)))
    random.shuffle(edges)
    ds = DSU(cols * rows)
    for wall_type, r, c, cell_1, cell_2 in edges:
        if ds.union(cell_1, cell_2):
            if wall_type == 'H': walls_h[r + 1][c] = 0
            else: walls_v[r][c + 1] = 0
    return walls_h, walls_v

def reduce_wall_density(walls_h, walls_v, cols, rows, target_percent=0.50):
    grid_h = 2 * rows + 1; grid_w = 2 * cols + 1; total_cells = grid_h * grid_w
    removable_walls = []
    for r in range(1, rows):
        for c in range(cols):
            if walls_h[r][c] == 1: removable_walls.append(('H', r, c))
    for r in range(rows):
        for c in range(1, cols):
            if walls_v[r][c] == 1: removable_walls.append(('V', r, c))
    random.shuffle(removable_walls)
    
    count_walls = 0
    for r in range(rows+1): count_walls += sum(walls_h[r])
    for r in range(rows): count_walls += sum(walls_v[r])
    count_walls += (rows+1)*(cols+1) 

    while removable_walls and (count_walls / total_cells > target_percent):
        w_type, r, c = removable_walls.pop()
        if w_type == 'H': walls_h[r][c] = 0
        else: walls_v[r][c] = 0
        count_walls -= 1
    return walls_h, walls_v

def check_path_algo(rows, cols, walls_h, walls_v, start, end, avoid_traps=None, blocked_gate=None):
    if avoid_traps is None: avoid_traps = set()
    queue = deque([(start, [start])])
    visited = set([start])
    while queue:
        (cx, cy), path = queue.popleft()
        if (cx, cy) == end: return path
        moves = [(0, -1, 'Up'), (0, 1, 'Down'), (-1, 0, 'Left'), (1, 0, 'Right')]
        for dx, dy, direction in moves:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in avoid_traps:
                blocked = False
                if direction == 'Up':
                    if walls_h[cy][cx] == 1: blocked = True
                    if blocked_gate and blocked_gate == ('H', cy, cx): blocked = True
                elif direction == 'Down':
                    if walls_h[cy + 1][cx] == 1: blocked = True
                    if blocked_gate and blocked_gate == ('H', cy + 1, cx): blocked = True
                elif direction == 'Left':
                    if walls_v[cy][cx] == 1: blocked = True
                    if blocked_gate and blocked_gate == ('V', cy, cx): blocked = True
                elif direction == 'Right':
                    if walls_v[cy][cx + 1] == 1: blocked = True
                    if blocked_gate and blocked_gate == ('V', cy, cx + 1): blocked = True
                if not blocked and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return None

def generate_solvable_data(cols, rows):
    while True:
        wh, wv = generate_random_maze_algo(cols, rows)
        wh, wv = reduce_wall_density(wh, wv, cols, rows, target_percent=0.50)
        
        py, px = random.randint(0, rows - 1), random.randint(0, cols - 1)
        border_cells = []
        for x in range(cols): border_cells.append((x, 0)); border_cells.append((x, rows - 1))
        for y in range(1, rows - 1): border_cells.append((0, y)); border_cells.append((cols - 1, y))
        ex, ey = random.choice(border_cells)
        if (px, py) == (ex, ey): continue

        if ey == 0: wh[0][ex] = 0
        elif ey == rows - 1: wh[rows][ex] = 0
        elif ex == 0: wv[ey][0] = 0
        elif ex == cols - 1: wv[ey][cols] = 0

        path_p_e = check_path_algo(rows, cols, wh, wv, (px, py), (ex, ey))
        if not path_p_e or len(path_p_e) < 4: continue

        cut_idx = random.randint(1, len(path_p_e) - 2)
        u, v = path_p_e[cut_idx], path_p_e[cut_idx + 1]
        gate_info = ('H', max(u[1], v[1]), u[0]) if u[0] == v[0] else ('V', u[1], max(u[0], v[0]))

        key_pos = None
        for _ in range(30):
            kx, ky = random.randint(0, cols - 1), random.randint(0, rows - 1)
            if (kx, ky) not in [(px, py), (ex, ey)] and (kx, ky) != v:
                if check_path_algo(rows, cols, wh, wv, (px, py), (kx, ky), blocked_gate=gate_info):
                    key_pos = (kx, ky); break
        if not key_pos: continue

        traps = []
        attempts = 0
        while len(traps) < 2 and attempts < 200:
            tx, ty = random.randint(0, cols - 1), random.randint(0, rows - 1)
            if (tx, ty) not in [(px, py), (ex, ey), key_pos] and (tx, ty) not in traps:
                traps.append((tx, ty))
                temp_traps = set(traps)
                path1 = check_path_algo(rows, cols, wh, wv, (px, py), key_pos, avoid_traps=temp_traps, blocked_gate=gate_info)
                path2 = check_path_algo(rows, cols, wh, wv, key_pos, (ex, ey), avoid_traps=temp_traps, blocked_gate=None)
                if not path1 or not path2: traps.pop()
            attempts += 1
        
        return {'wh': wh, 'wv': wv, 'p': (px, py), 'e': (ex, ey), 'k': key_pos, 'g': gate_info, 't': traps}

class MazeGenerator:
    def __init__(self, size):
        self.rows = size; self.cols = size
        self.hero_pos = None; self.key_pos = None; self.gate_pos = None; self.gate_obj = None
        self.enemies = []; self.traps = []; self.grid = []

    def generate(self):
        print("Generating Map (DSU Kruskal + Wall Reduction + AI Validated)...")
        attempts = 0
        while True:
            attempts += 1
            if attempts % 10 == 0: print(f"Searching for winnable map... Attempt {attempts}")
            
            # 1. Generate Structural Map (guaranteed connectivity)
            data = generate_solvable_data(self.cols, self.rows)
            
            # 2. Convert to Game Grid
            self.grid = self._convert_to_grid(data)
            
            # 3. Try to place Mummy and Validate with AI
            # Try a few different mummy positions for this map layout
            found_solution = False
            for _ in range(5):
                if self._spawn_mummy(data):
                    # Check if winnable
                    if self._check_solvable():
                        found_solution = True
                        break
            
            if found_solution:
                print(f">>> SUCCESS: Found Solvable Map in {attempts} attempts!")
                return self._export_data()
            
            # If map structure + mummy position makes it impossible, loop continues to generate new map
            if attempts > 1000:
                print(">>> TIMEOUT: Returning best effort (may be hard/impossible).")
                return self._export_data()

    def _convert_to_grid(self, data):
        wh, wv = data['wh'], data['wv']
        grid_h = 2 * self.rows + 1; grid_w = 2 * self.cols + 1
        grid = [[' ' for _ in range(grid_w)] for _ in range(grid_h)]
        for r in range(0, grid_h, 2):
            for c in range(0, grid_w, 2): grid[r][c] = '%'
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if wh[r][c] == 1: grid[2*r][2*c+1] = '%'
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if wv[r][c] == 1: grid[2*r+1][2*c] = '%'
        
        kx, ky = data['k']; grid[2*ky+1][2*kx+1] = 'K'
        self.traps = []
        for tx, ty in data['t']:
            grid[2*ty+1][2*tx+1] = 'T'
            self.traps.append((2*ty+1, 2*tx+1))
            
        gt, gr, gc = data['g']
        if gt == 'H': grid[2*gr][2*gc+1] = 'G'
        else: grid[2*gr+1][2*gc] = 'G'
        
        ex, ey = data['e']
        if ey == 0: grid[0][2*ex+1] = 'S'
        elif ey == self.rows - 1: grid[2*self.rows][2*ex+1] = 'S'
        elif ex == 0: grid[2*ey+1][0] = 'S'
        elif ex == self.cols - 1: grid[2*ey+1][2*self.cols] = 'S'
        
        self.hero_pos = data['p']
        self.key_pos = data['k']
        self.gate_obj = {"gate_position": (gr if gt=='H' else gr, gc), "isClosed": True}
        if gt == 'H': self.gate_obj['gate_position'] = (2*gr, 2*gc+1)
        else: self.gate_obj['gate_position'] = (2*gr+1, 2*gc)
        
        return grid

    def _spawn_mummy(self, data):
        self.enemies = []
        px, py = data['p']
        best_d = 0; mx, my = -1, -1
        empties = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (c, r) not in [data['p'], data['k'], data['e']] and (c, r) not in data['t']:
                    empties.append((c, r))
        random.shuffle(empties)
        for c, r in empties:
            dist = abs(c - px) + abs(r - py)
            if dist > 4: mx, my = c, r; break
        if mx != -1:
            self.enemies.append(("MW", mx, my))
            return True
        return False

    def _check_solvable(self):
        if not Dijkstra: return True
        exp = characters.Explorer(2*self.hero_pos[1]+1, 2*self.hero_pos[0]+1)
        mws = []
        for e in self.enemies:
            mws.append(characters.mummy_white(2*e[2]+1, 2*e[1]+1))
        gate = {"gate_position": self.gate_obj['gate_position'], "isClosed": True}
        key_grid_pos = (2*self.key_pos[1]+1, 2*self.key_pos[0]+1)
        try:
            path = Dijkstra(exp, mws, [], [], [], gate, self.traps, key_grid_pos, self.grid)
            return path is not None
        except Exception as e: return False

    def _export_data(self):
        map_data = ["".join(row) for row in self.grid]
        px, py = self.hero_pos
        agent_str = f"E {2*py+1} {2*px+1}\n"
        for e in self.enemies:
            agent_str += f"{e[0]} {2*e[2]+1} {2*e[1]+1}\n"
        return map_data, agent_str

# ==================================================================================

def login_menu():
    """Menu for login/register"""
    try:
        from game_utils import AuthManager
        auth = AuthManager()
    except ImportError:
        return None
    
    username = ""
    password = ""
    is_registering = False
    message = ""
    active_field = None  # None, "username" or "password" - only set when clicked
    show_password = [False]  # Use list to make it mutable and persistent across frames
    clock = pygame.time.Clock()
    cursor_visible = True
    cursor_timer = 0
    cursor_blink_interval = 500  # milliseconds
    
    while True:
        # Update cursor blinking
        cursor_timer += clock.tick(60)  # 60 FPS
        if cursor_timer >= cursor_blink_interval:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        canvas.fill(COLOR_BG)
        draw_text(canvas, t("mummy_maze"), 32, GAME_W//2, 60, COLOR_TITLE)
        draw_text(canvas, t("login_register"), 24, GAME_W//2, 100, COLOR_TEXT)
        
        mx, my = get_mouse_pos()
        
        # Draw settings button (top right)
        gear_rect = pygame.Rect(GAME_W - 80, 10, 70, 35)
        gear_hover = gear_rect.collidepoint((mx, my))
        pygame.draw.rect(canvas, (100, 100, 100) if gear_hover else (60, 60, 60), gear_rect)
        pygame.draw.rect(canvas, (200, 200, 200), gear_rect, 1)
        draw_text(canvas, t("settings"), 14, gear_rect.centerx, gear_rect.centery, (200, 200, 200))
        
        # Username field
        draw_text(canvas, t("username"), 18, GAME_W//2 - 120, 150)
        username_rect = pygame.Rect(GAME_W//2 - 100, 170, 200, 35)
        username_color = (120, 120, 120) if active_field == "username" else COLOR_BTN
        pygame.draw.rect(canvas, username_color, username_rect)
        pygame.draw.rect(canvas, COLOR_TEXT, username_rect, 2)
        
        # Draw username with cursor if active and field has been clicked
        username_display = username
        if active_field == "username":
            # Field is active, show cursor blinking
            if username:
                # If there's text, append cursor
                if cursor_visible:
                    username_display = username + "|"
                else:
                    username_display = username + " "
            else:
                # If empty, show only cursor
                if cursor_visible:
                    username_display = "|"
                else:
                    username_display = " "
        else:
            # Field is not active, show placeholder if empty
            username_display = username if username else t("enter_username")
        
        draw_text(canvas, username_display, 18, username_rect.centerx, username_rect.centery, 
                 (200, 200, 200) if username or active_field == "username" else (100, 100, 100))
        
        # Password field with eye icon
        draw_text(canvas, t("password"), 18, GAME_W//2 - 120, 220)
        password_rect = pygame.Rect(GAME_W//2 - 100, 240, 200, 35)
        password_color = (120, 120, 120) if active_field == "password" else COLOR_BTN
        pygame.draw.rect(canvas, password_color, password_rect)
        pygame.draw.rect(canvas, COLOR_TEXT, password_rect, 2)
        
        # Draw eye icon button (inside the password field, on the right side)
        eye_icon_rect = pygame.Rect(GAME_W//2 + 75, 247, 25, 20)
        eye_icon_hover = eye_icon_rect.collidepoint((mx, my))
        
        # Draw eye icon background button
        eye_bg_color = (100, 100, 100) if eye_icon_hover else (80, 80, 80)
        pygame.draw.rect(canvas, eye_bg_color, eye_icon_rect)
        pygame.draw.rect(canvas, (150, 150, 150), eye_icon_rect, 1)
        
        # Draw eye icon using shapes
        if show_password[0]:
            # Open eye - show password
            draw_eye_open(canvas, eye_icon_rect.centerx, eye_icon_rect.centery, size=7)
        else:
            # Closed eye - hide password
            draw_eye_closed(canvas, eye_icon_rect.centerx, eye_icon_rect.centery, size=7)
        
        # Draw password with cursor if active and field has been clicked
        password_display_value = password if show_password[0] else "*" * len(password)
        if active_field == "password":
            # Field is active, show cursor blinking
            if password:
                # If there's text, append cursor
                if cursor_visible:
                    password_display = password_display_value + "|"
                else:
                    password_display = password_display_value + " "
            else:
                # If empty, show only cursor
                if cursor_visible:
                    password_display = "|"
                else:
                    password_display = " "
        else:
            # Field is not active, show placeholder if empty
            password_display = password_display_value if password else t("enter_password")
        
        # Draw password text (adjusted to account for eye icon)
        password_text_rect = pygame.Rect(GAME_W//2 - 100, 240, 160, 35)
        draw_text(canvas, password_display, 18, password_text_rect.centerx, password_text_rect.centery,
                 (200, 200, 200) if password or active_field == "password" else (100, 100, 100))
        
        # Buttons
        action_rect = pygame.Rect(GAME_W//2 - 100, 300, 200, 40)
        toggle_rect = pygame.Rect(GAME_W//2 - 100, 350, 200, 30)
        skip_rect = pygame.Rect(GAME_W//2 - 60, 390, 120, 30)
        
        action_text = t("register") if is_registering else t("login")
        draw_button(canvas, action_rect, action_text, action_rect.collidepoint((mx, my)))
        toggle_text = t("switch_login") if is_registering else t("switch_register")
        draw_button(canvas, toggle_rect, toggle_text, toggle_rect.collidepoint((mx, my)), (80, 80, 80))
        draw_button(canvas, skip_rect, t("skip"), skip_rect.collidepoint((mx, my)), (60, 60, 60))
        
        # Message display
        if message:
            msg_color = COLOR_WIN if "success" in message.lower() or "chào mừng" in message.lower() else COLOR_LOSE
            draw_text(canvas, message[:40], 16, GAME_W//2, 430, msg_color)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_field = "password" if active_field == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                elif event.key == pygame.K_RETURN:
                    if username and password:
                        # Draw processing message
                        canvas.fill(COLOR_BG)
                        draw_text(canvas, "MUMMY MAZE DELUXE", 32, GAME_W//2, 60, COLOR_TITLE)
                        draw_text(canvas, "LOGIN / REGISTER", 24, GAME_W//2, 100, COLOR_TEXT)
                        draw_text(canvas, t("processing"), 20, GAME_W//2, GAME_H//2, COLOR_WIN)
                        pygame.display.flip()
                        pygame.time.delay(300)  # Show processing message for 0.5 seconds
                        
                        if is_registering:
                            success, msg = auth.register(username, password)
                        else:
                            success, msg = auth.login(username, password)
                        message = msg
                        if success:
                            return auth
                else:
                    if active_field == "username":
                        username += event.unicode
                    else:
                        password += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN: 
                click = True
                # Handle gear icon click (settings)
                if gear_rect.collidepoint((mx, my)):
                    settings_menu()
                    click = False
                # Switch active field on click
                elif eye_icon_rect.collidepoint((mx, my)):
                    # Toggle password visibility - don't set active field
                    show_password[0] = not show_password[0]
                    click = False  # Don't trigger other button actions
                elif username_rect.collidepoint((mx, my)):
                    active_field = "username"
                elif password_rect.collidepoint((mx, my)):
                    active_field = "password"
        
        if click:
            if action_rect.collidepoint((mx, my)) and username and password:
                # Draw processing message
                canvas.fill(COLOR_BG)
                draw_text(canvas, t("mummy_maze"), 32, GAME_W//2, 60, COLOR_TITLE)
                draw_text(canvas, t("login_register"), 24, GAME_W//2, 100, COLOR_TEXT)
                draw_text(canvas, t("processing"), 20, GAME_W//2, GAME_H//2, COLOR_WIN)
                pygame.display.flip()
                pygame.time.delay(300)  # Show processing message for 0.5 seconds
                
                if is_registering:
                    success, msg = auth.register(username, password)
                else:
                    success, msg = auth.login(username, password)
                message = msg
                if success:
                    return auth
            elif toggle_rect.collidepoint((mx, my)):
                is_registering = not is_registering
                message = ""
            elif skip_rect.collidepoint((mx, my)):
                return None  # Skip login
        
        pygame.display.flip()

def main_menu(auth_manager=None):
    while True:
        canvas.fill(COLOR_BG)
        draw_text(canvas, t("mummy_maze"), 40, GAME_W//2, 100, COLOR_TITLE)
        
        # Display current user if logged in
        if auth_manager and auth_manager.is_logged_in():
            draw_text(canvas, f"User: {auth_manager.get_current_user()}", 16, GAME_W//2, 170, COLOR_WIN)
        
        mx, my = get_mouse_pos()
        
        # Draw settings button (top right)
        gear_rect = pygame.Rect(GAME_W - 80, 10, 70, 35)
        gear_hover = gear_rect.collidepoint((mx, my))
        pygame.draw.rect(canvas, (100, 100, 100) if gear_hover else (60, 60, 60), gear_rect)
        pygame.draw.rect(canvas, (200, 200, 200), gear_rect, 1)
        draw_text(canvas, t("settings"), 14, gear_rect.centerx, gear_rect.centery, (200, 200, 200))
        
        btn_adv = pygame.Rect(GAME_W//2-100, 200, 200, 45) # Đổi tên biến cho dễ nhớ
        btn_rnd = pygame.Rect(GAME_W//2-100, 260, 200, 45)
        btn_load = pygame.Rect(GAME_W//2-100, 320, 200, 45)
        btn_logout = pygame.Rect(GAME_W//2-100, 380, 200, 35)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: click = True
            if event.type == pygame.VIDEORESIZE: pygame.display.flip()

        # --- VẼ NÚT ADVENTURE ---
        draw_button(canvas, btn_adv, "ADVENTURE", btn_adv.collidepoint((mx,my)))
        
        draw_button(canvas, btn_rnd, t("random_map"), btn_rnd.collidepoint((mx,my)))
        draw_button(canvas, btn_load, t("load_game"), btn_load.collidepoint((mx,my)), 
                   (50, 50, 50) if not (auth_manager and auth_manager.is_logged_in()) else None)
        if auth_manager and auth_manager.is_logged_in():
            draw_button(canvas, btn_logout, t("logout"), btn_logout.collidepoint((mx,my)), (100, 50, 50))
        
        pygame.display.flip()
        
        if click:
            if gear_rect.collidepoint((mx, my)):
                settings_menu()
            
            # --- SỬA LOGIC CLICK ---
            elif btn_adv.collidepoint((mx,my)): return "adventure", auth_manager # Trả về "adventure"
            
            elif btn_rnd.collidepoint((mx,my)): return "random", auth_manager
            elif btn_load.collidepoint((mx,my)) and auth_manager and auth_manager.is_logged_in():
                return "load", auth_manager
            elif btn_logout.collidepoint((mx,my)) and auth_manager and auth_manager.is_logged_in():
                auth_manager.logout()
                return "login", None

def save_game_menu(auth_manager, game, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars, current_map):
    """Menu to save current game"""
    global current_nav_bar
    
    try:
        from game_utils import SaveManager
        save_manager = SaveManager(auth_manager)
    except ImportError as e:
        print(f"ImportError in save_game_menu: {e}")
        return False
    except Exception as e:
        print(f"Error in save_game_menu init: {e}")
        return False
    
    if not auth_manager or not auth_manager.is_logged_in():
        print("Auth manager not logged in")
        return False
    
    # Temporarily save and clear nav bar so it doesn't interfere with save menu
    saved_nav_bar = current_nav_bar
    clear_nav_bar()
    
    save_name = ""
    message = ""
    active_field = True  # Save name field is always active
    clock = pygame.time.Clock()
    cursor_visible = True
    cursor_timer = 0
    cursor_blink_interval = 500  # milliseconds
    
    while True:
        # Update cursor blinking
        cursor_timer += clock.tick(60)  # 60 FPS
        if cursor_timer >= cursor_blink_interval:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        canvas.fill(COLOR_BG)
        draw_text(canvas, t("save_game"), 32, GAME_W//2, 80, COLOR_TITLE)
        
        mx, my = get_mouse_pos()
        
        draw_text(canvas, t("save_name"), 20, GAME_W//2 - 100, 150)
        name_rect = pygame.Rect(GAME_W//2 - 100, 175, 200, 35)
        pygame.draw.rect(canvas, COLOR_BTN, name_rect)
        pygame.draw.rect(canvas, COLOR_TEXT, name_rect, 2)
        
        # Display name with blinking cursor
        save_name_display = save_name
        if active_field:
            if save_name:
                # If there's text, append cursor
                if cursor_visible:
                    save_name_display = save_name + "|"
                else:
                    save_name_display = save_name + " "
            else:
                # If empty, show only cursor
                if cursor_visible:
                    save_name_display = "|"
                else:
                    save_name_display = " "
        else:
            # Field is not active, show placeholder if empty
            save_name_display = save_name if save_name else t("enter_save_name")
        
        draw_text(canvas, save_name_display, 18, name_rect.centerx, name_rect.centery,
                 (200, 200, 200) if save_name or active_field else (100, 100, 100))
        
        save_rect = pygame.Rect(GAME_W//2 - 100, 240, 120, 40)
        cancel_rect = pygame.Rect(GAME_W//2 + 20, 240, 80, 40)
        
        draw_button(canvas, save_rect, t("save"), save_rect.collidepoint((mx, my)))
        draw_button(canvas, cancel_rect, t("cancel"), cancel_rect.collidepoint((mx, my)))
        
        if message:
            msg_color = COLOR_WIN if "success" in message.lower() else COLOR_LOSE
            draw_text(canvas, message[:50], 16, GAME_W//2, 300, msg_color)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: set_nav_bar(saved_nav_bar); return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    save_name = save_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if save_name:
                        success, msg = save_manager.save_game(save_name, game, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars, current_map)
                        message = msg
                        if success:
                            pygame.time.wait(500)
                            return True
                elif event.key == pygame.K_ESCAPE:
                    set_nav_bar(saved_nav_bar)  # Restore nav bar before returning
                    return False
                else:
                    save_name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN: 
                click = True
                if name_rect.collidepoint((mx, my)):
                    active_field = True
                else:
                    active_field = False
        
        if click:
            if save_rect.collidepoint((mx, my)) and save_name:
                success, msg = save_manager.save_game(save_name, game, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars, current_map)
                message = msg
                if success:
                    pygame.time.wait(500)
                    set_nav_bar(saved_nav_bar)  # Restore nav bar before returning
                    return True
            elif cancel_rect.collidepoint((mx, my)):
                set_nav_bar(saved_nav_bar)  # Restore nav bar before returning
                return False
        
        pygame.display.flip()

def load_game_menu(auth_manager):
    """Menu to select and load a saved game"""
    try:
        from game_utils import SaveManager
        save_manager = SaveManager(auth_manager)
    except ImportError:
        return None
    
    if not auth_manager or not auth_manager.is_logged_in():
        return None
    
    saves = save_manager.list_saves()
    page = 0
    saves_per_page = 6
    
    while True:
        canvas.fill(COLOR_BG)
        draw_text(canvas, "LOAD GAME", 32, GAME_W//2, 50, COLOR_TITLE)
        
        mx, my = get_mouse_pos()
        
        if not saves:
            draw_text(canvas, "No saved games found", 20, GAME_W//2, 250, COLOR_TEXT)
            back_rect = pygame.Rect(GAME_W//2 - 60, 350, 120, 40)
            draw_button(canvas, back_rect, "BACK", back_rect.collidepoint((mx, my)))
        else:
            start_idx = page * saves_per_page
            end_idx = min(start_idx + saves_per_page, len(saves))
            
            for i in range(start_idx, end_idx):
                idx = i - start_idx
                save_rect = pygame.Rect(100, 100 + idx * 50, 294, 40)
                draw_button(canvas, save_rect, saves[i], save_rect.collidepoint((mx, my)))
            
            if len(saves) > saves_per_page:
                if page > 0:
                    prev_rect = pygame.Rect(50, 400, 80, 35)
                    draw_button(canvas, prev_rect, "<<", prev_rect.collidepoint((mx, my)))
                
                if end_idx < len(saves):
                    next_rect = pygame.Rect(GAME_W - 130, 400, 80, 35)
                    draw_button(canvas, next_rect, ">>", next_rect.collidepoint((mx, my)))
            
            back_rect = pygame.Rect(GAME_W//2 - 60, 440, 120, 35)
            draw_button(canvas, back_rect, "BACK", back_rect.collidepoint((mx, my)))
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.MOUSEBUTTONDOWN: click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
        
        if click:
            if not saves:
                if back_rect.collidepoint((mx, my)):
                    return None
            else:
                for i in range(start_idx, end_idx):
                    idx = i - start_idx
                    save_rect = pygame.Rect(100, 100 + idx * 50, 294, 40)
                    if save_rect.collidepoint((mx, my)):
                        return saves[i]
                
                if len(saves) > saves_per_page:
                    if page > 0:
                        prev_rect = pygame.Rect(50, 400, 80, 35)
                        if prev_rect.collidepoint((mx, my)):
                            page -= 1
                    
                    if end_idx < len(saves):
                        next_rect = pygame.Rect(GAME_W - 130, 400, 80, 35)
                        if next_rect.collidepoint((mx, my)):
                            page += 1
                
                if back_rect.collidepoint((mx, my)):
                    return None
        
        pygame.display.flip()

def select_map_screen(files):
    cols, rows = 3, 8
    w, h = 140, 40
    gap = 10
    start_x = (GAME_W - (cols*w + (cols-1)*gap))//2
    page = 0
    total = math.ceil(len(files)/(cols*rows))
    while True:
        canvas.fill(COLOR_BG)
        draw_text(canvas, "SELECT MAP", 30, GAME_W//2, 40, COLOR_TITLE)
        mx, my = get_mouse_pos()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: click = True
            if event.type == pygame.VIDEORESIZE: pygame.display.flip()
            
        s, e = page*cols*rows, min((page+1)*cols*rows, len(files))
        for i in range(s, e):
            idx = i - s
            r, c = idx//cols, idx%cols
            rect = pygame.Rect(start_x + c*(w+gap), 80 + r*(h+gap), w, h)
            draw_button(canvas, rect, files[i].replace(".txt",""), rect.collidepoint((mx,my)))
            if click and rect.collidepoint((mx,my)): return files[i]
        
        if total > 1:
            draw_text(canvas, f"{page+1}/{total}", 20, GAME_W//2, GAME_H-30)
            if page > 0:
                pr = pygame.Rect(20, GAME_H-45, 80, 35)
                draw_button(canvas, pr, "<<", pr.collidepoint((mx,my)))
                if click and pr.collidepoint((mx,my)): page -= 1
            if page < total-1:
                nr = pygame.Rect(GAME_W-100, GAME_H-45, 80, 35)
                draw_button(canvas, nr, ">>", nr.collidepoint((mx,my)))
                if click and nr.collidepoint((mx,my)): page += 1
        pygame.display.flip()

def game_over_popup():
    s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    s.fill(COLOR_OVERLAY)
    canvas.blit(s, (0,0))
    pygame.draw.rect(canvas, (50,50,50), (70,140,354,200))
    pygame.draw.rect(canvas, (255,0,0), (70,140,354,200), 2)
    draw_text(canvas, t("you_lose"), 40, GAME_W//2, 180, COLOR_LOSE)
    
    mx, my = get_mouse_pos()
    b_try = pygame.Rect(100, 250, 130, 40)
    b_sol = pygame.Rect(260, 250, 130, 40)
    draw_button(canvas, b_try, t("try_again"), b_try.collidepoint((mx,my)))
    if Dijkstra: draw_button(canvas, b_sol, t("solution"), b_sol.collidepoint((mx,my)), (0,100,0))
    else: draw_button(canvas, b_sol, t("no_ai"), False, (50,50,50))
    return b_try, b_sol

def game_win_popup():
    s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    s.fill(COLOR_OVERLAY)
    canvas.blit(s, (0,0))
    pygame.draw.rect(canvas, (50,50,50), (50,140,394,200))
    pygame.draw.rect(canvas, (0,200,0), (50,140,394,200), 2)
    draw_text(canvas, t("you_escaped"), 40, GAME_W//2, 180, COLOR_WIN)
    
    mx, my = get_mouse_pos()
    b_again = pygame.Rect(60, 250, 110, 40)
    b_home = pygame.Rect(185, 250, 110, 40)
    b_next = pygame.Rect(310, 250, 110, 40)
    draw_button(canvas, b_again, t("again"), b_again.collidepoint((mx,my)))
    draw_button(canvas, b_home, t("home"), b_home.collidepoint((mx,my)))
    draw_button(canvas, b_next, t("next"), b_next.collidepoint((mx,my)), (0,100,0) if not b_next.collidepoint((mx,my)) else (0,150,0))
    return b_again, b_home, b_next

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s

def alphanum_key(s):
    """Sắp xếp tự nhiên: map1, map2, ..., map10"""
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def get_sorted_maps():
    """Lấy danh sách map đã sắp xếp từ dễ đến khó"""
    try:
        files = os.listdir(maze_path)
        # Chỉ lấy file .txt
        v = [f for f in files if f.endswith('.txt')]
        # Sắp xếp theo số (Natural sort)
        v.sort(key=alphanum_key)
        return v
    except:
        return []

def get_next_map(curr):
    v = get_sorted_maps()
    if curr in v:
        idx = v.index(curr)
        if idx + 1 < len(v): return v[idx+1]
    return None

class GameState:
    def __init__(self, file_name):
        self.screen_size_x = GAME_W
        self.screen_size_y = GAME_H
        self.maze_rect = 360
        self.coordinate_screen_x = 67
        self.coordinate_screen_y = 80
        self.get_input_maze(file_name)
        self.get_input_object(file_name)
        self.gate = {}
        if self.gate_position:
            self.gate = { "gate_position": self.gate_position, "isClosed": True, "cellIndex": 0 }
        if self.explorer_position[1] // 2 <= self.maze_size // 2: self.explorer_direction = "RIGHT"
        else: self.explorer_direction = "LEFT"
        self.mummy_white_direction = ["DOWN"] * len(self.mummy_white_position)
        self.mummy_red_direction = ["DOWN"] * len(self.mummy_red_position)
        self.scorpion_white_direction = ["DOWN"] * len(self.scorpion_white_position)
        self.scorpion_red_direction = ["DOWN"] * len(self.scorpion_red_position)
        self.history = []

    def get_input_maze(self, name):
        self.maze = []
        path = os.path.join(maze_path, name)
        if not os.path.exists(path): sys.exit(f"File {name} not found")
        with open(path,"r") as file:
            for line in file:
                row = [c for c in line if c != '\n' and c != '\r']
                if row: self.maze.append(row)
        self.maze_size = len(self.maze) // 2
        self.cell_rect = self.maze_rect // self.maze_size
        self.stair_position = self.key_position = self.gate_position = ()
        self.traps = [] 
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == 'S': self.stair_position = (i, j)
                
                # --- SỬA ĐOẠN NÀY ---
                if self.maze[i][j] == 'T': 
                    # Chỉ thêm trap nếu danh sách đang trống (chưa có trap nào)
                    if not self.traps:
                        self.traps.append((i, j))
                    else:
                        # Nếu đã có trap rồi thì biến các trap thừa thành đường đi (xóa logic bẫy)
                        self.maze[i][j] = ' ' 
                # --------------------

                if self.maze[i][j] == 'K': self.key_position = (i, j)
                if self.maze[i][j] == 'G': self.gate_position = (i, j)
        self.trap_position = self.traps[0] if self.traps else ()

    def get_input_object(self, name):
        self.mummy_white_position = []
        self.mummy_red_position = []
        self.scorpion_white_position = []
        self.scorpion_red_position = []
        
        agent_file = name if "temp" not in name else "temp_random_agents.txt"
        path = os.path.join(object_path, agent_file)
        if not os.path.exists(path):
            self.explorer_position = [1, 1]
            return

        with open(path, "r") as file:
            for line in file:
                x = line.split()
                if not x: continue
                if x[0] == 'E': self.explorer_position = [int(x[1]), int(x[2])]
                elif x[0] == 'MW': self.mummy_white_position.append([int(x[1]), int(x[2])])
                elif x[0] == 'MR': self.mummy_red_position.append([int(x[1]), int(x[2])])
                elif x[0] == 'SW': self.scorpion_white_position.append([int(x[1]), int(x[2])])
                elif x[0] == 'SR': self.scorpion_red_position.append([int(x[1]), int(x[2])])

    def show_information(self): pass

    def save_state(self, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars):
        state = {
            'exp_pos': (explorer_char.get_x(), explorer_char.get_y()),
            'mw_pos': [(m.get_x(), m.get_y()) for m in mw_chars],
            'mr_pos': [(m.get_x(), m.get_y()) for m in mr_chars],
            'sw_pos': [(s.get_x(), s.get_y()) for s in sw_chars],
            'sr_pos': [(s.get_x(), s.get_y()) for s in sr_chars],
            'gate': copy.deepcopy(self.gate)
        }
        self.history.append(state)

    def undo(self, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars):
        if not self.history: return False
        state = self.history.pop()
        explorer_char.move_xy(state['exp_pos'][0], state['exp_pos'][1])
        for i, m in enumerate(mw_chars):
            if i < len(state['mw_pos']): m.move_xy(state['mw_pos'][i][0], state['mw_pos'][i][1])
        for i, m in enumerate(mr_chars):
            if i < len(state['mr_pos']): m.move_xy(state['mr_pos'][i][0], state['mr_pos'][i][1])
        for i, m in enumerate(sw_chars):
            if i < len(state['sw_pos']): m.move_xy(state['sw_pos'][i][0], state['sw_pos'][i][1])
        for i, m in enumerate(sr_chars):
            if i < len(state['sr_pos']): m.move_xy(state['sr_pos'][i][0], state['sr_pos'][i][1])
        self.gate = state['gate']
        return True

    def reset(self, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars):
        """Reset game to initial state"""
        # Reset explorer position
        explorer_char.move_xy(self.explorer_position[0], self.explorer_position[1])
        
        # Reset enemies to initial positions
        for i, m in enumerate(mw_chars):
            if i < len(self.mummy_white_position):
                m.move_xy(self.mummy_white_position[i][0], self.mummy_white_position[i][1])
        for i, m in enumerate(mr_chars):
            if i < len(self.mummy_red_position):
                m.move_xy(self.mummy_red_position[i][0], self.mummy_red_position[i][1])
        for i, s in enumerate(sw_chars):
            if i < len(self.scorpion_white_position):
                s.move_xy(self.scorpion_white_position[i][0], self.scorpion_white_position[i][1])
        for i, s in enumerate(sr_chars):
            if i < len(self.scorpion_red_position):
                s.move_xy(self.scorpion_red_position[i][0], self.scorpion_red_position[i][1])
        
        # Reset gate
        if self.gate_position:
            self.gate = {"gate_position": self.gate_position, "isClosed": True, "cellIndex": 0}
        
        # Clear history
        self.history = []
        return True

def load_image_path(size):
    d = os.path.join(project_path, "image")
    return (os.path.join(d, "backdrop.png"), os.path.join(d, f"floor{size}.jpg"), os.path.join(d, f"walls{size}.png"),
            os.path.join(d, f"key{size}.png"), os.path.join(d, f"gate{size}.png"), os.path.join(d, f"trap{size}.png"),
            os.path.join(d, f"stairs{size}.png"), os.path.join(d, f"explorer{size}.png"), os.path.join(d, f"mummy_white{size}.png"),
            os.path.join(d, f"redmummy{size}.png"), os.path.join(d, f"white_scorpion{size}.png"), os.path.join(d, f"red_scorpion{size}.png"))

def Cal_coordinates(game, position_x, position_y):
    coordinate_x = game.coordinate_screen_x + game.cell_rect * (position_y // 2)
    coordinate_y = game.coordinate_screen_y + game.cell_rect * (position_x // 2)
    if position_x - 1 >= 0 and (game.maze[position_x - 1][position_y] == "%" or game.maze[position_x - 1][position_y] == "G"):
        coordinate_y += 3
    return [coordinate_x, coordinate_y]

def character_same_place_with_key(character, key_position, gate, render, game, backdrop, floor, stair, stair_position, trap, trap_position,
                key, gate_sheet, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red):
    if key_position and character.get_x() == key_position[0] and character.get_y() == key_position[1]:
        gate["isClosed"] = not gate["isClosed"]
        gate["cellIndex"] = 0 if gate["isClosed"] else -1
        if render:
            graphics.gate_animation(canvas, game, backdrop, floor, stair, stair_position, trap, trap_position,
                           key, key_position, gate_sheet, gate, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red)
            pygame.display.flip()
    return gate

def update_list_character(list_character, list_sprite_sheet_character):
    i = 0
    while i < len(list_character):
        j = 0
        while j < len(list_character):
            if j != i and list_character[i].check_same_position(list_character[j]):
                del list_character[j]
                del list_sprite_sheet_character[j]
            j += 1
        i += 1
    return list_character, list_sprite_sheet_character

def update_lists_character(list_strong_scharacter, list_week_scharacter, list_sprite_sheet_week_character):
    for i in range(len(list_strong_scharacter)):
        j = 0
        while j < len(list_week_scharacter):
            if list_strong_scharacter[i].check_same_position(list_week_scharacter[j]):
                del list_week_scharacter[j]
                del list_sprite_sheet_week_character[j]
            j += 1
    return list_week_scharacter, list_sprite_sheet_week_character

def check_explorer_is_killed(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character,
                            scorpion_red_character, trap_list):
    if trap_list:
        for t in trap_list:
            if explorer_character.get_x() == t[0] and explorer_character.get_y() == t[1]: return True
    for l in [mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character]:
        for e in l:
            if explorer_character.get_x() == e.get_x() and explorer_character.get_y() == e.get_y(): return True
    return False

def update_enemy_position(render, game, backdrop, floor, stair, trap, key, gate, wall, explorer, explorer_character,mummy_white_character,
                        mummy_red_character, scorpion_white_character, scorpion_red_character, list_mummy_white,
                         list_mummy_red, list_scorpion_white, list_scorpion_red):
    game.gate = character_same_place_with_key(explorer_character, game.key_position, game.gate, render, game,
                                              backdrop, floor, stair, game.stair_position, trap, game.trap_position,
                                              key, gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
    if check_explorer_is_killed(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character, game.traps): return True

    for _ in range(2): # 2 steps
        mw_past = []; mw_new = []
        for i in range(len(mummy_white_character)):
            mw_past.append([mummy_white_character[i].get_x(), mummy_white_character[i].get_y()])
            mummy_white_character[i] = mummy_white_character[i].white_move(game.maze, game.gate, explorer_character)
            mw_new.append([mummy_white_character[i].get_x(), mummy_white_character[i].get_y()])
        for i in range(len(mummy_white_character)):
            game.gate = character_same_place_with_key(mummy_white_character[i], game.key_position, game.gate, render, game, backdrop, floor, stair, game.stair_position, trap, game.trap_position, key, gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)

        mr_past = []; mr_new = []
        for i in range(len(mummy_red_character)):
            mr_past.append([mummy_red_character[i].get_x(), mummy_red_character[i].get_y()])
            mummy_red_character[i] = mummy_red_character[i].red_move(game.maze, game.gate, explorer_character)
            mr_new.append([mummy_red_character[i].get_x(), mummy_red_character[i].get_y()])
        for i in range(len(mummy_red_character)):
            game.gate = character_same_place_with_key(mummy_red_character[i], game.key_position, game.gate, render, game, backdrop, floor, stair, game.stair_position, trap, game.trap_position, key, gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)

        sw_past = []; sw_new = []
        for i in range(len(scorpion_white_character)):
            sw_past.append([scorpion_white_character[i].get_x(), scorpion_white_character[i].get_y()])
            scorpion_white_character[i] = scorpion_white_character[i].white_move(game.maze, game.gate, explorer_character)
            sw_new.append([scorpion_white_character[i].get_x(), scorpion_white_character[i].get_y()])
        for i in range(len(scorpion_white_character)):
            game.gate = character_same_place_with_key(scorpion_white_character[i], game.key_position, game.gate, render, game, backdrop, floor, stair, game.stair_position, trap, game.trap_position, key, gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)

        sr_past = []; sr_new = []
        for i in range(len(scorpion_red_character)):
            sr_past.append([scorpion_red_character[i].get_x(), scorpion_red_character[i].get_y()])
            scorpion_red_character[i] = scorpion_red_character[i].red_move(game.maze, game.gate, explorer_character)
            sr_new.append([scorpion_red_character[i].get_x(), scorpion_red_character[i].get_y()])
        for i in range(len(scorpion_red_character)):
            game.gate = character_same_place_with_key(scorpion_red_character[i], game.key_position, game.gate, render, game, backdrop, floor, stair, game.stair_position, trap, game.trap_position, key, gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)

        if render:
            graphics.enemy_move_animation(mw_past, mw_new, mr_past, mr_new, sw_past, sw_new, sr_past, sr_new,
                                          canvas, game, backdrop, floor, stair, game.stair_position, trap,
                                          game.trap_position, key, game.key_position, gate, game.gate, wall,
                                          explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
            pygame.display.flip()

        if check_explorer_is_killed(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character, game.traps): return True

        mummy_white_character, list_mummy_white = update_list_character(mummy_white_character, list_mummy_white)
        mummy_red_character, list_mummy_red = update_list_character(mummy_red_character, list_mummy_red)
        if mummy_red_character: mummy_red_character, list_mummy_red = update_lists_character(mummy_white_character, mummy_red_character, list_mummy_red)
        if scorpion_white_character: scorpion_white_character, list_scorpion_white = update_lists_character(mummy_white_character, scorpion_white_character, list_scorpion_white)
        if scorpion_red_character: scorpion_red_character, list_scorpion_red = update_lists_character(mummy_white_character, scorpion_red_character, list_scorpion_red)
        if scorpion_white_character: scorpion_white_character, list_scorpion_white = update_lists_character(mummy_red_character, scorpion_white_character, list_scorpion_white)
        if scorpion_red_character: scorpion_red_character, list_scorpion_red = update_lists_character(mummy_red_character, scorpion_red_character, list_scorpion_red)
        if scorpion_red_character: scorpion_red_character, list_scorpion_red = update_lists_character(scorpion_white_character, scorpion_red_character, list_scorpion_red)

    return False

def run_ai_solver(game, assets):
    print("AI SOLVING WITH DIJKSTRA...")
    (backdrop, floor, wall, key, gate_img, trap, stair, exp_s, mw_s, mr_s, sw_s, sr_s) = assets
    exp = characters.Explorer(game.explorer_position[0], game.explorer_position[1])
    mws = [characters.mummy_white(p[0], p[1]) for p in game.mummy_white_position]
    mrs = [characters.mummy_red(p[0], p[1]) for p in game.mummy_red_position]
    sws = [characters.scorpion_white(p[0], p[1]) for p in game.scorpion_white_position]
    srs = [characters.scorpion_red(p[0], p[1]) for p in game.scorpion_red_position]

    if Dijkstra:
        ans = Dijkstra(exp, mws, mrs, sws, srs, game.gate, game.traps, game.key_position, game.maze)
    else:
        return False

    if not ans:
        print("NO SOLUTION FOUND!")
        return False

    exp_d = {"sprite_sheet": exp_s, "coordinates": Cal_coordinates(game, exp.get_x(), exp.get_y()), "direction": game.explorer_direction, "cellIndex": 0}
    list_mw = [{"sprite_sheet": mw_s, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.mummy_white_position]
    list_mr = [{"sprite_sheet": mr_s, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.mummy_red_position]
    list_sw = [{"sprite_sheet": sw_s, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.scorpion_white_position]
    list_sr = [{"sprite_sheet": sr_s, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.scorpion_red_position]

    for i in range(1, len(ans)): 
        nx, ny = ans[i]
        dx, dy = nx - exp.get_x(), ny - exp.get_y()
        if dx == -2: exp_d["direction"] = "UP"
        elif dx == 2: exp_d["direction"] = "DOWN"
        elif dy == -2: exp_d["direction"] = "LEFT"
        elif dy == 2: exp_d["direction"] = "RIGHT"
        
        pygame.time.wait(200)

        exp.move(nx, ny, True, canvas, game, backdrop, floor, stair, game.stair_position, trap, game.trap_position, 
                 key, game.key_position, gate_img, game.gate, wall, exp_d, list_mw, list_mr, list_sw, list_sr)
        
        update_enemy_position(True, game, backdrop, floor, stair, trap, key, gate_img, wall, exp_d, exp, mws, mrs, sws, srs, list_mw, list_mr, list_sw, list_sr)
        
        pygame.display.flip() 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: sys.exit()
    
    return True

def rungame(layout, auth_manager=None, load_data=None):
    current_map = layout
    render = True
    
    # If loading from save, use saved map
    if load_data:
        current_map = load_data.get('current_map', layout)

    while True:
        game = GameState(current_map)
        game.show_information()
        path_tuple = load_image_path(game.maze_size)
        raw_backdrop = pygame.image.load(path_tuple[0])
        # Ép ảnh nền về đúng kích thước chuẩn của game (494x480)
        # Dùng smoothscale để ảnh vẫn nét mà không bị vỡ bố cục
        backdrop = pygame.transform.smoothscale(raw_backdrop, (GAME_W, GAME_H))
        
        floor = pygame.image.load(path_tuple[1])
        floor = pygame.image.load(path_tuple[1])
        wall = graphics.wall_spritesheet(path_tuple[2], game.maze_size)
        key = graphics.key_spritesheet(path_tuple[3])
        gate = graphics.gate_spritesheet(path_tuple[4])
        trap = graphics.trap_spritesheet(path_tuple[5])
        stair = graphics.stairs_spritesheet(path_tuple[6])
        exp_sheet = graphics.character_spritesheet(path_tuple[7])
        mw_sheet = graphics.character_spritesheet(path_tuple[8])
        mr_sheet = graphics.character_spritesheet(path_tuple[9])
        sw_sheet = graphics.character_spritesheet(path_tuple[10])
        sr_sheet = graphics.character_spritesheet(path_tuple[11])
        assets = (backdrop, floor, wall, key, gate, trap, stair, exp_sheet, mw_sheet, mr_sheet, sw_sheet, sr_sheet)

        explorer = { "sprite_sheet": exp_sheet, "coordinates": Cal_coordinates(game, game.explorer_position[0], game.explorer_position[1]), "direction": game.explorer_direction, "cellIndex": 0 }
        list_mummy_white = [{"sprite_sheet": mw_sheet, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.mummy_white_position]
        list_mummy_red = [{"sprite_sheet": mr_sheet, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.mummy_red_position]
        list_scorpion_white = [{"sprite_sheet": sw_sheet, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.scorpion_white_position]
        list_scorpion_red = [{"sprite_sheet": sr_sheet, "coordinates": Cal_coordinates(game, p[0], p[1]), "direction": "DOWN", "cellIndex": 0} for p in game.scorpion_red_position]

        graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
        pygame.display.flip()

        explorer_character = characters.Explorer(game.explorer_position[0], game.explorer_position[1])
        mummy_white_character = [characters.mummy_white(p[0], p[1]) for p in game.mummy_white_position]
        mummy_red_character = [characters.mummy_red(p[0], p[1]) for p in game.mummy_red_position]
        scorpion_white_character = [characters.scorpion_white(p[0], p[1]) for p in game.scorpion_white_position]
        scorpion_red_character = [characters.scorpion_red(p[0], p[1]) for p in game.scorpion_red_position]
        
        # Initialize navigation bar
        nav_bar = NavigationBar(GAME_W)
        set_nav_bar(nav_bar)  # Set it globally so it's drawn on every frame
        
        # Load from save data if provided
        if load_data and 'game_state' in load_data:
            gs = load_data['game_state']
            explorer_character.move_xy(gs['explorer_position'][0], gs['explorer_position'][1])
            game.explorer_direction = gs.get('explorer_direction', game.explorer_direction)
            game.gate = gs.get('gate', game.gate)
            game.history = gs.get('history', [])
            
            # Restore enemy positions
            for i, pos in enumerate(gs.get('mummy_white_positions', [])):
                if i < len(mummy_white_character):
                    mummy_white_character[i].move_xy(pos[0], pos[1])
            for i, pos in enumerate(gs.get('mummy_red_positions', [])):
                if i < len(mummy_red_character):
                    mummy_red_character[i].move_xy(pos[0], pos[1])
            for i, pos in enumerate(gs.get('scorpion_white_positions', [])):
                if i < len(scorpion_white_character):
                    scorpion_white_character[i].move_xy(pos[0], pos[1])
            for i, pos in enumerate(gs.get('scorpion_red_positions', [])):
                if i < len(scorpion_red_character):
                    scorpion_red_character[i].move_xy(pos[0], pos[1])
            
            # Update display
            explorer["coordinates"] = Cal_coordinates(game, explorer_character.get_x(), explorer_character.get_y())
            explorer["direction"] = game.explorer_direction
            for i, m in enumerate(mummy_white_character): 
                list_mummy_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
            for i, m in enumerate(mummy_red_character): 
                list_mummy_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
            for i, s in enumerate(scorpion_white_character): 
                list_scorpion_white[i]["coordinates"] = Cal_coordinates(game, s.get_x(), s.get_y())
            for i, s in enumerate(scorpion_red_character): 
                list_scorpion_red[i]["coordinates"] = Cal_coordinates(game, s.get_x(), s.get_y())
            graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
            pygame.display.flip()

        isEnd = False
        isWin = False
        loop_running = True
        
        while loop_running:
            if isEnd:
                btn_try, btn_sol = game_over_popup()
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = get_mouse_pos()
                            if btn_try.collidepoint((mx, my)): waiting=False; loop_running=False 
                            elif btn_sol.collidepoint((mx, my)):
                                waiting=False
                                if run_ai_solver(game, assets):
                                    isWin = True
                                    isEnd = False
                                    waiting = False
                continue
            
            if isWin:
                b_again, b_home, b_next = game_win_popup()
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = get_mouse_pos()
                            if b_again.collidepoint((mx, my)): waiting=False; loop_running=False
                            elif b_home.collidepoint((mx, my)): clear_nav_bar(); return
                            elif b_next.collidepoint((mx, my)):
                                next_map = get_next_map(current_map)
                                if next_map: current_map = next_map; waiting=False; loop_running=False
                                else: clear_nav_bar(); return
                continue

                continue

            ex = explorer_character.get_x()
            ey = explorer_character.get_y()
            nex, ney = ex, ey
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: clear_nav_bar(); return
                if event.type == pygame.VIDEORESIZE: pygame.display.flip()
                
                # 1. XỬ LÝ CLICK CHUỘT (NAV BAR + DI CHUYỂN)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = get_mouse_pos()
                    
                    # A. Nếu click vào Nav Bar (Menu trên cùng)
                    if nav_bar.is_in_nav_bar((mx, my)):
                        button_clicked = nav_bar.get_clicked_button((mx, my))
                        if button_clicked == "save":
                            if auth_manager and auth_manager.is_logged_in():
                                save_result = save_game_menu(auth_manager, game, explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character, current_map)
                                if save_result: clear_nav_bar(); return
                                graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                                pygame.display.flip()
                        elif button_clicked == "undo":
                            if game.undo(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character):
                                explorer["coordinates"] = Cal_coordinates(game, explorer_character.get_x(), explorer_character.get_y())
                                for i, m in enumerate(mummy_white_character): list_mummy_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(mummy_red_character): list_mummy_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(scorpion_white_character): list_scorpion_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(scorpion_red_character): list_scorpion_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                                pygame.display.flip()
                        elif button_clicked == "reset":
                            if game.reset(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character):
                                explorer["coordinates"] = Cal_coordinates(game, explorer_character.get_x(), explorer_character.get_y())
                                explorer["direction"] = game.explorer_direction
                                for i, m in enumerate(mummy_white_character): list_mummy_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(mummy_red_character): list_mummy_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(scorpion_white_character): list_scorpion_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                for i, m in enumerate(scorpion_red_character): list_scorpion_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                                graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                                pygame.display.flip()
                        elif button_clicked == "exit":
                            clear_nav_bar(); return

                    # B. Nếu click vào Bản đồ (DI CHUYỂN NHÂN VẬT)
                    else:
                        click_col = int((mx - game.coordinate_screen_x) // game.cell_rect)
                        click_row = int((my - game.coordinate_screen_y) // game.cell_rect)
                        curr_col = ey // 2
                        curr_row = ex // 2
                        max_h, max_w = len(game.maze), len(game.maze[0])

                        # Kiểm tra click vào ô lân cận để di chuyển
                        moved_by_mouse = False
                        if click_col == curr_col and click_row == curr_row - 1: # Click Lên
                            if ex - 2 >= 0 and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex - 2, ey):
                                nex -= 2; explorer["direction"] = "UP"; moved_by_mouse = True
                        elif click_col == curr_col and click_row == curr_row + 1: # Click Xuống
                            if ex + 2 < max_h and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex + 2, ey):
                                nex += 2; explorer["direction"] = "DOWN"; moved_by_mouse = True
                        elif click_row == curr_row and click_col == curr_col - 1: # Click Trái
                            if ey - 2 >= 0 and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex, ey - 2):
                                ney -= 2; explorer["direction"] = "LEFT"; moved_by_mouse = True
                        elif click_row == curr_row and click_col == curr_col + 1: # Click Phải
                            if ey + 2 < max_w and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex, ey + 2):
                                ney += 2; explorer["direction"] = "RIGHT"; moved_by_mouse = True
                        
                        # [QUAN TRỌNG] Thực thi di chuyển ngay lập tức khi click chuột
                        if moved_by_mouse:
                            game.save_state(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character)
                            explorer_character.move(nex, ney, render, canvas, game, backdrop, floor,
                                                    stair, game.stair_position, trap, game.trap_position, key, game.key_position,
                                                    gate, game.gate, wall, explorer,
                                                    list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                            
                            isEnd = update_enemy_position(render, game, backdrop, floor, stair, trap, key, gate, wall, explorer,
                                                explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character,
                                                list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)

                # 2. XỬ LÝ BÀN PHÍM
                if event.type == pygame.KEYDOWN:
                    max_h, max_w = len(game.maze), len(game.maze[0])
                    # Win Check
                    if event.key == pygame.K_UP and ex > 0 and game.maze[ex-1][ey] == "S": isWin=True; break
                    if event.key == pygame.K_DOWN and ex < max_h-1 and game.maze[ex+1][ey] == "S": isWin=True; break
                    if event.key == pygame.K_LEFT and ey > 0 and game.maze[ex][ey-1] == "S": isWin=True; break
                    if event.key == pygame.K_RIGHT and ey < max_w-1 and game.maze[ex][ey+1] == "S": isWin=True; break
                    
                    if event.key == pygame.K_u: # Undo
                        if game.undo(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character):
                            explorer["coordinates"] = Cal_coordinates(game, explorer_character.get_x(), explorer_character.get_y())
                            for i, m in enumerate(mummy_white_character): list_mummy_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(mummy_red_character): list_mummy_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(scorpion_white_character): list_scorpion_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(scorpion_red_character): list_scorpion_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                            pygame.display.flip()
                        continue
                    
                    if event.key == pygame.K_r: # Reset
                        if game.reset(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character):
                            explorer["coordinates"] = Cal_coordinates(game, explorer_character.get_x(), explorer_character.get_y())
                            explorer["direction"] = game.explorer_direction
                            for i, m in enumerate(mummy_white_character): list_mummy_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(mummy_red_character): list_mummy_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(scorpion_white_character): list_scorpion_white[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            for i, m in enumerate(scorpion_red_character): list_scorpion_red[i]["coordinates"] = Cal_coordinates(game, m.get_x(), m.get_y())
                            graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                            pygame.display.flip()
                        continue
                    
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL: # Save
                        if auth_manager and auth_manager.is_logged_in():
                            save_result = save_game_menu(auth_manager, game, explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character, current_map)
                            if save_result: clear_nav_bar(); return
                            graphics.draw_screen(canvas, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, game.stair_position, trap, game.trap_position, key, game.key_position, gate, game.gate, wall, explorer, list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                            pygame.display.flip()
                        continue

                    # Logic Di chuyển bằng Phím
                    if event.key == pygame.K_UP:
                        if ex - 2 >= 0 and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex - 2, ey):
                            nex -= 2; explorer["direction"] = "UP"
                    if event.key == pygame.K_DOWN:
                        if ex + 2 < max_h and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex + 2, ey):
                            nex += 2; explorer["direction"] = "DOWN"
                    if event.key == pygame.K_LEFT:
                        if ey - 2 >= 0 and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex, ey - 2):
                            ney -= 2; explorer["direction"] = "LEFT"
                    if event.key == pygame.K_RIGHT:
                        if ey + 2 < max_w and explorer_character.eligible_character_move(game.maze, game.gate, ex, ey, ex, ey + 2):
                            ney += 2; explorer["direction"] = "RIGHT"
                    
                    # [QUAN TRỌNG] Thực thi di chuyển nếu có thay đổi toạ độ từ bàn phím
                    if ex != nex or ey != ney:
                        game.save_state(explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character)
                        explorer_character.move(nex, ney, render, canvas, game, backdrop, floor,
                                                 stair, game.stair_position, trap, game.trap_position, key, game.key_position,
                                                 gate, game.gate, wall, explorer,
                                                 list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
                        
                        isEnd = update_enemy_position(render, game, backdrop, floor, stair, trap, key, gate, wall, explorer,
                                              explorer_character, mummy_white_character, mummy_red_character, scorpion_white_character, scorpion_red_character,
                                              list_mummy_white, list_mummy_red, list_scorpion_white, list_scorpion_red)
            
            # Update mouse position for nav bar (display hook will draw it)
            get_mouse_pos()
            pygame.display.flip()

if __name__ == '__main__':
    init_display()
    auth_manager = None
    
    while True:
        # Show login menu first (can skip)
        try:
            from game_utils import AuthManager
            auth_manager = login_menu()
            if auth_manager is None:
                # User skipped login, create an empty AuthManager
                auth_manager = AuthManager()
        except ImportError as e:
            print(f"Warning: Could not import game_utils: {e}")
            print("Login and save/load features will be disabled.")
            # Create a dummy auth_manager that won't cause errors
            class DummyAuthManager:
                def is_logged_in(self): return False
                def get_current_user(self): return None
            auth_manager = DummyAuthManager()
        
        while True:
            choice, auth_manager = main_menu(auth_manager)
            
            if choice == "login":
                # User clicked logout, go back to login
                break
            
            valid_maps = []
            try:
                files = os.listdir(maze_path)
                valid_maps = [f for f in files if f.endswith('.txt')]
                valid_maps.sort()
            except: pass
            
            layout = None
            load_data = None
            
            if choice == "load":
                # Load game menu
                if auth_manager and auth_manager.is_logged_in():
                    try:
                        from game_utils import SaveManager
                        save_manager = SaveManager(auth_manager)
                        save_name = load_game_menu(auth_manager)
                        if save_name:
                            success, data, msg = save_manager.load_game(save_name)
                            if success and data:
                                layout = data.get('current_map')
                                if layout:
                                    load_data = data
                                    print(f"Load successful! Map: {layout}, Data loaded: {load_data is not None}")
                                    # Don't continue here - let it proceed to run the game below
                                else:
                                    print(f"ERROR: Save file does not contain 'current_map' field!")
                                    continue
                            else:
                                # Show error and continue
                                print(f"Load failed: {msg}")
                                continue
                        else:
                            # User clicked BACK or closed menu
                            continue
                    except Exception as e:
                        print(f"Error loading: {e}")
                        continue
                else:
                    # Not logged in
                    continue
            
            elif choice == "random":
                # ... (Giữ nguyên logic random)
                layout = "temp_random.txt"
                
            # --- SỬA ĐOẠN NÀY (Thay cho choice == "select") ---
            elif choice == "adventure": 
                # Lấy danh sách map đã sắp xếp
                maps = get_sorted_maps()
                if maps:
                    layout = maps[0] # Lấy map đầu tiên (Dễ nhất/Level 1)
                    print(f"Starting Adventure Mode: {layout}")
                else:
                    print("No maps found in 'map/maze' folder!")
            
            # (Bạn có thể xoá hoặc comment lại phần select_map_screen nếu không dùng nữa)
            # elif choice == "select" and valid_maps: 
            #    layout = select_map_screen(valid_maps)
            
            if layout:
                print(f"Starting map: {layout}")
                if load_data:
                    print(f"Loading saved game state...")
                try: 
                    rungame(layout, auth_manager, load_data)
                except Exception as e: 
                    import traceback
                    traceback.print_exc()
            elif choice == "load":
                # This shouldn't happen if load was successful
                print(f"ERROR: Load menu returned but layout is None! This might mean the save file is corrupted.")
                print(f"Please try loading a different save or create a new game.")