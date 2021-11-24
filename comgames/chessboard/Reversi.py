from chessboard import Chessboard, PositionError

class Reversi(Chessboard):
    '''
    Class for Reversi Game
    '''
    def __init__(self):
        super().__init__(board_size=8)
        self.chess_number = [2, 2]
        self.pos[3][3] = 1
        self.pos[4][4] = 1
        self.pos[3][4] = 2
        self.pos[4][3] = 2
        self._user_pos_dict[1] = [(3, 3), (4, 4)]
        self._user_pos_dict[2] = [(3, 4), (4, 3)]
        self.remind = self.board_size ** 2 - 4

    def check_win(self):
        count = self.count_chess()
        if count[0] != count[1]:
            return 1 if count[0] > count[1] else 2
        else:
            return False

    def get_actions(self, player=None):
        if not player:
            player = self.get_player()
        available_action = []
        oppo_chess_dict = {}
        for chess in self._user_pos_dict[player]:
            for angle in self.full_angle:
                step = 1
                oppo_chess_count = 0
                oppo_chess = []
                while True:
                    close_pos = self.get_close_chess(chess, angle, step)
                    if self.within_range(close_pos):
                        close_chess = self.get_chess(close_pos)
                    else:
                        break
                    if close_chess == player or not self.within_range(close_pos):
                        break
                    elif close_chess == self.another_player(player):
                        step += 1
                        oppo_chess_count += 1
                        oppo_chess.append(close_pos)
                        continue
                    else:
                        if oppo_chess_count > 0:
                            key = self._cal_key(close_pos)
                            if oppo_chess_dict.get(key):
                                oppo_chess_dict[key] += oppo_chess
                            else:
                                oppo_chess_dict[key] = oppo_chess
                            available_action.append(close_pos)
                        break
        return {
            'action': available_action,
            'opponent': oppo_chess_dict,
        }

    def move(self, pos, action=None):
        if not action:
            action = self.get_actions()
        available_action = action.get('action')
        oppo_chess_dict = action.get('opponent')
        current_player = self.get_player()
        another_player = self.another_player()
        if pos in available_action:
            self.set_pos(pos)
            self.remind -= 1
            key = self._cal_key(pos)
            color_list = oppo_chess_dict[key]
            for oppo_chess in color_list:
                self.pos[oppo_chess[0]][oppo_chess[1]] = current_player
                self._user_pos_dict[current_player].append(oppo_chess)
                self._user_pos_dict[another_player].remove(oppo_chess)
            color_list.append(pos)
            return color_list
        else:
            raise PositionError('Error move, please input again!')
