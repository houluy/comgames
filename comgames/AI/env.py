import comgames.game


class Env:
    def __init__(self, game_name):
        self.game = comgames.game.Game(game_name)
        self.max_round = self.game.board.mround()
        self.reward_dic = {
            1: 100,
            -2: 10, # Duel
            0: 0, 
        }
        self.finish_state = {
            "Win": 1,
            "Tie": 2,
            "Move": 0,
        }

    def _reward(self, result):
        return self.reward_dic.get(result)

    def observation(self):
        return self.game.board.state

    def info(self):
        return 

    def actions(self, state):
        return self.game.board.positions(self.game.board.state2board(state))
    
    def step(self, action):
        self.game.move(action)
        finish = self.game.board.check_win_by_step(action, player=self.game.board.player)
        if self.game.board.game_round == self.max_round - 1 and not finish:
            return self.game.board.state, self._reward(-2), self.finish_state["Tie"], "Tie!"
        if finish:
            return self.game.board.state, self._reward(1), self.finish_state["Win"], "Agent wins!"
        if not finish:
            self.game.board.game_round += 1
            return self.game.board.state, self._reward(0), self.finish_state["Move"], "Switch player!"

    def reset(self):
        self.game.board.clear()

