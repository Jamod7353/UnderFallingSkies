import random
import pygame
import copy


class Place:
    def __init__(self, type, bonus, cost, pos):
        self.type = type
        self.bonus = bonus
        self.cost = cost
        self.positions = pos
        self.free_positions = copy.deepcopy(self.positions)
        self.free_slots = len(self.free_positions)

    def reset(self):
        self.free_slots = len(self.positions)
        self.free_positions = copy.deepcopy(self.positions)

    def set_die(self, pos):
        if pos in self.free_positions:
            self.free_positions.remove(pos)
            self.free_slots -= 1
            return True
        return False

    def used(self, pos):
        return pos in self.positions and self.free_slots == 0


class Die:
    def __init__(self, color, iD):
        self.color = color
        self.value = 0
        self.roll()
        self.iD = iD
        self.used = self.iD >= 5  # let blue dice be used (not settable)
        self.position = [0, 0]

    def roll(self):
        self.value = random.randint(1, 6)

    def place(self, pos):
        self.used = True
        self.position = pos

    def reset(self):
        self.used = self.iD >= 5  # let blue dice be used (not settable)
        self.position = [0, 0]
        self.roll()

    def remove(self):
        self.position = [0, 0]

    def get_id(self):
        return self.iD

    def get_value(self):
        return self.value


class Game:
    energy = 2
    turn_science = 0
    turn_shot = 0
    turn_drill = 0
    # science line
    science_lv = [[], []]
    science_lv[0] = [0, 3, 1, 4, 2, 3, 2, 6, 2, 1, 4, 7, 4, 2, 12]
    science_lv[1] = []
    # mothership items and line
    DRILL1 = 30
    DRILL2 = 31
    ALIEN1 = 32
    ALIEN2 = 33
    SHIP = 34
    SHOT = 35
    DEATH = 36
    # cards
    # EXPLODE - level as Integer between 1 and 6
    LEFT = 10
    RIGHT = 11
    MOVE_MOTHERSHIP = 12
    END = 99
    # card [MS, [card1lv1, card1lv2] ,...]
    card = [[], [[], []], [[], []], [[], []], [[], []]]
    card[1][0] = [[0, DRILL1, SHIP, ALIEN1], [0, 0, 0, 2], [0, 0, 1, RIGHT],
                  [0, 0, RIGHT, 0], [0, LEFT, 0, 0], [0, 0, 0, MOVE_MOTHERSHIP]]
    card[1][1] = []
    card[2][0] = [[DRILL1, DRILL2, ALIEN2, SHIP], [0, 0, 3, RIGHT], [0, LEFT, MOVE_MOTHERSHIP, 0],
                  [LEFT, MOVE_MOTHERSHIP, RIGHT, 3], [RIGHT, 2, 0, 0], [0, 0, 4, LEFT]]
    card[2][1] = []
    card[3][0] = [[DRILL1, SHOT, 0, DEATH], [MOVE_MOTHERSHIP, RIGHT, 0, 0], [6, 0, RIGHT, LEFT],
                  [0, 3, 0, MOVE_MOTHERSHIP], [LEFT, MOVE_MOTHERSHIP, 5, 0], [0, 2, 0, LEFT]]
    card[3][1] = []
    card[4][0] = [[0, 0, 0, 0], [5, 0, 0, END], [0, 3, 0, END],
                  [LEFT, 5, 0, END], [4, RIGHT, MOVE_MOTHERSHIP, END], [MOVE_MOTHERSHIP, 0, 6, END]]
    card[4][1] = []
    # TODO add lvl2 cards
    # bunker cards
    MIN1 = 20
    ENERGY = 21
    ROBOT = 22
    SHOT = 23
    SCIENCE = 24
    DRILL_START = 25
    EMPTY = 26
    ENERGYSHOT = 27
    ENERGYROBOT = 28
    bunker_card0 = [[Place(MIN1, 0, 0, [[5, 0]]), Place(MIN1, 0, 0, [[4, 0]]), Place(MIN1, 0, 0, [[3, 0]]),
                     Place(MIN1, 0, 0, [[2, 0]]), Place(MIN1, 0, 0, [[1, 0]]), Place(ENERGY, -1, 0, [[1, 1]]),
                     Place(ROBOT, -1, 1, [[2, 1]]), Place(SHOT, -1, 1, [[3, 1]]), Place(EMPTY, 0, 0, [[4, 1]]),
                     Place(SCIENCE, -1, 1, [[5, 1]]), Place(DRILL_START, 0, 1, [[5, 2]]), Place(SHOT, 0, 2, [[4, 2]]),
                     Place(ENERGY, 0, 0, [[3, 2], [2, 2]]), Place(SCIENCE, 0, 1, [[1, 2]])],
                    []]
    bunker_card1 = [[Place(ROBOT, 0, 2, [[1, 3]]), Place(SHOT, 1, 2, [[2, 3]]), Place(SCIENCE, 0, 1, [[3, 3], [4, 3]]),
                     Place(ENERGY, 0, 0, [[5, 3]]), Place(SHOT, 0, 1, [[5, 4]]), Place(ROBOT, 0, 1, [[4, 4]]),
                     Place(EMPTY, 0, 0, [[3, 4]]), Place(ENERGYSHOT, -3, 0, [[2, 4], [1, 4]]),
                     Place(EMPTY, 0, 0, [[1, 5]]),
                     Place(SCIENCE, 0, 1, [[2, 5], [3, 5], [4, 5]]), Place(EMPTY, 0, 0, [[5, 5]])],
                    []]

    # set level
    # level[mothership, row1, row2, row3, row4, row5, science, bunker0, bunker1]
    level = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self):
        self.phase = [1, 0, 0, None]  # [dice_phase, set_robot, die_active, chosen_die]
        self.dice = [Die('black', 0), Die('black', 1), Die('black', 2), Die('white', 3), Die('white', 4),
                     Die('blue', 5), Die('blue', 6)]
        self.free_rows = [1, 2, 3, 4, 5]
        self.robot_value = 0
        self.robot_resolved = [True, True]
        self.science = self.science_lv[self.level[6]]

        self.attack_counter = 0
        self.attack_death = 0
        if self.level[7] == 0:
            self.attack_death += 2
        else:
            self.attack_death += 3
        if self.level[8] == 0:
            self.attack_death += 3
        else:
            self.attack_death += 2

        self.board = [[0], [0], [0], [0], [0], [0], [0], [0], [0]]
        # build board (mothership-row is row 0)
        for c in range(1, 5):  # for each card extend the rows to build the map
            for row in range(6):
                self.board[row].extend(self.card[c][self.level[c]][row])
        self.science_pointer = 0
        self.bunker = self.bunker_card0[self.level[7]] + self.bunker_card1[self.level[8]]
        self.drill_pointer = 0
        self.drilled = False
        while self.bunker[self.drill_pointer].type != self.DRILL_START:
            self.drill_pointer += len(self.bunker[self.drill_pointer].positions)
        self.mothership_pointer = 0
        self.ships = [[1, self.mothership_pointer], [2, self.mothership_pointer], [3, self.mothership_pointer],
                      [4, self.mothership_pointer], [5, self.mothership_pointer],
                      [-1, self.mothership_pointer], [-1, self.mothership_pointer]]

    def drill_to_bunker_pointer(self, pointer):
        pointer += 1
        for i in range(len(self.bunker)):
            pointer -= len(self.bunker[i].positions)
            if pointer <= 0:
                return i
        return len(self.bunker)

    def bunker_to_drill_pointer(self, pointer):
        p = pointer
        for i in range(pointer):
            p += len(self.bunker[i].positions) - 1
        return p

    def game_end(self):
        print("Spielende")
        # TODO Spielende-Methode

    def choose_slot(self):
        pass

    def move_ship(self, row, steps):
        for s in self.ships:
            if s[0] == row:
                s[1] += steps
                if s[1] >= 16:
                    self.remove_ship(s)
                    self.raise_attacks()
                # resolve fields
                if self.board[row][s[1]] == self.LEFT:
                    if s[0] > 1:
                        s[0] -= 1
                elif self.board[row][s[1]] == self.RIGHT:
                    if s[0] < 5:
                        s[0] += 1
                elif self.board[row][s[1]] == self.MOVE_MOTHERSHIP:
                    # auf Spielende prüfen
                    if self.board[0][self.mothership_pointer + 1] == self.DEATH:
                        self.game_end()
                        return
                    self.mothership_pointer += 1

                    # checks if a ship is above the mothership and resets it
                    for sh in self.ships:
                        if sh[0] > 0:
                            if sh[1] < self.mothership_pointer:
                                sh[1] = self.mothership_pointer

    def set_energy(self, amount):
        self.energy += amount
        if self.energy > 7:
            self.energy = 7
        elif self.energy < 0:
            self.energy = 0

    def remove_ship(self, pos):
        for i in range(len(self.ships)):
            if self.ships[i] == pos:
                if i < 5:  # normal ship
                    self.ships[i] = [0, self.mothership_pointer]
                else:  # red ship
                    self.ships[i] = [-1, self.mothership_pointer]

    def reset_ships(self):
        # lists empty cols
        freelines = []
        for i in range(1, 5):
            freelines.append(i)
        for f in self.ships:
            if f[0] in freelines:
                freelines.remove(f[0])
        for i in range(len(self.ships)):
            if self.ships[i][0] == 0:
                if freelines:
                    self.ships[i] = [freelines.pop(), self.mothership_pointer]
                else:
                    # TODO: Spalte mit höchstem Abstand
                    pass
                    # self.ships[i] = (choose_slot(), pointer)
                    # Auswahl auf ein leeres Feld

    def ready_red_ship(self):
        if self.ships[5][0] == -1:
            self.ships[5][0] = 0
        elif self.ships[6][0] == -1:
            self.ships[6][0] = 0

    def reset_turn(self):
        for d in self.dice:
            if not d.color == 'blue':
                d.reset()
        for b in self.bunker:
            b.reset()
        for d in self.dice:
            if d.color == 'blue' and not d.position[0] == 0:
                self.place_die(d.position, d)
        self.free_rows = [1, 2, 3, 4, 5]
        self.robot_resolved = [True, True]
        self.drilled = False

    def reset_for_resolve(self):
        self.turn_shot = 0
        self.turn_drill = 0
        self.turn_science = 0
        if self.dice[5].position[0] > 0:
            self.robot_resolved[0] = False
        if self.dice[6].position[0] > 0:
            self.robot_resolved[1] = False
        for d in self.dice:
            if not d.color == 'blue':
                d.used = False

    def get_level(self):
        return self.level

    def get_ships(self):
        return self.ships

    def get_mspointer(self):
        return self.mothership_pointer

    def pos_get_bunker(self, pos):
        for b in self.bunker:
            if pos in b.free_positions:
                return b
        return None

    def place_die(self, pos, die):
        if pos[0] in self.free_rows:
            # checking available spots in the bunker
            for i in range(self.drill_to_bunker_pointer(self.drill_pointer)):
                if pos in self.bunker[i].free_positions:
                    if die.color == 'blue':  # blue can't be set on Robot
                        if self.bunker[i].type in [self.MIN1, self.SHOT, self.ENERGY,
                                                   self.SCIENCE, self.ENERGYSHOT, self.ENERGYROBOT]:
                            self._place_die_helper(pos, die, i)
                            return True

                    elif self.bunker[i].type in [self.MIN1, self.SHOT, self.ENERGY, self.ROBOT,
                                                 self.SCIENCE, self.ENERGYSHOT, self.ENERGYROBOT]:
                        self._place_die_helper(pos, die, i)
                        return True

            # checking spots for drilling
            if not self.drilled:
                for i in range(self.drill_to_bunker_pointer(self.drill_pointer),
                               self.drill_to_bunker_pointer(self.drill_pointer + die.value + 1)):
                    if die.color != 'blue':
                        if pos in self.bunker[i].free_positions:
                            self._place_die_helper(pos, die, i)
                            self.drilled = True
                            return True
        return False

    def _place_die_helper(self, pos, die, i):
        self.bunker[i].set_die(pos)
        die.place(pos)
        self.free_rows.remove(pos[0])
        if die.color != 'blue':
            if pos[1] == 0:
                self.move_ship(pos[0], die.get_value() - 1)
            else:
                self.move_ship(pos[0], die.get_value())
            if die.color == 'white':
                for d in self.dice:
                    if not d.used and d.color != 'blue':
                        d.roll()
        else:  # die.color == 'blue'
            self.dice[5].used = True
            self.dice[6].used = True

    def resolve_die(self, die):
        if (b := self.get_bunker_place(die.position)) is not None:
            if die.color == 'blue':
                if not self.robot_resolved[die.get_id() - 5]:
                    self._resolve_helper_(die, b)
                    die.value -= 1
                    if die.value <= 1:
                        die.remove()
                    self.robot_resolved[die.get_id() - 5] = True
            else:
                if b in self.bunker[self.drill_to_bunker_pointer(self.drill_pointer):]:  # die is behind drill-pointer
                    for bu in self.bunker[self.drill_to_bunker_pointer(self.drill_pointer):]:
                        for pos in bu.positions:
                            self.drill_pointer += 1
                            print(self.drill_pointer, end=', ')
                            if pos == die.position:
                                break
                    # self.drill_pointer += die.value
                    # TODO: Min aus Würfel und Würfel-Position (Abstand)
                elif b.type == self.ROBOT:
                    self.dice[5].used = False
                    self.dice[6].used = False
                    self.robot_value = die.get_value() + b.bonus
                    self.phase[1] = 1
                else:
                    self._resolve_helper_(die, b)
            # remove all other dice in the same bunker field
            for d in self.dice:
                if d.position in b.positions:
                    if d.color != 'blue':
                        d.remove()
        die.remove()

    def _resolve_helper_(self, die, b):
        if b.type == self.ENERGY:
            self.set_energy(die.get_value() + b.bonus)
        elif b.type == self.SHOT:
            self.turn_shot += die.get_value() + b.bonus
        elif b.type == self.SCIENCE:
            self.turn_science += die.get_value() + b.bonus
            self.move_science()
        elif b.type == self.ENERGYSHOT:
            self.turn_shot += die.get_value() + b.bonus
            self.set_energy(die.get_value() + b.bonus)
        elif b.type == self.ENERGYROBOT:
            pass
        elif b.type == self.MIN1 or b.type == self.EMPTY:
            pass

    def get_bunker_place(self, pos):
        for b in self.bunker:
            if b.used(pos):
                return b
        return None

    def move_science(self):
        while self.science[self.science_pointer + 1] <= self.turn_science:
            self.turn_science -= self.science[self.science_pointer + 1]
            self.science_pointer += 1
            if self.science_pointer >= len(self.science):
                self.game_end()
                return

    def all_dice_reset(self):
        for d in self.dice:
            if not d.color == 'blue':
                if not d.position[0] == 0:
                    return False
            else:
                if not d.position[0] == 0 and not self.robot_resolved[d.get_id() - 5]:
                    return False
        return True

    def resolve_mothership(self):
        if self.board[0][self.mothership_pointer + 1] == self.DEATH:
            self.game_end()
            return
        elif self.board[0][self.mothership_pointer + 1] == self.DRILL1:
            self.drill_pointer -= 1
        elif self.board[0][self.mothership_pointer + 1] == self.DRILL2:
            self.drill_pointer -= 2
        elif self.board[0][self.mothership_pointer + 1] == self.ALIEN2:
            self.science_pointer -= 2
            if self.science_pointer < 0:
                self.science_pointer = 0
        elif self.board[0][self.mothership_pointer + 1] == self.ALIEN1:
            self.science_pointer -= 1
            if self.science_pointer < 0:
                self.science_pointer = 0
        elif self.board[0][self.mothership_pointer + 1] == self.SHIP:
            self.ready_red_ship()
        elif self.board[0][self.mothership_pointer + 1] == self.SHOT:
            self.raise_attacks()

        self.mothership_pointer += 1
        self.reset_ships()

    def raise_attacks(self):
        self.attack_counter += 1
        if self.attack_counter >= self.attack_death:
            self.game_end()


class Grafics:
    def __init__(self, game):
        self.game = game
        pygame.init()
        pygame.display.set_caption("Under Falling Skies")

        self.message = "welcome"
        info = pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        self.cell_height = self.cell_width = HEIGHT // 28
        self.card_height = self.cell_height * 4
        self.card_width = self.cell_width * 6
        self.offset = -50  # window title and linux bar at top
        self.ship_offset = self.offset + 4 * self.cell_height
        self.dice_offset = int(self.card_height * 4.451)
        self.screen = pygame.display.set_mode([2 * self.card_width, HEIGHT + self.offset])
        image_files = [["../img/mothership_0.png", "../img/card1_0.png", "../img/card2_0.png",
                        "../img/card3_0.png", "../img/card4_0.png", "../img/bunker0_0.png",
                        "../img/bunker1_0.png", "../img/science_0.png"],
                       # LV.1 image files are not existing yet... pass
                       ["../img/mothership_1.png", "../img/card1_1.png", "../img/card2_1.png",
                        "../img/card3_1.png", "../img/card4_1.png", "../img/bunker0_1.png",
                        "../img/bunker1_1.png", "../img/science_1.png"]]
        ship_files = ["../img/alien_ship.png", "../img/alien_ship_red.png"]
        science_file = "../img/science.png"
        energy_file = "../img/energy.png"
        shot_file = "../img/shot.png"
        drill_file = "../img/drill.png"
        self.science_marker = pygame.transform.scale(pygame.image.load(science_file),
                                                     (self.cell_width // 2, self.cell_height // 2))
        self.energy_marker = pygame.transform.scale(pygame.image.load(energy_file),
                                                    (self.cell_width // 2, self.cell_height // 2))
        self.shot_marker = pygame.transform.scale(pygame.image.load(shot_file),
                                                  (self.cell_width * 2 // 3, self.cell_height * 2 // 3))
        self.drill_marker = pygame.transform.scale(pygame.image.load(drill_file),
                                                   (self.cell_width * 2 // 3, self.cell_height * 2 // 3))
        dice_white_files = ["../img/die_w_1.png", "../img/die_w_2.png", "../img/die_w_3.png",
                            "../img/die_w_4.png", "../img/die_w_5.png", "../img/die_w_6.png"]
        dice_black_files = ["../img/die_black_1.png", "../img/die_black_2.png", "../img/die_black_3.png",
                            "../img/die_black_4.png", "../img/die_black_5.png", "../img/die_black_6.png"]
        dice_blue_files = ["../img/die_blue_1.png", "../img/die_blue_2.png", "../img/die_blue_3.png",
                           "../img/die_blue_4.png", "../img/die_blue_5.png", "../img/die_blue_6.png"]
        self.dice_white = []
        self.dice_blue = []
        self.dice_black = []
        for i in range(6):
            self.dice_white.append(pygame.transform.scale(pygame.image.load(dice_white_files[i]),
                                                          (self.cell_width * 2 // 3, self.cell_width * 2 // 3)))
            self.dice_blue.append(pygame.transform.scale(pygame.image.load(dice_blue_files[i]),
                                                         (self.cell_width * 2 // 3, self.cell_width * 2 // 3)))
            self.dice_black.append(pygame.transform.scale(pygame.image.load(dice_black_files[i]),
                                                          (self.cell_width * 2 // 3, self.cell_width * 2 // 3)))

        self.ship_img = pygame.image.load(ship_files[0]).convert_alpha()
        self.ship_img = pygame.transform.scale(self.ship_img, (self.cell_width * 2 // 3, self.cell_width * 2 // 3))
        self.ship_img_red = pygame.image.load(ship_files[1]).convert_alpha()
        self.ship_img_red = pygame.transform.scale(self.ship_img_red,
                                                   (self.cell_width * 2 // 3, self.cell_width * 2 // 3))

        # load board-cards depending on chosen levels
        level = game.get_level()
        self.card = []
        for i in range(8):
            self.card.append(pygame.image.load(image_files[level[i]][i]).convert())
            self.card[i] = pygame.transform.scale(self.card[i], (self.card_width, self.card_height))
        self.dice_rect = []
        for d in game.dice:
            self.dice_rect.append(pygame.Rect([-1, -1], [self.cell_width * 2 // 3, self.cell_width * 2 // 3]))
        self.attack_positions = self._set_attack_positions()

    def _set_attack_positions(self):
        pos = []
        x = int(0.017 * self.card_width)
        y_offset_lv1_0 = 5 * self.card_height + int(0.24 * self.card_height) + self.offset
        y_offset_lv2_0 = 5 * self.card_height + int(0.1 * self.card_height) + self.offset
        y_offset_lv1_1 = 6 * self.card_height + int(0.1 * self.card_height) + self.offset
        y_offset_lv2_1 = 6 * self.card_height + int(0.12 * self.card_height) + self.offset
        y_dist_lvl1_0 = int(0.28 * self.card_height)
        y_dist_lvl2_0 = int(0.31 * self.card_height)
        y_dist_lvl1_1 = int(0.28 * self.card_height)
        y_dist_lvl2_1 = int(0.32 * self.card_height)

        if self.game.level[7] == 0:
            for i in range(3):
                pos.append([x, y_offset_lv1_0 + i * y_dist_lvl1_0])
        else:
            for i in range(4):
                pos.append([x, y_offset_lv2_0 + i * y_dist_lvl2_0])

        if self.game.level[8] == 0:
            for i in range(3):
                pos.append([x, y_offset_lv1_1 + i * y_dist_lvl1_1])
        else:
            for i in range(2):
                pos.append([x, y_offset_lv2_1 + i * y_dist_lvl2_1])

        return pos

    def get_cell_width(self):
        return self.cell_width

    def print_cards(self):
        for i in range(1, 7):
            self.screen.blit(self.card[i], (0, self.card_height * i + self.offset))
        self.screen.blit(self.card[7], (self.card_width, self.card_height * 6 + self.offset))
        # print mothership on top
        self.screen.blit(self.card[0], (0, self.offset + self.game.get_mspointer() * self.cell_height))

    def print_markers(self):
        science_position = (self.card_width + int(
            0.55 * self.card_width + ((self.game.science_pointer % 5) - 2) * 0.14 * self.card_width * (-1) ** (
                    self.game.science_pointer // 5)),
                            6 * self.card_height + self.offset + int(
                                0.12 * self.card_height + self.game.science_pointer // 5 * 0.2 * self.card_height))
        energy_position = (self.card_width + int(0.157 * self.card_width + self.game.energy * 0.102 * self.card_width),
                           6 * self.card_height + self.offset + int(0.8 * self.card_height))

        self.screen.blit(self.science_marker, science_position)
        self.screen.blit(self.energy_marker, energy_position)
        self.screen.blit(self.shot_marker, self.attack_positions[self.game.attack_counter])
        drill_pos = self._drill_position()
        self.screen.blit(self.drill_marker,
                         (drill_pos[0] * self.cell_width,
                          (1 + drill_pos[1]) * int(self.cell_width * 4 / 3) + self.dice_offset))

    def _drill_position(self):
        pointer = self.game.drill_pointer
        for i in range(len(self.game.bunker)):
            pointer -= len(self.game.bunker[i].positions)
            if pointer < 0:
                return self.game.bunker[i].positions[len(self.game.bunker[i].positions) + pointer]

    def print_ships(self):
        ships = self.game.get_ships()
        mspointer = self.game.get_mspointer()
        for i in range(len(ships)):
            # ship is in a row
            if ships[i][0] > 0:
                if i < 5:
                    self.screen.blit(self.ship_img,
                                     (ships[i][0] * self.cell_width,
                                      (ships[i][1] - 1) * self.cell_height + self.ship_offset))
                else:
                    self.screen.blit(self.ship_img_red,
                                     (ships[i][0] * self.cell_width,
                                      (ships[i][1] - 1) * self.cell_height + self.ship_offset))
            # ship is in ready-area
            elif ships[i][0] == 0:
                if i < 5:
                    tmp_img = self.ship_img
                else:
                    tmp_img = self.ship_img_red
                self.screen.blit(tmp_img,
                                 ((i + 1) * self.cell_width, (mspointer - 2) * self.cell_height + self.ship_offset))
            else:
                self.screen.blit(self.ship_img_red,
                                 (self.card_width + (7 - i) * self.cell_width,
                                  (mspointer - 1) * self.cell_height + self.ship_offset))

    def print_dice(self):
        for d in self.game.dice:
            if d.color == 'black':
                tmp_img = self.dice_black[d.value - 1]
            elif d.color == 'white':
                tmp_img = self.dice_white[d.value - 1]
            else:
                tmp_img = self.dice_blue[d.value - 1]
            if self.game.phase[2] and self.game.phase[3] is d:
                self.screen.blit(tmp_img, pygame.mouse.get_pos())
            elif d.position[0] == 0:
                print_position = (d.get_id() % 5 * self.cell_width + self.card_width + int(0.5 * self.cell_width),
                                  5 * self.card_height + d.get_id() // 5 * self.cell_height + self.offset)
                self.screen.blit(tmp_img, print_position)
                self.dice_rect[d.get_id()].update(print_position, self.dice_rect[d.get_id()].size)
            else:
                print_position = (d.position[0] * self.cell_width,
                                  (1 + d.position[1]) * int(self.cell_width * 4 / 3) + self.dice_offset)
                self.screen.blit(tmp_img, print_position)
                self.dice_rect[d.get_id()].update(print_position, self.dice_rect[d.get_id()].size)

    def coordinates_to_bunkerposition(self, pos):
        x = pos[0] // self.cell_width  # !! depends on print_dice method
        y = round((pos[1] - self.dice_offset) / int(self.cell_width * 4 / 3)) - 1
        return [x, y]

    def _bunk_to_coord(self, pos):  # for testing
        return (pos[0] * self.cell_width,
                (1 + pos[1]) * int(self.cell_width * 4 / 3) + self.dice_offset)

    def move_die(self, mouse_pos):
        for i in range(len(self.dice_rect)):
            if self.dice_rect[i].collidepoint(mouse_pos):
                if not self.game.dice[i].used:
                    return self.game.dice[i]
        return None

    def draw_text(self, text):
        font = pygame.font.SysFont("arial", 25)
        y_pos = 4 * self.card_height + self.offset
        x_pos = int(self.card_width * 1.1)
        text = font.render(text, 1, (255, 255, 255))
        self.screen.blit(text, (x_pos, y_pos))

    def print(self):
        self.screen.fill((96, 96, 96))
        self.print_cards()
        self.print_ships()
        self.print_dice()
        self.print_markers()
        # self.draw_text(self.message)
        pygame.display.flip()


def main():
    # init
    game = Game()
    grafic = Grafics(game)
    grafic.print()

    # running game
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                game.phase = manage_dice(game.phase, game, grafic)
            grafic.print()

            # switch game phases (dice phase, resolve phase, moterhship phase)
            if game.phase[0]:  # phase 1 -> phase 2
                if not game.free_rows:
                    game.phase[0] = 0
                    game.reset_for_resolve()
            elif game.all_dice_reset() and not game.phase[1]:  # phase 2 -> phase 3 (-> phase 1)
                game.reset_turn()
                game.resolve_mothership()  # phase 3
                game.phase[0] = 1
            # print(game.drill_pointer, game.drill_to_bunker_pointer(game.drill_pointer))

            # tests
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game.move_ship(1, 1)
                    game.drill_pointer += 1
                    # game.science_pointer += 1
                    # game.energy += 1
                    # game.raise_attacks()
                elif event.key == pygame.K_2:
                    game.move_ship(2, 1)
                    game.energy = 0
                elif event.key == pygame.K_3:
                    game.move_ship(3, 1)
                elif event.key == pygame.K_4:
                    game.move_ship(4, 1)
                elif event.key == pygame.K_5:
                    game.move_ship(5, 1)

        grafic.print()


def manage_dice(phase, game, grafic):  # [dice_phase, set_robot, die_active, chosen_die]
    if phase[1]:  # place robot after resolving robot field in bunker
        if phase[2]:  # place robot die
            game.free_rows = [1, 2, 3, 4, 5]
            if game.place_die(grafic.coordinates_to_bunkerposition(pygame.mouse.get_pos()), phase[3]):
                phase[1] = 0
                phase[2] = 0
                game.dice[5].used = False
                game.dice[6].used = False
                return phase
        else:  # pick robot die
            grafic.message = "pick a robot (blue die)"
            if (chosen_die := grafic.move_die(pygame.mouse.get_pos())) is not None:
                if chosen_die.color == 'blue':
                    grafic.message = "place the die"
                    phase[3] = chosen_die
                    phase[3].value = game.robot_value
                    phase[2] = 1
                    return phase
    elif phase[0]:  # Phase 1: place dice - chose and set a normal die
        if phase[2]:  # place the chosen die
            if game.place_die(grafic.coordinates_to_bunkerposition(pygame.mouse.get_pos()), phase[3]):
                phase[2] = 0
                return phase
        else:  # chose a die
            if (chosen_die := grafic.move_die(pygame.mouse.get_pos())) is not None:
                grafic.message = "place your chosen die"
                phase[3] = chosen_die
                phase[2] = 1
                return phase
    else:  # Phase 2: resolve dice
        grafic.message = "click on a die to resolve it"
        if d := grafic.move_die(pygame.mouse.get_pos()):
            game.resolve_die(d)
    return phase


if __name__ == '__main__':
    main()
