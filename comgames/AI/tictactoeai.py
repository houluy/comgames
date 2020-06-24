import random
from collections import defaultdict, UserDict
from collections.abc import Iterable, MutableSequence

import comgames.game


class Env:
    def __init__(self):
        self.game = comgames.game.Game("tictactoe")
        self.game.board.print_pos()
        self.max_round = self.game.board.mround()
        self.reward_dic = {
            1: 10,
            -1: -10,
            -2: 5, # Duel
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


class Q(UserDict):
    def __init__(self, gamma=0.99, alpha=0.1):
        self.gamma = gamma
        self.alpha = alpha
        super().__init__()

    def __str__(self):
        ret_str = []
        for key, value in self.data.items():
            try:
                ret_str.append(f"State: {key[0]}, action: {key[1]}, Q: {value}")
            except IndexError: # Terminal state, no actions
                ret_str.append(f"Terminal state: {key}, Q: {value}")
        return '\n'.join(ret_str)

    def _state2str(self, state):
        return ''.join([str(x) for x in state])

    def _key_transform(self, key):
        assert len(key) <= 2
        assert isinstance(key[0], Iterable)
        state_str = self._state2str(key[0])
        try:
            new_key = (state_str, key[1])
        except IndexError:
            new_key = (state_str,)
        return new_key

    def __getitem__(self, key):
        """
        @params
        key: a two-element tuple, first element is an iterable, second one can be empty (terminal state)
        """
        new_key = self._key_transform(key)
        return super().__getitem__(new_key)

    def __setitem__(self, key, value):
        new_key = self._key_transform(key)
        super().__setitem__(new_key, value)

    def __missing__(self, key):
        self.data[key] = value = 0
        return value

    def update(self, state, action, next_state, reward, actions=None):
        key = (state, action)
        current_Q = self[key]
        if actions is not None:
            for ind, a in enumerate(actions):
                if ind == 0:
                    max_nQ = self[(next_state, a)]
                else:
                    temp_Q = self[(next_state, a)]
                    if temp_Q > max_nQ:
                        max_nQ = temp_Q
            # For non-terminal state: Q(s, a) <- Q(s, a) + alpha[r + gamma * maxQ(s', a') - Q(s, a)]
        else:
            max_nQ = self[(next_state,)]
        self[key] = current_Q + self.alpha*(reward + self.gamma * max_nQ - current_Q)


class Agent:
    def __init__(self):
        self.Q = Q()

    def epsilon_greedy(self, state, actions, epsilon=0.1):
        rand = random.random()
        if rand < epsilon:
            return random.choice(actions)
        else:
            for ind, a in enumerate(actions):
                if ind == 0:
                    action, maxQ = [a], self.Q[(state, a)]
                else:
                    Q = self.Q[(state, a)]
                    if self.Q[(state, a)] > maxQ:
                        action, maxQ = [a], self.Q[(state, a)]
                    elif self.Q[(state, a)] == maxQ:
                        action.append(a) # randomly choose an action if Q value is equivalent
                    else:
                        continue
            if len(action) == 1:
                return action[0]
            else:
                return random.choice(action)


def main():
    episodes = 5
    env = Env()
    agent = Agent()

    for e in range(episodes):
        state = env.observation()
        done = False
        while not done:
            actions = env.actions(state)
            action = agent.epsilon_greedy(state, actions)
            next_state, reward, done, info = env.step(action)
            if done:
                agent.Q.update(state, action, next_state, reward) 
            else:
                agent.Q.update(state, action, next_state, reward, actions=env.actions(next_state))
                state = next_state
        env.reset()
    print(agent.Q)

