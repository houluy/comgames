import sys
import argparse
from functools import partial

from chessboard import Chessboard, PositionError
from colorline import cprint
import comgames
from .network import *
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
parser.add_argument('--host', help='Host a game online')
parser.add_argument('-p', '--port', help='Port', type=int, default=9999)
parser.add_argument('-c', '--connect', help='Connect to a server, \'host:port\'')

def main():
    args = parser.parse_args()
    if args.host:
        server = Server(args.host, args.port)
    elif args.connect:
        host, port = args.connect.split(':')
        client = Client(host, int(port))
        client.connect()

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

if __name__ == '__main__':
    main()
