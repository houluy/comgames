import sys
import socket

from chessboard import Chessboard, PositionError
from .Reversi import Reversi
from .utils import *

class Game:
    def __init__(self, game_name):
        self.game_name = game_name
        if self.game_name == 'Reversi':
            self.game = Reversi()
        else:
            self.game = Chessboard(game_name=self.game_name)
        self.game.print_pos()

    def _get_input(self, raw=False):
        self.player_str = self.game.get_player_str()
        input_print('Player {}\'s turn: '.format(self.player_str))
        ipt = input('')
        pos = self.game.handle_input(ipt, place=False)
        if raw:
            return ipt
        else:
            return pos

    def _get_remote_pos(self, sock):
        data = sock.recv(MAX_LENGTH)
        return data.decode()

    def _send_pos(self, sock, pos_str):
        sock.send(pos_str.encode())

    def _check_win(self, winning):
        if winning is True:
            nprint('player {} wins'.format(self.player_str))
            self.game.print_pos(coordinates=self.game.get_win_list())
            sys.exit(0)
        else:
            self.game.print_pos(coordinates=[winning])

    def _basic_handle(self, pos):
        winning = self.move(pos)
        self._check_win(winning)
        return pos

    def _handle_remote_with_pos(self, pos_str):
        pos = self.game.handle_input(pos_str, place=False)
        self._basic_handle(pos)

    def _handle_remote(self, sock):
        self.player_str = self.game.get_player_str()
        nprint('Waiting for the other player to move...')
        pos_str = self._get_remote_pos(sock)
        self._handle_remote_with_pos(pos_str)

    def _handle_local(self):
        pos = self._get_input()
        self._basic_handle(pos)

    def _handle_send(self, sock):
        pos_str = self._get_input(raw=True)
        self._send_pos(sock, pos_str)
        self._handle_remote_with_pos(pos_str)

    def move(self, pos):
        return self.game.set_pos(pos, check=True)

    def play(self, mode, **kwargs):
        self.mode = mode
        if self.mode == 'local':
            while True:
                try:
                    self._handle_local()
                except Exception as e:
                    eprint(e)
                    continue
        else:
            s = kwargs.get('socket')
            first_move = kwargs.get('first')
            if self.mode == 'client':
                self._handle_remote_with_pos(first_move)
            while True:
                try:
                    pos = self._handle_send(s)
                except Exception as e:
                    eprint(e)
                    eprint('Retry please: ')
                    continue
                while True:
                    try:
                        self._handle_remote(s)
                    except Exception as e:
                        eprint(e)
                        continue
                    else:
                        break

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


