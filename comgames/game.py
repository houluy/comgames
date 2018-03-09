from functools import partial
import sys

from chessboard import Chessboard, PositionError
from colorline import cprint
from .Reversi import Reversi
from . import network

eprint = partial(cprint, color='r', bcolor='c', mode='highlight')
input_print = partial(cprint, color='g', bcolor='k', end='')
nprint = partial(cprint, color='r', bcolor='b')

class Game:
    def __init__(self, game_name, online='local', address=None):
        self.game_name = game_name
        if self.game_name == 'Reversi':
            self.game = Reversi()
        else:
            self.game = Chessboard(game_name=self.game_name)
        self.game.print_pos()
        self.online = online
        if self.online == 'client':
            self.seq = 2
            self.remote = network.Client(**address)
        elif self.online == 'server':
            class TCPHandler(socketserver.BaseRequestHandler):
                def handle(self):
                    self.data = self.request.recv(100)
                    return self.data
            self.seq = 1
            self.remote = network.Server(**address)
        

    def _get_input(self):
        self.player_str = self.game.get_player_str()
        input_print('Player {}\'s turn: '.format(self.player_str))
        ipt = input('')
        pos = self.game.handle_input(ipt, place=False)
        return pos

    def _get_remote_pos(self):


    def play(self, pos):
        winning = self.game.set_pos(pos, check=True)
        if winning is True:
            nprint('player {} wins'.format(self.player_str))
            self.game.print_pos(coordinates=self.game.get_win_list())
            sys.exit(0)
        else:
            self.game.print_pos(coordinates=[winning])

    def local_play(self):
        while True:
            pos = self._get_input()
            self.play(pos)

    def online_play(self, pos):
        if self.seq == 2:
            self.
        while True:


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


