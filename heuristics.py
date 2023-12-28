import utility_functions as util


# Heuristics
# Functions must have 2 parameters: grid_object and turn_count
# if you want to protect a function from being selectable, add '_' before the name
# for example: _corner, _xSquare won't be selectable

def coin_parity(grid, turn_count):
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

    # coeffcient:
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
                            and (direction[0], direction[1] not in moves[player * -1])):
                        frontier[player].append((direction[0], direction[1]))
                        break

    # parameters of the corner/X + C squares/remaining edge squares
    corner_square = [(0, 0), (0, 7), (7, 7), (7, 0)]
    C_square = [(0, 1), (1, 0), (0, 6), (7, 1), (6, 0), (7, 1), (7, 6), (6, 7)]
    X_square = [(1, 1), (6, 6), (6, 1), (6, 6)]
    edge_square = [(0, 2), (0, 3), (0, 4), (0, 5), (7, 4), (7, 5), (7, 2), (7, 3), (2, 0), (3, 0), (4, 0), (5, 0),
                   (2, 7), (3, 7), (4, 7), (5, 7)]

    # calculate the total mobility
    white_mobility = 2 / 5 * len(moves[1]) + 3 / 5 * len(frontier[-1])
    black_mobility = 2 / 5 * len(moves[-1]) + 3 / 5 * len(frontier[1])

    # take into account the quality of the move
    # if currentPlayer == 1:
    #     for move in blackMoves:
    #         if move in corner_square:
    #             black_mobility += 6 * corner
    #         if move in X_square:
    #             black_mobility += 6 * X
    #         if move in C_square:
    #             black_mobility += 6*C
    #         if move in edge_square:
    #             black_mobility += 6*edge
    #     for move in frontier[1]:
    #         if move in corner_square:
    #             black_mobility += 4 * corner
    #         if move in X_square:
    #             black_mobility += 4 * X   # not sure about this
    #         if move in C_square:
    #             black_mobility += 4 * C
    #         if move in edge_square:
    #             black_mobility += 4 * edge

    # for move in whiteMoves:
    #     if move in corner_square:
    #         white_mobility += 6 * corner
    #     if move in X_square:
    #         white_mobility += 6 * X
    #     if move in C_square:
    #         white_mobility += 6*C
    #     if move in edge_square:
    #         white_mobility += 6*edge

    # for move in frontier[-1]:
    #     if move in corner_square:
    #         white_mobility += 4 * corner
    #     if move in X_square:
    #         white_mobility += 4 * X
    #     if move in C_square:
    #         white_mobility += 4 * C
    #     if move in edge_square:
    #         white_mobility += 4 * edge

    # # Fix this ASAP, return only 1 value if possible
    # return white_mobility, black_mobility, len(frontier[1]), len(frontier[-1])

    # Temporary return value
    return black_mobility - white_mobility


def stability(grid, turn_count):
    # unstable: each disc = -1
    black_move, white_unstable = util.find_avail_moves_global(grid, 1)
    white_move, black_unstable = util.find_avail_moves_global(grid, -1)

    # semi-stable: each disc = 0

    # stable: each disc = 1
    black_stable = util.stable_disc(grid, 1)
    white_stable = util.stable_disc(grid, -1)

    return len(black_stable) - len(white_stable)


def xSquare(grid, turn_count):
    coordinates = (
        [1, 1], [6, 6],
        [6, 1], [1, 6],
    )

    black_disks = sum([1 if grid[coor[0]][coor[1]] == 1 else 0 for coor in coordinates])
    white_disks = sum([1 if grid[coor[0]][coor[1]] == -1 else 0 for coor in coordinates])

    return -5 * black_disks + 5 * white_disks


def corner(grid, turn_count):
    coordinates = (
        [0, 0], [0, 7],
        [7, 0], [7, 7],
    )

    black_disks = sum([1 if grid[coor[0]][coor[1]] == 1 else 0 for coor in coordinates])
    white_disks = sum([1 if grid[coor[0]][coor[1]] == -1 else 0 for coor in coordinates])

    return 10 * black_disks - 10 * white_disks


def corner_occupancy(grid, turn_count):
    corner = [[0, 0], [0, 7], [7, 0], [7, 7]]
    white_corner = sum([1 if grid[cor[0]][cor[1]] == 1 else 0 for cor in corner])
    black_corner = sum([1 if grid[cor[0]][cor[1]] == -1 else 0 for cor in corner])
    return 25 * white_corner - 25 * black_corner


# need to build dynamic weight
def static_weight_beginning(grid, turn_count):
    weight = [
        [120, -20, 40, 5, 5, 40, -20, 120],
        [-20, -80, -5, -5, -5, -5, -80, -20],
        [40, -5, 25, 3, 3, 25, -5, 40],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [40, -5, 25, 3, 3, 25, -5, 40],
        [-20, -80, -5, -5, -5, -5, -80, -20],
        [120, -20, 40, 5, 5, 40, -20, 120],
    ]
    res = (sum([int(grid[i][j]) * int(weight[i][j]) for i in range(0, 8) for j in range(0, 8)]))
    return res / 30


def static_weight_ending(grid, turn_count):
    weight = [
        [120, -20, 20, 5, 5, 20, -20, 120],
        [-20, -40, 0, 0, 0, 0, -40, -20],
        [20, 0, 0, 0, 0, 0, 0, 20],
        [5, 0, 0, 0, 0, 0, 0, 5],
        [5, 0, 0, 0, 0, 0, 0, 5],
        [20, 0, 0, 0, 0, 0, 0, 20],
        [-20, -40, 0, 0, 0, 0, -40, -20],
        [120, -20, 20, 5, 5, 20, -20, 120],
    ]
    res = sum([int(grid[i][j]) * int(weight[i][j]) for i in range(0, 8) for j in range(0, 8)])
    return res / 20


