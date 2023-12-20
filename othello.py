import pygame
import random
from grid import Grid
from computer import ComputerPlayer
from heuristics import *

# Othello: main game object, responsible for assigning turns and updating board


class Othello:
    '''
    Othello game.\n
    mode 1: human vs. AI\n
    mode 2: AI vs. AI\n
    mode 3: AI vs. engine (human plays engine's moves)
    '''
    def __init__(self, mode: int):
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello')

        self.human_player = 1 if mode == 1 else 0 if mode == 2 else -1
        self.player_AI_max = 0 if mode == 1 or mode == 3 else 1
        self.player_AI_min = -1 if mode == 1 or mode == 2 else 1

        self.player1 = 1  # do not edit, black player
        self.player2 = -1  # do not edit, white player

        self.firstPlayer = self.player1
        self.currentPlayer = self.firstPlayer

        self.time = 0

        self.rows = 8
        self.columns = 8

        self.recent_move = None
        self.gameOver = True
        self.forfeited_turns = 0

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.computerPlayer = ComputerPlayer(self.grid)

        self.RUN = True

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()

                if event.button == 1:
                    if self.currentPlayer == self.human_player and not self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - 80) // 80, (y - 80) // 80
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if not validCells:
                            pass
                        else:
                            if (y, x) in validCells:
                                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)
                                self.recent_move = (y, x)
                                swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                                for tile in swappableTiles:
                                    self.grid.animateTransitions(tile, self.currentPlayer)
                                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                self.currentPlayer *= -1
                                self.forfeited_turns = 0
                                self.time = pygame.time.get_ticks()

                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        if x >= 320 and x <= 480 and y >= 400 and y <= 480:
                            self.grid.newGame()
                            self.gameOver = False
                            self.currentPlayer = self.firstPlayer

    def update(self):
        # player_AI_min's turn
        if self.currentPlayer == self.player_AI_min:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.player_AI_min:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 5, -64, 64, self.player_AI_min)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player_AI_min)

                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    self.recent_move = cell
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        # player_AI_max's turn
        if self.currentPlayer == self.player_AI_max:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.player_AI_max:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 5, -64, 64, self.player_AI_max)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player_AI_max)

                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    self.recent_move = cell
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

        # human_player's turn
        if self.currentPlayer == self.human_player:
            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                self.forfeited_turns += 1
                if self.forfeited_turns == 2:
                    self.gameOver = True
                    return
                self.currentPlayer *= -1


    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        self.grid.markRecentMove(self.screen, self.recent_move)
        pygame.display.update()