from utility_functions import *

# heuristics for Computer player


# Global functions help assess grid
def findValidCellsGlobal(grid, currentPlayer):
    '''Return a list of all empty cells that are adjacent to opposing player'''
    validCellToClick = []
    for gridX, row in enumerate(grid):
        for gridY, col in enumerate(row):
            if grid[gridX][gridY] != 0:
                continue
            DIRECTIONS = directions(gridX, gridY)

            for direction in DIRECTIONS:
                dirX, dirY = direction
                checkedCell = grid[dirX][dirY]

                if checkedCell == 0 or checkedCell == currentPlayer:
                    continue

                if (gridX, gridY) in validCellToClick:
                    continue

                validCellToClick.append((gridX, gridY))
    return validCellToClick


def swappableTilesGlobal(x, y, grid, currentPlayer):
    '''Return a list of all opponent's tiles being flipped if currentPlayer moves to (x, y)'''
    surroundCells = directions(x, y)
    if len(surroundCells) == 0:
        return []

    swappableTiles = []
    for checkCell in surroundCells:
        checkX, checkY = checkCell
        difX, difY = checkX - x, checkY - y
        currentLine = []

        RUN = True
        while RUN:
            if grid[checkX][checkY] == currentPlayer * -1:
                currentLine.append((checkX, checkY))
            elif grid[checkX][checkY] == currentPlayer:
                RUN = False
                break
            elif grid[checkX][checkY] == 0:
                currentLine.clear()
                RUN = False
            checkX += difX
            checkY += difY

            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                currentLine.clear()
                RUN = False

        if len(currentLine) > 0:
            swappableTiles.extend(currentLine)

    return swappableTiles


def findAvailMovesGlobal(grid, currentPlayer):
    '''Return a list of possible moves from currentPlayer'''
    validCells = findValidCellsGlobal(grid, currentPlayer)
    playableCells = []

    for cell in validCells:
        x, y = cell
        if cell in playableCells:
            continue
        swapTiles = swappableTilesGlobal(x, y, grid, currentPlayer)

        # if len(swapTiles) > 0 and cell not in playableCells:
        if len(swapTiles) > 0:
            playableCells.append(cell)

    return playableCells


# heuristics
def coinParity(grid, player):
    score = 0
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            score += (col * player)
    return score