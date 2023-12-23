import pygame
import copy
import time
import importlib
from grid import Grid
from computer import ComputerPlayer
from heuristics import *

# Othello: main game object, responsible for assigning turns and updating board


class Othello:
    def __init__(self, mode: int = 0, is_recording: bool = False, game_file: str = None):
        """
        :param mode: 0: replay | 1: human vs. AI | 2: AI vs. AI | 3: AI vs. engine
        :param is_recording: whether the current game is being recorded
        :param game_file: relative path to game record (for mode = 0 only)
        """
        pygame.init()
        self.mode = mode
        self.is_recording = is_recording
        self.game_file = game_file

        # ADVANCED SETTINGS #
        base_height = 600  # window height, MUST be multiple of 10
        self.random_sprite = False  # turn on if you want some fun
        #####################

        # GAME REPLAYING #
        if self.mode == 0:
            pkg, f = self.game_file.split('/')
            mod = importlib.import_module(f'.{f[:-3:]}', package=pkg)
            self.data = mod.data
            self.is_recording = False
        ##################

        # GAME RECORDING #
        if self.mode and self.is_recording:
            t = time.localtime()
            self.file_name = (f'game_records/Game_{t.tm_mday:0>2d}{t.tm_mon:0>2d}{str(t.tm_year % 100).zfill(2)}'
                              f'_{t.tm_hour:0>2d}{t.tm_min:0>2d}{t.tm_sec:0>2d}.py')
            self.recorded = False
        ##################

        # UI SCALING #
        self.tile_size = base_height // 10
        self.screen = pygame.display.set_mode((base_height * (4/3), base_height))
        caption = (f'Othello'
                   f'{f' - Replaying /{self.game_file}' if self.mode == 0 else ' - Human vs. AI' if self.mode == 1 else ''}'
                   f'{' - AI vs. AI' if self.mode == 2 else ' - AI vs. Human' if self.mode == 3 else ''}'
                   f'{f' - Recording to /{self.file_name}' if self.is_recording else ''}'
                   f'{' - I\'m feeling lucky' if self.random_sprite else ''}')
        pygame.display.set_caption(caption)
        ##############

        # GAME RULE #
        if self.mode == 1 or self.mode == -1:
            self.human_player, self.AI_black, self.AI_white = (1, 0, -1)
        elif self.mode == 2:
            self.human_player, self.AI_black, self.AI_white = (0, 1, -1)
        elif self.mode == 3 or self.mode == -3:
            self.human_player, self.AI_black, self.AI_white = (-1, 0, 1)
        elif self.mode == 0:
            if self.data['game_mode'] == 1:
                self.human_player, self.AI_black, self.AI_white = (1, 0, 0)
            elif self.data['game_mode'] == 2:
                self.human_player, self.AI_black, self.AI_white = (0, 0, 0)
            elif self.data['game_mode'] == 3:
                self.human_player, self.AI_black, self.AI_white = (-1, 0, 0)
        self.player1 = 1  # black player
        self.player2 = -1  # white player
        self.currentPlayer = self.player1  # black always goes first
        #############

        # METRICS/CONDITIONS #
        self.time = 0
        self.turn_count = 0 if self.mode == 0 else 1
        self.gameOver = True
        self.forfeited_turns = 0
        ######################

        # ROLLBACK #
        self.recent_move = None
        self.states = list()
        ##################

        # GAME OBJECTS INITIALIZATION #
        self.grid = Grid(8, 8, (self.tile_size, self.tile_size), self)
        self.computerPlayer = ComputerPlayer(self.grid)
        ###############################

        self.RUN = True

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        tile = self.tile_size
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            # General event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()
                if event.button == 1:
                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 4 and x <= tile * 6 and y >= tile * 5 and y <= tile * 6:
                            self.grid.newGame(self.random_sprite)
                            self.gameOver = False
                            self.currentPlayer = self.player1
                            self.recent_move = None
                            self.states = list()
                            self.turn_count = 0 if self.mode == 0 else 1

            # Human player move/rollback
            if event.type == pygame.MOUSEBUTTONDOWN and self.mode != 0:
                if event.button == 1:
                    if self.currentPlayer == self.human_player and not self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - tile) // tile, (y - tile) // tile
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if not validCells:
                            pass
                        else:
                            if (y, x) in validCells:
                                self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                                self.recent_move = (y, x, self.currentPlayer)
                                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)
                                swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                                for tile in swappableTiles:
                                    self.grid.animateTransitions(tile, self.currentPlayer)
                                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                self.turn_count += 1
                                self.currentPlayer *= -1
                                self.forfeited_turns = 0
                                self.time = pygame.time.get_ticks()
                    if self.currentPlayer == self.human_player and not self.gameOver and self.turn_count >= 3:
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 10.8 and x <= tile * 12.4 and y >= tile * 8 and y <= tile * 9:
                            self.states.pop()
                            prev_board, prev_recent_move = self.states.pop()
                            self.grid.recoverGrid(prev_board)
                            self.recent_move = prev_recent_move
                            self.turn_count -= 2
                            return

            # Replay control
            if self.mode == 0:
                # Replay roll backward/forward
                if event.type == pygame.KEYDOWN and not self.gameOver:
                    if event.key == pygame.K_LEFT:
                        if self.turn_count > 0:
                            self.turn_count -= 1
                        elif self.turn_count == 0:
                            self.turn_count = self.data['turn_count']
                        self.grid.recoverGrid(self.data[f'board{self.turn_count}'])
                        self.recent_move = self.data[f'recent_move{self.turn_count}']
                        if self.recent_move is None:
                            self.currentPlayer = self.player1
                        else:
                            self.currentPlayer = self.data[f'recent_move{self.turn_count}'][2]
                    if event.key == pygame.K_RIGHT:
                        if self.turn_count < self.data['turn_count']:
                            self.turn_count += 1
                        elif self.turn_count == self.data['turn_count']:
                            self.turn_count = 0
                        self.grid.recoverGrid(self.data[f'board{self.turn_count}'])
                        self.recent_move = self.data[f'recent_move{self.turn_count}']
                        if self.recent_move is None:
                            self.currentPlayer = self.player1
                        else:
                            self.currentPlayer = self.data[f'recent_move{self.turn_count}'][2]
                # Branch into new game record
                if event.type == pygame.MOUSEBUTTONDOWN and not self.gameOver:
                    if event.button == 1\
                            and ((self.data['game_mode'] == 1 and self.turn_count % 2 == 0)
                                 or (self.data['game_mode'] == 3 and self.turn_count % 2 != 0)):
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 10.8 and x <= tile * 12.4 and y >= tile * 8 and y <= tile * 9:
                            print('let\'s go baby that\'s what i was looking for')

    def update(self):
        # AI_white's turn
        if self.currentPlayer == self.AI_white and not self.gameOver:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.AI_white:

                    cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 3, -100, 100, self.AI_white)
                    # cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player_AI_min)

                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.recent_move = (cell[0], cell[1], self.currentPlayer)
                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.turn_count += 1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        # AI_black's turn
        if self.currentPlayer == self.AI_black and not self.gameOver:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.AI_black:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 3, -100, 100, self.player_AI_max)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.AI_black)

                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.recent_move = (cell[0], cell[1], self.currentPlayer)
                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.turn_count += 1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

        # human_player's turn
        if self.currentPlayer == self.human_player and not self.gameOver:
            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                self.forfeited_turns += 1
                if self.forfeited_turns == 2:
                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.gameOver = True
                    return
                self.currentPlayer *= -1

        if self.mode and self.is_recording:
            if self.gameOver and self.turn_count > 1 and not self.recorded:
                f = open(self.file_name, 'w')
                f.write('data = {\n')
                f.write(f'\t"game_mode": {self.mode},\n')
                f.write(f'\t"turn_count": {self.turn_count - 1},\n')
                for turn in range(self.turn_count):
                    board, recent_move = self.states[turn]
                    next_recent_move = self.states[turn + 1][1] if turn < self.turn_count - 1 else (0, 0, None)
                    f.write(f'\t"board{turn}": {str(board)},\n')
                    if recent_move is None:
                        f.write(f'\t"recent_move{turn}": {str(recent_move)},\n')
                        continue
                    f.write(f'\t"recent_move{turn}": ({recent_move[0]}, {recent_move[1]}, {next_recent_move[2]}),\n')
                f.write('}')
                self.recorded = True
                f.close()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        self.grid.markRecentMove(self.screen)
        self.grid.markNextMove(self.screen)
        self.grid.drawTurns(self.screen)
        self.grid.drawRollbackButton(self.screen)
        self.grid.drawBranchButton(self.screen)
        pygame.display.update()
