import os
import graphics
import pygame


class character:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def check_same_position(self, character):
        return (character.x == self.x) and (character.y == self.y)
    def inboard(x, y) :
        return x > 1 and x <= len(maze) and y >= 1 and y <= len(maze)
    def eligible_character_move(self, maze, gate, x, y, new_x, new_y):
        if not maze or len(maze) == 0: return False
        if new_x < 0 or new_x >= len(maze) or new_y < 0 or new_y >= len(maze[0]): return False
            
        if maze[new_x][new_y] == "%": return False

        mid_x = (x + new_x) // 2
        mid_y = (y + new_y) // 2
        if maze[mid_x][mid_y] == "%": return False

        if gate and "gate_position" in gate and gate["isClosed"]:
            gx, gy = gate["gate_position"]
            

            locked_row = (gx // 2) * 2 + 1
            locked_col = (gy // 2) * 2 + 1
            
            if new_x == locked_row and new_y == locked_col:
                print(f"BLOCK: Cannot ENTER the Gate Cell ({new_x}, {new_y})")
                return False

            if x == locked_row and y == locked_col:
                print(f"BLOCK: Cannot EXIT the Gate Cell")
                return False

        cell_char = maze[mid_x][mid_y]
        if (cell_char == "G" or (gate and gate.get("gate_position") == (mid_x, mid_y))) and gate["isClosed"]:
            return False
        
        return True

    def move_animation(self, x, y, screen, game, backdrop, floor, stair, stair_position, trap, trap_position,
                key, key_position, gate_sheet, gate, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red):
        raise NotImplementedError("This is base class method")

    def move_xy(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def move(self, new_x, new_y, render, screen, game, backdrop, floor, stair, stair_position, trap, trap_position,
                key, key_position, gate_sheet, gate, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red):
        if render:
            self.move_animation(new_x, new_y, screen, game, backdrop, floor, stair, stair_position, trap, trap_position,
                key, key_position, gate_sheet, gate, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red)
        self.x = new_x
        self.y = new_y

    def set_x(self, x):
        self.x = x
    def set_y(self, y):
        self.y = y
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y

class Explorer(character):
    exp_walk_sound = None
    def move_animation(self, x, y, screen, game, backdrop, floor, stair, stair_position, trap, trap_position,
                key, key_position, gate_sheet, gate, wall, explorer, mummy_white, mummy_red, scorpion_white, scorpion_red):

        if Explorer.exp_walk_sound is None:
            sound_path = os.path.join("sound", "expwalk.wav")
            Explorer.exp_walk_sound = pygame.mixer.Sound(sound_path)
            Explorer.exp_walk_sound.set_volume(0.4)
 
        explorer_start_x = game.coordinate_screen_x + game.cell_rect * (self.y // 2)
        explorer_start_y = game.coordinate_screen_y + game.cell_rect * (self.x // 2)
        if game.maze[x - 1][y] == "%" or game.maze[x - 1][y] == "G":
            explorer_start_y += 3
        explorer["coordinates"] = [explorer_start_x, explorer_start_y]
        step_stride = game.cell_rect // 5
        coordinates = list(explorer["coordinates"])
        for i in range(6):
            if i == 0:
                if not pygame.mixer.Channel(0).get_busy():
                    pygame.mixer.Channel(0).play(Explorer.exp_walk_sound)
                    
            if i < 5:
                if explorer["direction"] == "UP":
                    coordinates[1] -= step_stride
                if explorer["direction"] == "DOWN":
                    coordinates[1] += step_stride
                if explorer["direction"] == "LEFT":
                    coordinates[0] -= step_stride
                if explorer["direction"] == "RIGHT":
                    coordinates[0] += step_stride
            explorer["coordinates"] = list(coordinates)
            explorer["cellIndex"] = i % 5
            graphics.draw_screen(screen, game.maze, backdrop, floor, game.maze_size, game.cell_rect, stair, stair_position,
                                trap, trap_position, key, key_position, gate_sheet, gate, wall, \
                                explorer, mummy_white, mummy_red, scorpion_white, scorpion_red)
            pygame.time.delay(85)
            pygame.display.update()

class enemy(character):
    def __init__(self, x, y):
        self.attempt = 0
        self.step_count = 0
        super().__init__(x, y)

    def move_Vertical(self, maze, gate, explorer):
        if self.step_count == 2: return self
        new_x = self.get_x() + 2 * sign(explorer.get_x() - self.get_x())
        new_y = self.get_y()
        if self.eligible_character_move(maze, gate, self.get_x(), self.get_y(), new_x, new_y):
            self.move_xy(new_x, new_y)
            self.step_count += 1
            if self.step_count == 2:
                return self
        else:
            self.attempt += 1
        return self

    def move_Horizontal(self, maze, gate, explorer):
        if self.step_count == 2: return self
        new_x = self.get_x()
        new_y = self.get_y() + 2 * sign(explorer.get_y() - self.get_y())
        if self.eligible_character_move(maze, gate, self.get_x(), self.get_y(), new_x, new_y):
            self.move_xy(new_x, new_y)
            self.step_count += 1
            if self.step_count == 2:
                return self
        else:
            self.attempt += 1
        return self

    def set_attempt(self, attempt):
        self.attempt = attempt
    def get_attempt(self):
        return self.attempt
    def set_step_count(self, step_count):
        self.step_count = step_count
    def get_step_count(self):
        return self.step_count

class mummy_white(enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

    def white_move(self, maze, gate, explorer):
        if self.check_same_position(explorer):
            return self
        else:
            self.set_step_count(0)
            self.set_attempt(0)
            while self.get_attempt() < 5 and self.get_step_count() < 1:
                while self.get_y() != explorer.get_y():
                    self = self.move_Horizontal(maze, gate, explorer)
                    if self.get_step_count() >= 1:
                        return self
                    if self.get_attempt() > 4: break
                if self.check_same_position(explorer):
                    return self
                self = self.move_Vertical(maze, gate, explorer)
                if (self.check_same_position(explorer) or self.get_step_count() >= 1):
                    return self
            return self

class mummy_red(enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

    def red_move(self, maze, gate, explorer):
        if self.check_same_position(explorer):
            return self
        else:
            self.set_step_count(0)
            self.set_attempt(0)
            while self.get_attempt() < 5 and self.get_step_count() < 1:
                while self.get_x() != explorer.get_x():
                    self = self.move_Vertical(maze, gate, explorer)
                    if self.get_step_count() >= 1:
                        return self
                    if self.get_attempt() > 4: break
                if self.check_same_position(explorer):
                    return self
                self = self.move_Horizontal(maze, gate, explorer)
                if (self.check_same_position(explorer) or self.get_step_count() >= 1):
                    return self
            return self

class scorpion_white(mummy_white):
    def __init__(self, x, y):
        super().__init__(x, y)

class scorpion_red(mummy_red):
    def __init(self, x, y):
        super().__init__(x, y)

def sign(x):
    if x == 0:
        return x
    else:
        return x // abs(x)