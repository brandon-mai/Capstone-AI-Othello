import pygame
from othello import Othello

if __name__ == '__main__':

    # MODIFY THESE ONLY #
    mode = 1
    is_recording = False
    game_file = 'game_records/Game_231223_121159.py'  # demo game record with mode = 1
    # game_file = 'game_records/Game_231223_180856.py'  # demo game record with mode = 2
    # game_file = 'game_records/Game_231223_181031.py'  # demo game record with mode = 3
    # MODIFY THESE ONLY #

    while True:
        game = Othello(mode=mode, is_recording=is_recording, imported_file_path=game_file)
        next_mode, game_file = game.run()
        if next_mode == 0:
            break
        mode = next_mode

    pygame.quit()
