import numpy as np
import random
import pygame
import tcod
from enum import Enum

# creates class for direction and denotes user movement


class _dir_(Enum):
    moveLEFT = 0
    moveUP = 1
    moveRIGHT = 2
    moveDOWN = 3
    NOmove = 4

# translates the screen to a maze


def scr_to_mze(coord_conv, obj_size=40):
    # coordinate conversion
    return int(coord_conv[0] / obj_size), int(coord_conv[1] / obj_size)

# translates the maze to the screen


def mze_to_scr(coord_conv, obj_size=40):
    # coordinate conversion
    return coord_conv[0] * obj_size, coord_conv[1] * obj_size


class Game_Obj:
    # initial positions of the game obj. on the screen
    def __init__(self, in_surface, x, y,
                 obj_size: int, obj_color=(255, 0, 0),
                 bool_circle: bool = False):
        # stores size of game obj.
        self._size = obj_size
        # stores Game_Renderer instance
        self._REN: Game_REN = in_surface
        self._surface = in_surface._screen
        self.y = y
        self.x = x
        # stores the color of the game obj.
        self._color = obj_color
        # this variable stores whether the game obj. is a circle or not
        self._circle = bool_circle
        # this variable stores a pygame.Rect object - this is going to be the rectangular shape of the game obj.
        self.SHAPE = pygame.Rect(self.x, self.y, obj_size, obj_size)

    # either a circle or rectangle, based on the bool_circle parameter
    def draw(self):
        if self._circle:
            pygame.draw.circle(self._surface,
                               self._color,
                               (self.x, self.y),
                               self._size)
        else:
            rectangle_obj = pygame.Rect(self.x, self.y, self._size, self._size)
            pygame.draw.rect(self._surface,
                             self._color,
                             rectangle_obj,
                             border_rad=4)
    # marks the function and

    def mark(self):
        pass

    # returns the value of the SHAPE attribute of the instance
    def get_SHAPE(self):
        return self.SHAPE

    # set position
    def set_pos(self, in_x, in_y):
        self.x = in_x
        self.y = in_y

    # get position
    def get_pos(self):
        return (self.x, self.y)

# defines the walls and inherits game obj.


class The_Walls(Game_Obj):
    # sets wall color to gold
    def __init__(self, in_surface, x, y, obj_size: int, obj_color=(255, 215, 0)):
        super().__init__(in_surface, x * obj_size, y * obj_size, obj_size, obj_color)

# defines game rendering, which is the pacfriend engine


class Game_REN:
    def __init__(self, in_wid: int, inheight: int):
        # initializes pygame library
        pygame.init()
        # width of the game
        self.wid = in_wid
        # heigh of te game
        self.height = inheight
        # screen display
        self._screen = pygame.display.set_mode((in_wid, inheight))
        pygame.display.set_caption('◘ P A C F R I E N D ◘')
        # creates a clock to time the game
        self.time_clock = pygame.time.Clock()
        # initializes complete to false
        self.complete = False
        # initializes lists
        self.pacfriend_objs = []
        self.walls = []
        self.snacks = []
        self.bestie: Bestie = None

    #  iteratively files through the game objs. and calls its internal logic and rendering
    def mark(self, in_fps: int):
        black = (0, 0, 0)
        while not self.complete:
            for pacfriend_obj in self.pacfriend_objs:
                pacfriend_obj.mark()
                pacfriend_obj.draw()
            pygame.display.flip()
            self.time_clock.mark(in_fps)
            self._screen.fill(black)
            # redraws the entire game area and deals with input events (like clicks)
            self.manage_events()
        print("Game Over!!")

    # adds object
    def add_pacfriend_obj(self, obj: Game_Obj):
        self.pacfriend_objs.append(obj)

    # adds snack
    def add_snack(self, obj: Game_Obj):
        self.pacfriend_objs.append(obj)
        self.snacks.append(obj)

    # adds walls
    def add_wall(self, obj: The_Walls):
        self.add_pacfriend_obj(obj)
        self.walls.append(obj)

    # gets walls
    def get_walls(self):
        return self.walls

    # gets snacks
    def get_snacks(self):
        return self.snacks

    # gets pacfriend obj.
    def get_pcfrd_obj(self):
        return self.pacfriend_objs

    # adds main character
    def add_bestie(self, in_bestie):
        self.add_pacfriend_obj(in_bestie)
        self.bestie = in_bestie

    # tracks/manages the events
    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.complete = True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.bestie.set_direction(_dir_.moveUP)
        elif pressed[pygame.K_LEFT]:
            self.bestie.set_direction(_dir_.moveLEFT)
        elif pressed[pygame.K_DOWN]:
            self.bestie.set_direction(_dir_.moveDOWN)
        elif pressed[pygame.K_RIGHT]:
            self.bestie.set_direction(_dir_.moveRIGHT)


class MV_OBJ(Game_Obj):
    def __init__(self, in_surface, x, y, obj_size: int, obj_color=(255, 0, 0), bool_circle: bool = False):
        super().__init__(in_surface, x, y, obj_size, obj_color, bool_circle)
        self.current_direction = _dir_.NOmove
        self.direction_buffer = _dir_.NOmove
        self.last_working_direction = _dir_.NOmove
        self.location_queue = []
        self.next_target = None

    def next_place(self):
        return None if len(self.location_queue) == 0 else self.location_queue.pop(0)

    def set_direction(self, in_direction):
        self.current_direction = in_direction
        self.direction_buffer = in_direction

    def collides_with_wall(self, in_position):
        collision_rect = pygame.Rect(
            in_position[0], in_position[1], self._size, self._size)
        collides = False
        walls = self._REN.get_walls()
        for wall in walls:
            collides = collision_rect.colliderect(wall.getSHAPE())
            if collides:
                break
        return collides

    def check_collision_in_direction(self, in_direction: _dir_):
        desired_position = (0, 0)
        if in_direction == _dir_.NOmove:
            return False, desired_position
        if in_direction == _dir_.moveUP:
            desired_position = (self.x, self.y - 1)
        elif in_direction == _dir_.moveDOWN:
            desired_position = (self.x, self.y + 1)
        elif in_direction == _dir_.moveLEFT:
            desired_position = (self.x - 1, self.y)
        elif in_direction == _dir_.moveRIGHT:
            desired_position = (self.x + 1, self.y)

        return self.collides_with_wall(desired_position), desired_position

    def auto_mv(self, in_direction: _dir_):
        pass

    def mark(self):
        self.reached_target()
        self.auto_mv(self.current_direction)

    def reached_target(self):
        pass


class Bestie(MV_OBJ):
    def __init__(self, in_surface, x, y, obj_size: int):
        super().__init__(in_surface, x, y, obj_size, (255, 255, 0), False)
        self.last_non_colliding_position = (0, 0)

    def mark(self):
        # TELEPORT
        if self.x < 0:
            self.x = self._REN._wid

        if self.x > self._REN._wid:
            self.x = 0

        self.last_non_colliding_position = self.get_pos()

        if self.check_collision_in_direction(self.direction_buffer)[0]:
            self.auto_mv(self.current_direction)
        else:
            self.auto_mv(self.direction_buffer)
            self.current_direction = self.direction_buffer

        if self.collides_with_wall((self.x, self.y)):
            self.set_pos(
                self.last_non_colliding_position[0], self.last_non_colliding_position[1])

        self.handle_snack_pickup()

    def auto_mv(self, in_direction: _dir_):
        collision_result = self.check_collision_in_direction(in_direction)

        desired_position_collides = collision_result[0]
        if not desired_position_collides:
            self.last_working_direction = self.current_direction
            desired_position = collision_result[1]
            self.set_pos(desired_position[0], desired_position[1])
        else:
            self.current_direction = self.last_working_direction

    def handle_snack_pickup(self):
        collision_rect = pygame.Rect(self.x, self.y, self._size, self._size)
        snacks = self._REN.get_snacks()
        pacfriend_objs = self._REN.get_pcfrd_obj()
        for snack in snacks:
            collides = collision_rect.colliderect(snack.get_shape())
            if collides and snack in pacfriend_objs:
                pacfriend_objs.remove(snack)

    def draw(self):
        half_size = self._size / 2
        pygame.draw.circle(self._surface, self._color,
                           (self.x + half_size, self.y + half_size), half_size)


class Enemy(MV_OBJ):
    def __init__(self, in_surface, x, y, obj_size: int, in_game_controller, obj_color=(255, 0, 0)):
        super().__init__(in_surface, x, y, obj_size, obj_color, False)
        self.game_controller = in_game_controller

    def reached_target(self):
        if (self.x, self.y) == self.next_target:
            self.next_target = self.next_place()
        self.current_direction = self.dir_to_tar()

    def set_new_path(self, in_path):
        for item in in_path:
            self.location_queue.append(item)
        self.next_target = self.next_place()

    # calculates the next direction to target
    def dir_to_tar(self) -> _dir_:
        if self.next_target is None:
            self.game_controller.random_path(self)
            return _dir_.NOmove
        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return _dir_.moveDOWN if diff_y > 0 else _dir_.moveUP
        if diff_y == 0:
            return _dir_.moveLEFT if diff_x < 0 else _dir_.moveRIGHT
        self.game_controller.random_path(self)
        return _dir_.NOmove

    def auto_mv(self, in_direction: _dir_):
        if in_direction == _dir_.moveUP:
            self.set_pos(self.x, self.y - 1)
        elif in_direction == _dir_.moveDOWN:
            self.set_pos(self.x, self.y + 1)
        elif in_direction == _dir_.moveLEFT:
            self.set_pos(self.x - 1, self.y)
        elif in_direction == _dir_.moveRIGHT:
            self.set_pos(self.x + 1, self.y)


class Snack(Game_Obj):
    def __init__(self, in_surface, x, y):
        super().__init__(in_surface, x, y, 4, (255, 255, 0), True)


class Pathfinder:
    def __init__(self, in_arr):
        cost = np.array(in_arr, dtype=np.bool_).tolist()
        self.pf = tcod.path.AStar(cost=cost, diagonal=0)

    def get_path(self, from_x, from_y, to_x, to_y) -> object:
        res = self.pf.get_path(from_x, from_y, to_x, to_y)
        return [(sub[1], sub[0]) for sub in res]


class pacfriend_Remote:
    def __init__(self):
        self.my_awesome_maze = [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP           XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X                          X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X      XX    XX    XX      X",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX X   G  X XX XXXXXX",
            "          X G    X          ",
            "XXXXXX XX X   G  X XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "X            XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X   XX       G        XX   X",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "X      XX    XX    XX      X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X                          X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.nmpy_mz = []
        self.snack_spaces = []
        self.reachable_spaces = []
        self.enemy_chars = []
        self.enemy_identifiers = [
            (181, 136, 116),
            (128, 128, 0),
            (255, 219, 8),
            (242, 133, 0)
        ]
        self.size = (0, 0)
        self.mz_to_npmy()
        self.p = Pathfinder(self.nmpy_mz)

    def random_path(self, in_enemy: Enemy):
        random_space = random.choice(self.reachable_spaces)
        current_maze_coord = scr_to_mze(in_enemy.get_pos())

        path = self.p.get_path(current_maze_coord[1], current_maze_coord[0], random_space[1],
                               random_space[0])
        test_path = [mze_to_scr(item) for item in path]
        in_enemy.set_new_path(test_path)

    def mz_to_npmy(self):
        for x, row in enumerate(self.my_awesome_maze):
            self.size = (len(row), x + 1)
            binary_row = []
            for y, column in enumerate(row):
                if column == "G":
                    self.enemy_chars.append((y, x))

                if column == "X":
                    binary_row.append(0)
                else:
                    binary_row.append(1)
                    self.snack_spaces.append((y, x))
                    self.reachable_spaces.append((y, x))
            self.nmpy_mz.append(binary_row)


if __name__ == "__bestie__":
    unified_size = 40
    pacfriend_game = pacfriend_Remote()
    size = pacfriend_game.size
    game_REN = Game_REN(
        size[0] * unified_size, size[1] * unified_size)

    for y, row in enumerate(pacfriend_game.nmpy_mz):
        for x, column in enumerate(row):
            if column == 0:
                game_REN.add_wall(The_Walls(game_REN, x, y, unified_size))

    for snack_space in pacfriend_game.snack_spaces:
        translated = mze_to_scr(snack_space)
        snack = Snack(
            game_REN, translated[0] + unified_size / 2, translated[1] + unified_size / 2)
        game_REN.add_snack(snack)

    for i, enemy_spawn in enumerate(pacfriend_game.enemy_chars):
        translated = mze_to_scr(enemy_spawn)
        enemy = Enemy(game_REN, translated[0], translated[1], unified_size, pacfriend_game,
                      pacfriend_game.enemy_identifiers[i % 4])
        game_REN.add_pacfriend_obj(enemy)

    pacfriend = Bestie(game_REN, unified_size, unified_size, unified_size)
    game_REN.add_bestie(pacfriend)
    game_REN.mark(120)
