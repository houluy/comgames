import sys
import argparse
import socket

import comgames
from .Reversi import Reversi
from .game import Game
from .utils import *

available_games = [
    'fourinarow',
    'Gomoku',
    'tictactoe',
    'Reversi',
    'normal',
]

parser = argparse.ArgumentParser(description='A colorful calendar', prefix_chars='-+')
parser.add_argument('-v', '--version', help='show version', version=comgames.__version__, action='version')
parser.add_argument('-g', '--game', help='Game name', choices=available_games, default='tictactoe')
parser.add_argument('--host', help='Host a game online')
parser.add_argument('-p', '--port', help='Port', type=int, default=9999)
parser.add_argument('-c', '--connect', help='Connect to a server, \'host:port\'')

def main():
    args = parser.parse_args()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if args.connect:
        host, port = args.connect.split(':')
        port = int(port)
        try:
            s.connect((host, port))
        except Exception as e:
            eprint(e)
            sys.exit(-1)
        game_name = s.recv(MAX_LENGTH).decode()
        nprint('Start playing {} with {}'.format(game_name, (host, port)))
        first_move = s.recv(MAX_LENGTH).decode()
        mode = 'client'
        kwargs = {
            'socket': s,
            'first': first_move,
        }
    else:
        game_name = args.game
        mode = 'local'
        kwargs = {}
        if args.host:
            host, port = args.host, args.port
            s.bind((host, port))
            s.listen(1)
            nprint('Waiting for connection...')
            sock, addr = s.accept()
            nprint('Receive a connection from {}'.format(addr))
            sock.send(game_name.encode())
            mode = 'server'
            kwargs['socket'] = sock
    game = Game(game_name=game_name)
    game.play(mode=mode, **kwargs)
    s.close()

if __name__ == '__main__':
    main()
