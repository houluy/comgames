import sys
import socket

from comgames.play.game import Game
from comgames.AI.env import Env
from comgames.AI.agent import agent_list
from comgames.AI.train import Trainer
from comgames.utils import *


def main(args):
    if args.connect or args.host:
        # Play online
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
        elif args.host:
            host, port = args.host, args.port
            s.bind((host, port))
            s.listen(1)
            nprint('Waiting for connection...')
            sock, addr = s.accept()
            nprint('Receive a connection from {}'.format(addr))
            sock.send(game_name.encode())
            mode = 'server'
            kwargs['socket'] = sock
            game_name = args.game
            s.close()
    elif args.train:
        game = Game(game_name=args.game)
        trainer = Trainer(game, algo=args.algorithm)
        trainer.train()
    else:
        # Play locally
        game = Game(game_name=args.game)
        if args.ai:
            algo = args.algorithm
            env = Env(game)
            agent = agent_list[algo](env=env)
            game.play(pos_func=agent.act)
        else:
            game.play(pos_func=game.input_pos)



