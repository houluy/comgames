import sys
import argparse
from functools import partial

from chessboard import Chessboard, PositionError
from colorline import cprint
import comgames

eprint = partial(cprint, color='r', bcolor='c', mode='highlight')

available_games = [
    'fourinarow',
    'Gomoku',
    'tictactoe',
    'normal',
]

parser = argparse.ArgumentParser(description='A colorful calendar', prefix_chars='-+')
parser.add_argument('-v', '--version', help='show version', version=comgames.__version__, action='version')
parser.add_argument('-g', '--game', help='Game name', choices=available_games)

def main():
    args = parser.parse_args()
    while True:
        if args.game:
            game_name = args.game
        else:
            game_name = input('Please input the game name: ')
        try:
            board = Chessboard(game_name=game_name)
        except ValueError as e:
            eprint(e)
            continue
        else:
            break

    board.print_pos()
    while True:
        player_number = board.get_player()
        cprint('Player {}\'s turn: '.format(player_number), color='y', bcolor='c', end='')
        ipt = input('')
        try:
            pos = board.handle_input(ipt, check=True)
        except Exception as e:
            eprint(e)
            board.print_pos()
            continue
        if pos is True:
            cprint('player {} wins'.format(player_number), color='y', bcolor='b')
            board.print_pos(coordinates=board.get_win_list())
            sys.exit(0)
        else:
            board.print_pos(coordinates=[pos])
        #print(str(board))

if __name__ == '__main__':
    main()
