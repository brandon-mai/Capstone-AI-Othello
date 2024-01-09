import utility_functions as util
import json
with open("preprocess/table.json", "r") as file:
    TABLE = json.load(file)

# Heuristics
# Functions MUST have 2 parameters: grid_object and turn_count
# if you want to protect a function from being selectable, add '_' before the name
# for example: _corner, _xSquare won't be selectable

def parity(grid, turn_count):
    # Direction 1: maximizing B/W disks ratio
    B = 0
    W = 0
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            if col == 1:
                B += 1
            elif col == -1:
                W += 1
    disk_ratio = 100 * (B / (B + W)) if B > W else -100 * (W / (B + W)) if B < W else 0

    # Direction 2: maximizing disks number advantage
    disk_count = sum([sum(row) for row in grid])

    return disk_count


def mobility(grid, turn_count):
    # actual/potential mobility: For simplicity I would use the most simple form
    moves = {1: [], -1: []}
    moves[1], swappable_white = util.find_avail_moves_global(grid, 1)
    moves[-1], swappable_black = util.find_avail_moves_global(grid, -1)

    # coefficients:
    corner = 3
    X = -4
    C = -3
    edge = 0.5

    # potential mobility: I would calculate the number of frontier/outside discs
    frontier = {1: [], -1: []}
    for gridX, row in enumerate(grid):
        for gridY, col in enumerate(row):
            if grid[gridX][gridY] != 0:
                player = grid[gridX][gridY]
                valid_directions = []
                if gridX != 0: valid_directions.append((gridX - 1, gridY))
                if gridX != 7: valid_directions.append((gridX + 1, gridY))
                if gridY != 0: valid_directions.append((gridX, gridY - 1))
                if gridY != 7: valid_directions.append((gridX, gridY + 1))

                for direction in valid_directions:
                    if (grid[direction[0]][direction[1]] == 0 and (direction[0], direction[1]) not in frontier[player]
                            and ((direction[0], direction[1]) not in moves[player * -1])):
                        frontier[player].append((direction[0], direction[1]))
                        break

    # parameters of the corner/X + C squares/remaining edge squares
    corner_square = [(0, 0), (0, 7), (7, 7), (7, 0)]
    C_square = [(0, 1), (1, 0), (0, 6), (7, 1), (6, 0), (7, 1), (7, 6), (6, 7)]
    X_square = [(1, 1), (6, 6), (6, 1), (6, 6)]
    edge_square = [(0, 2), (0, 3), (0, 4), (0, 5), (7, 4), (7, 5), (7, 2), (7, 3), (2, 0), (3, 0), (4, 0), (5, 0),
                   (2, 7), (3, 7), (4, 7), (5, 7)]

    # calculate the total mobility
    black_mobility = 2 / 5 * len(moves[1]) + 3 / 5 * len(frontier[-1])
    white_mobility = 2 / 5 * len(moves[-1]) + 3 / 5 * len(frontier[1])

    # take into account the quality of the move
    for square in corner_square:
        if grid[square[0]][square[1]] == 1:
            black_mobility += corner
        if grid[square[0]][square[1]] == -1:
            white_mobility += corner

    for square in X_square:
        if grid[square[0]][square[1]] == 1:
            black_mobility += X
        if grid[square[0]][square[1]] == -1:
            white_mobility += X

    return black_mobility - white_mobility


def stability1(grid, turn_count):
    # unstable: each disc = -1
    black_move, white_unstable = util.find_avail_moves_global(grid, 1)
    white_move, black_unstable = util.find_avail_moves_global(grid, -1)

    # semi-stable: each disc = 0
    weight1 = (1 - grid[0][1] ** 2) * (1 - grid[0][6] ** 2) * grid[0][2] * grid[0][5] * grid[0][2] * grid[0][1] * \
              grid[0][7]
    weight2 = (1 - grid[7][1] ** 2) * (1 - grid[7][6] ** 2) * grid[7][2] * grid[7][5] * grid[7][2] * grid[7][1] * \
              grid[7][6]
    weight3 = (1 - grid[1][0] ** 2) * (1 - grid[6][0] ** 2) * grid[5][0] * grid[2][0] * grid[2][0] * grid[1][0] * \
              grid[6][0]
    weight4 = (1 - grid[1][7] ** 2) * (1 - grid[6][7] ** 2) * grid[2][7] * grid[5][7] * grid[2][7] * grid[1][7] * \
              grid[6][7]
    # stable: each disc = 1

    black_stable = util.stable_disc(grid, 1)
    white_stable = util.stable_disc(grid, -1)
    return 100 * (weight1 + weight2 + weight3 + weight4) + len(black_move) - len(white_move) - len(
        white_unstable) + len(black_unstable)


def stability3(grid, count):
    # unstable
    blackMoves, unstableWhiteTiles = util.find_avail_moves_global(grid, 1)
    whiteMoves, unstableBlackTiles = util.find_avail_moves_global(grid, -1)

    # stable
    whiteStable = util.stable_disc(grid, -1)
    blackStable = util.stable_disc(grid, 1)

    res = 0.4*(len(blackMoves) - len(whiteMoves)) + 0.6 * (len(unstableWhiteTiles) - len(unstableBlackTiles))

    # eval edge pos

    return res


def stability2(grid, count):
    edges = util.extractEdge(grid)
    res = 0
    for edge in edges:
        if str(edge) in TABLE:
            res += 100*TABLE[str(edge)]

    return res

def stability(grid, count):
    numW = 0
    numB = 0
    A_square = [[0, 2], [0, 5], [2, 0], [2, 7], [5, 0], [5, 7], [7, 2], [7, 5]]
    B_square = [[3, 0], [4, 0], [0, 3], [0, 4], [3, 7], [4, 7], [7, 3], [7, 4]]
    C_square = [[0, 1], [0, 6], [1, 0], [1, 7], [6, 0], [6, 7], [7, 1], [7, 6]]
    X_square = [[1, 1], [1, 6], [6, 1], [6, 6]]
    corrner = [[0, 0], [0, 7], [7, 0], [7, 7]]
    # unstable
    whiteMoves, unstableBlackTiles = util.find_avail_moves_global(grid, -1)
    blackMoves, unstableWhiteTiles = util.find_avail_moves_global(grid, 1)
    if len(unstableWhiteTiles) != 0:
        for i in range(len(unstableWhiteTiles[0])):
            if list(unstableWhiteTiles[0][i]) in A_square:
                numW += 20
            if list(unstableWhiteTiles[0][i]) in B_square:
                numW += 15
            if list(unstableWhiteTiles[0][i]) in C_square:
                numW -= 50
            if list(unstableWhiteTiles[0][i]) in X_square:
                numW -= 75
    if len(unstableBlackTiles) != 0:
        for i in range(len(unstableBlackTiles[0])):
            if list(unstableBlackTiles[0][i]) in A_square:
                numB += 20
            if list(unstableBlackTiles[0][i]) in B_square:
                numB += 15
            if list(unstableBlackTiles[0][i]) in C_square:
                numB -= 50
            if list(unstableBlackTiles[0][i]) in X_square:
                numB -= 75

                # stable
    whiteStable = util.stable_disc(grid, -1)
    blackStable = util.stable_disc(grid, 1)

    if len(whiteStable) != 0:
        for i in range(len(whiteStable)):
            if whiteStable[i] in A_square:
                numW += 1000
            if whiteStable[i] in B_square:
                numW += 1000
            if whiteStable[i] in C_square:
                numW += 1200
            if whiteStable[i] in X_square:
                numW += 1500
            if whiteStable[i] in corrner:
                numW += 8000
            else:
                numW += 10
    if len(blackStable) != 0:
        for i in range(len(blackStable)):
            if blackStable[i] in A_square:
                numB += 1000
            if blackStable[i] in B_square:
                numB += 1000
            if blackStable[i] in C_square:
                numB += 1200
            if blackStable[i] in corrner:
                numB += 8000
            if blackStable[i] in X_square:
                numB += 1500
            else:
                numB += 10

    # semi-stable
    semistablewhite = []
    if len(unstableWhiteTiles) != 0:
        for i in range(len(unstableWhiteTiles[0])):
            if list(unstableWhiteTiles[0][i]) not in whiteStable:
                semistablewhite.append(unstableWhiteTiles[0][i])
    if len(semistablewhite) != 0:
        for i in range(len(semistablewhite)):
            if list(semistablewhite[i]) in A_square:
                numW += 100
            if list(semistablewhite[i]) in B_square:
                numW += 100
            if list(semistablewhite[i]) in C_square:
                numW -= 125
            if list(semistablewhite[i]) in X_square:
                numW -= 200
            else:
                numW += 5
    semistableblack = []
    if len(unstableBlackTiles) != 0:
        for i in range(len(unstableBlackTiles[0])):
            if list(unstableBlackTiles[0][i]) not in blackStable:
                semistableblack.append(unstableBlackTiles[0][i])
    if len(semistableblack) != 0:
        for i in range(len(semistableblack)):
            if list(semistableblack[i]) in A_square:
                numB += 100
            if list(semistableblack[i]) in B_square:
                numB += 100
            if list(semistableblack[i]) in C_square:
                numB -= 125
            if list(semistableblack[i]) in X_square:
                numB -= 200
            else:
                numB += 5
    # return len(whiteStable) - len(blackStable)
    return (numB - numW) // 100
