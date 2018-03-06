import sys
import argparse
from functools import partial

from chessboard import Chessboard, PositionError
from colorline import cprint
import comgames
from .Reversi import Reversi

eprint = partial(cprint, color='r', bcolor='c', mode='highlight')
input_print = partial(cprint, color='g', bcolor='k', end='')
nprint = partial(cprint, color='r', bcolor='b')

available_games = [
    'fourinarow',
    'Gomoku',
    'tictactoe',
    'Reversi',
    'normal',
]

parser = argparse.ArgumentParser(description='A colorful calendar', prefix_chars='-+')
parser.add_argument('-v', '--version', help='show version', version=comgames.__version__, action='version')
parser.add_argument('-g', '--game', help='Game name', choices=available_games)

def play_reversi(r):
    r.print_pos()
    end = False
    while True:
        action = r.get_actions()
        player = r.get_player_str()
        opponent = r.another_player_str()
        if not action.get('action'):
            if r.remind != 0:
                nprint('player {} stops!'.format(player))
            if end == True or r.remind == 0:
                winner = r.check_win()
                nprint('Player {} wins'.format(r.character.get(winner)))
                winner_chess = r.user_pos_dict[winner]
                r.print_pos(winner_chess)
                sys.exit(0)
            else:
                r.skip_round()
                end = True
                continue
        input_print('player {} moves: '.format(player))
        input_str = input('')
        try:
            pos = r.handle_input(input_str, place=False, check=False)
        except Exception as e:
            eprint(e)
            continue
        if pos[0] != 'u':
            try:
                color_list = r.move(pos, action)
            except PositionError as e:
                eprint(e)
                r.print_pos(action.get('action'))
                continue
            except Exception as e:
                eprint(e)
                continue
            r.print_pos(color_list)
        else:
            r.print_pos()
        end = False

def main():
    args = parser.parse_args()
    while True:
        if args.game:
            game_name = args.game
        else:
            game_name = input('Please input the game name: ')
        if game_name == 'Reversi':
            r = Reversi()
            play_reversi(r)
        try:
            board = Chessboard(game_name=game_name)
        except ValueError as e:
            eprint(e)
            continue
        else:
            break

    board.print_pos()
    while True:
        player_str = board.get_player_str()
        input_print('Player {}\'s turn: '.format(player_str))
        ipt = input('')
        try:
            pos = board.handle_input(ipt, check=True)
        except Exception as e:
            eprint(e)
            board.print_pos()
            continue
        if pos is True:
            nprint('player {} wins'.format(player_str))
            board.print_pos(coordinates=board.get_win_list())
            sys.exit(0)
        else:
            board.print_pos(coordinates=[pos])
        #print(str(board))

if __name__ == '__main__':
    main()
