import sys
import socket

from comgames.game import Game
from comgames.utils import *


def main(args):
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
    if game_name == "fourinarow":
        game.play_fourinarow()
    else:
        game.local_play()
    s.close()


def local_main(args):
    game_name = args.game
    game = Game(game_name=game_name)
    game.local_play()

