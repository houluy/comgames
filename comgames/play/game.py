import sys
import socket
import logging

from comgames.chessboard import Chessboard, PositionError
from comgames.chessboard.Reversi import Reversi
from comgames.utils import *

class Game:
    def __init__(self, game_name):
        self.game_name = game_name
        self.logger = logging.getLogger(__name__)
        if self.game_name == 'Gomoku':
            self.board_size = 15
            self.win = 5
        elif self.game_name == 'tictactoe':
            self.board_size = 3
            self.win = 3
        elif self.game_name == 'fourinarow':
            """Four in a row has a typical rule that only column number needs to be determined
            by players!
            """
            self.board_size = 7
            self.win = 4
        elif self.game_name == 'Reversi':
            self.board_size = 15
            self.win = -1
        elif self.game_name == 'normal':
            self.board_size = int(input('Board size: '))
            self.win = int(input('Winning chess number: '))
        else:
            raise ValueError('Unsupported game, please refer to docs!')
        
        if self.game_name == 'Reversi':
            self.board = Reversi()
        else:
            self.board = Chessboard(board_size=self.board_size, win=self.win)

    def debug(self, *args):
        for a in args:
            self.logger.debug(a)

    def input_pos(self, board):
        """ Get position from input """
        input_print('Player {}\'s turn: '.format(board.character[board.player]))
        ipt = input('')
        if self.game_name == "fourinarow":
            return board.process_single_ipt(ipt)
        else:
            return board.process_ipt(ipt)

    def _get_remote_pos(self, sock):
        data = sock.recv(MAX_LENGTH)
        return data.decode()

    def _send_pos(self, sock, pos_str):
        sock.send(pos_str.encode())

    def celebrate(self, done=0):
        if done == 0:
            return
        elif done == 1:
            nprint('Player {} wins'.format(self.board.player_ch))
            self.board.print_pos(coordinates=self.board.win_list)
        else:
            nprint('TIE!')

    def column2pos(self, column):
        "Convert column to position, using the topmost row"
        row = self.board.get_row_by_column(column)
        return (row, column)

    def move(self, pos):
        if self.game_name == "fourinarow":
            pos = self.column2pos(pos)
        self.board.set_pos(pos, validate=True)
        return pos

    def _basic_handle(self, pos):
        winning = self.move(pos)
        self._check_win(winning)
        return pos

    def _handle_remote_with_pos(self, pos_str):
        pos = self.board.handle_input(pos_str, place=False)
        self._basic_handle(pos)

    def _handle_remote(self, sock):
        self.player_str = self.board.get_player_str()
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

    def play(self, pos_func):
        """
        Play game, the pos can be generated in three ways:
        - local input
        - AI agent
        - Remote server
        Params:
        @pos_func: Function to generate pos
            pos = pos_func(board)
        """
        finish = False
        done = 1
        max_round = self.board.mround()
        self.board.print_pos()
        self.board.game_round += 1
        while not finish:
            try:
                pos = pos_func(self.board)
            except (ValueError, PositionError) as e:
                eprint(e)
                continue
            self.board.set_pos(pos)
            self.board.print_pos(coordinates=[pos])
            finish = self.board.check_win_by_step(pos, player=self.board.player)
            if self.board.game_round == max_round and not finish:
                done = 2
                break
            if not finish:
                self.board.game_round += 1
        self.celebrate(done)

    #def play(self, mode, **kwargs):
    #    self.mode = mode
    #    if self.mode == 'local':
    #        while True:
    #            try:
    #                self._handle_local()
    #            except Exception as e:
    #                eprint(e)
    #                continue
    #    else:
    #        s = kwargs.get('socket')
    #        first_move = kwargs.get('first')
    #        if self.mode == 'client':
    #            self._handle_remote_with_pos(first_move)
    #        while True:
    #            try:
    #                pos = self._handle_send(s)
    #            except Exception as e:
    #                eprint(e)
    #                eprint('Retry please: ')
    #                continue
    #            while True:
    #                try:
    #                    self._handle_remote(s)
    #                except Exception as e:
    #                    eprint(e)
    #                    continue
    #                else:
    #                    break

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


