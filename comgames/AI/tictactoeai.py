import random

import comgames.game


class Env:
    def __init__(self):
        self.game = comgames.game.Game("tictactoe")
        self.game.board.print_pos()
        self.max_round = self.game.board.mround()
        self.reward_dic = {
            1: 10,
            -1: -10,
            -2: 1, # Duel
            0: 0, 
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
        self.game.board.print_pos(coordinates=[action])
        finish = self.game.board.check_win_by_step(action, player=self.game.board.player)
        done = False
        if self.game.board.game_round == self.max_round - 1 and not finish:
            done = True
            self.game.celebrate(duel=True)
            return self.game.board.state, self._reward(-2), done, "Duel!"
        if finish:
            done = True
            self.game.celebrate(duel=False)
            return self.game.board.state, self._reward(1), done, "Agent wins!"
        if not finish:
            self.game.board.game_round += 1
            pos = self.game.input_pos()
            self.game.board.set_pos(pos)
            self.game.board.print_pos(coordinates=[pos])
            finish = self.game.board.check_win_by_step(pos, player=self.game.board.player)
            if self.game.board.game_round == self.max_round and not finish:
                done = True
                self.game.celebrate(duel=True)
                return self.game.board.state, self._reward(-2), done, "Duel!"
            if finish:
                done = True
                self.game.celebrate(duel=False)
                return self.game.board.state, self._reward(-1), done, "Player wins!"
            if not finish:
                self.game.board.game_round += 1
                return self.game.board.state, self._reward(0), done, "Not finished"

    def reset(self):
        self.game.board.clear()



episodes = 1
env = Env()

for e in range(episodes):
    state = env.observation()
    done = False
    while not done:
        actions = env.actions(state)
        action = random.choice(actions)
        next_state, reward, done, info = env.step(action)
        print(reward)
        state = next_state


