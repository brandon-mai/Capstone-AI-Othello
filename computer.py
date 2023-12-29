import copy
import random

# Computer player, implemented with searching algorithms and heuristics
# EDIT USED HEURISTICS / EVALUATING FUNCTIONS IN evaluating_functions.py ONLY


class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject
        self.evaluated = dict()
        self.eval_counter = 0

    def hash_board(self, grid):
        black_str = ''.join(['1' if tile == 1 else '0' for row in grid for tile in row])
        white_str = ''.join(['1' if tile == -1 else '0' for row in grid for tile in row])
        black_str = int(black_str, 2)
        white_str = int(white_str, 2)
        return int(str(black_str) + str(white_str))

    def move_ordering_static(self, grid, heuristics, player):
        moves = self.grid.findAvailMoves(grid, player)
        static_weight = [
            [120, -20, 40, 5, 5, 40, -20, 120],
            [-20, -80, -5, -5, -5, -5, -80, -20],
            [40, -5, 25, 3, 3, 25, -5, 40],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [40, -5, 25, 3, 3, 25, -5, 40],
            [-20, -80, -5, -5, -5, -5, -80, -20],
            [120, -20, 40, 5, 5, 40, -20, 120],
        ]
        moves_sorted = sorted(moves, key=lambda move: static_weight[move[0]][move[1]], reverse=True)
        return moves_sorted[::player]  # Decreasing if player = 1, increasing if player = -1

    def move_ordering_shallow(self, grid, heuristics, player):
        newGrid = copy.deepcopy(grid)
        avail_moves = self.grid.findAvailMoves(newGrid, player)
        scores = list()

        for move in avail_moves:
            x, y = move
            swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
            newGrid[x][y] = player
            for tile in swappableTiles:
                newGrid[tile[0]][tile[1]] = player

            bMove, value = self.MINIMAX_ABP(newGrid, heuristics, 0, float('-inf'), float('inf'), player * -1, 0)

            scores.append(value)
            newGrid = copy.deepcopy(grid)

        moves_sorted = sorted(avail_moves, key=lambda move: scores[avail_moves.index(move)], reverse=True)
        return moves_sorted[::player]

    def RANDOM(self, grid, player):
        availMoves = self.grid.findAvailMoves(self.grid.gridLogic, player)
        return random.choice(availMoves), 0

    # Basic MINIMAX with Alpha-Beta Pruning for reference
    def MINIMAX_ABP(self, grid, heuristics, depth, alpha, beta, player, turn_count):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, heuristics(grid, turn_count)
            self.eval_counter += 1
            return bestMove, Score

        if player > 0:
            bestScore = float('-inf')
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.MINIMAX_ABP(newGrid, heuristics, depth - 1, alpha, beta, player * -1, turn_count + 1)

                self.eval_counter += 1
                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = float('inf')
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.MINIMAX_ABP(newGrid, heuristics, depth - 1, alpha, beta, player * -1, turn_count + 1)

                self.eval_counter += 1
                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

    def NEGAMAX(self, grid, heuristics, depth, alpha, beta, player, turn_count):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        # if self.hash_board(grid) in self.evaluated.keys():
        #     best_move, score = self.evaluated[self.hash_board(grid)]
        #     self.evaluated.pop(self.hash_board(grid))
        #     return best_move, score

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, heuristics(grid, turn_count)
            self.eval_counter += 1
            return bestMove, Score * player

        bestScore = float('-inf')
        bestMove = availMoves[0]

        for move in availMoves:
            x, y = move
            swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
            newGrid[x][y] = player
            for tile in swappableTiles:
                newGrid[tile[0]][tile[1]] = player

            bMove, value = self.NEGAMAX(newGrid, heuristics, depth - 1, -beta, -alpha, player * -1, turn_count + 1)
            value *= -1

            self.eval_counter += 1
            if value > bestScore:
                bestScore = value
                bestMove = move
            alpha = max(alpha, bestScore)
            if beta <= alpha:
                break

            newGrid = copy.deepcopy(grid)
        # self.evaluated[self.hash_board(grid)] = (bestMove, bestScore)
        return bestMove, bestScore

    def MINIMAX_ABP_EXPERIMENTAL(self, grid, heuristics, depth, alpha, beta, player, turn_count, screening=False, ply=3):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if (self.hash_board(grid), player) in self.evaluated.keys():
            best_move, score = self.evaluated[(self.hash_board(grid), player)]
            self.evaluated.pop((self.hash_board(grid), player))
            return best_move, score

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, heuristics(grid, turn_count)
            self.eval_counter += 1
            return bestMove, Score

        if screening is False:
            availMoves = self.move_ordering_shallow(grid, heuristics, player)
            screening = True
            ply = depth - 2

        if player > 0:
            bestScore = float('-inf')
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.MINIMAX_ABP_EXPERIMENTAL(newGrid, heuristics, depth - 1, alpha, beta, player * -1,
                                                             turn_count + 1, screening, ply - 1)

                self.eval_counter += 1
                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            if ply > 0:
                self.evaluated[(self.hash_board(grid), player)] = (bestMove, bestScore)
            return bestMove, bestScore

        if player < 0:
            bestScore = float('inf')
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.MINIMAX_ABP_EXPERIMENTAL(newGrid, heuristics, depth - 1, alpha, beta, player * -1,
                                                      turn_count + 1, screening, ply - 1)

                self.eval_counter += 1
                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            if ply > 0:
                self.evaluated[(self.hash_board(grid), player)] = (bestMove, bestScore)
            return bestMove, bestScore
