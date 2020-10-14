import logging

class Env:
    def __init__(self):
        self.game = comgames.game.Game("fourinarow")
        self.max_round = self.game.board.mround()
        self.reward_dic = {
            1: 100,
            -2: 0, # Duel
            0: 0,
        }
        self.finish_state = {
            "Win": 1,
            "Tie": 2,
            "Move": 0,
        }

    def _reward(self, result):
        return self.reward_dic.get(result)


