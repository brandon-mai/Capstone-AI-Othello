import pygame
import random
from grid import Grid
from computer import ComputerPlayer
from heuristics import *

# Othello: main game object, responsible for assigning turns and updating board


class Othello:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello')

        self.human_player = 1  # edit to match player1 - human or AI
        self.player_AI_max = 0  # edit to match player1 - human or AI
        self.player_AI_min = -1

        self.player1 = 1  # do not edit, black player, maximizing player
        self.player2 = -1  # do not edit, white player, minimizing player

        self.firstPlayer = self.player1  # edit this line to select who plays first, player1 or player2
        self.currentPlayer = self.firstPlayer

        self.time = 0

        self.rows = 8
        self.columns = 8

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
        if self.currentPlayer == self.player_AI_min:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.player2:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 5, -64, 64, self.player2)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player2)

                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        if self.currentPlayer == self.player_AI_max:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.gameOver = True
                        return
                    self.currentPlayer *= -1
                if self.currentPlayer == self.player1:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 5, -64, 64, self.player1)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player1)

                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

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
        pygame.display.update()