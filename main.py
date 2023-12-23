import pygame
from othello import Othello

if __name__ == '__main__':

    # MODIFIABLE #
    mode = 0
    is_recording = True
    game_file = 'game_records/Game_231223_121159.py'  # demo game mode = 1
    # game_file = 'game_records/Game_231223_121911.py'  # demo game mode = 2
    # game_file = 'game_records/Game_231223_123357.py'  # demo game mode = 3
    ##############

    game = Othello(mode, is_recording, game_file)
    game.run()
    pygame.quit()
