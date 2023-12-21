import copy
import random

# Computer player, implemented with searching algorithms and heuristics
# EDIT USED HEURISTICS IN othello.py


class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject

    def computerRandom(self, grid, player):
        availMoves = self.grid.findAvailMoves(self.grid.gridLogic, player)
        return random.choice(availMoves), 0

    def computerHard(self, grid, heuristics, depth, alpha, beta, player):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        #if depth == 0:
        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, heuristics(grid, player)
            return bestMove, Score

        #if len(availMoves) == 0:
        #    bestMove, Score = None, evaluateBoard()
        #    return bestMove, Score

        if player > 0:
            bestScore = alpha
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerHard(newGrid, heuristics, depth-1, alpha, beta, player *-1)

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = beta
            bestMove = None

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerHard(newGrid, heuristics, depth-1, alpha, beta, player)

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
