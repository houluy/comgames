import random
from collections import defaultdict, UserDict
from collections.abc import Iterable, MutableSequence
import logging
import pickle

fmt = "%(message)s"
logging.basicConfig(
    level=logging.DEBUG, format=fmt, filename="logs.log"
)

import comgames.game


class Env:
    def __init__(self):
        self.game = comgames.game.Game("tictactoe")
        self.game.board.print_pos()
        self.max_round = self.game.board.mround()
        self.reward_dic = {
            1: 100,
            -2: 0, # Duel
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
            return self.game.board.state, self._reward(0), done, "Switch player!"

    def reset(self):
        self.game.board.clear()


class Q(UserDict):
    def __init__(self, gamma=0.9, alpha=0.1):
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

    def sum(self):
        val = 0
        for k, v in self.data.items():
            val += v
        return val


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
    episodes = 3000
    env = Env()
    agent_off = Agent()
    agent_def = Agent()

    for e in range(episodes):
        state = env.observation()
        done = False
        game_round = 0
        while not done:
            game_round += 1
            actions = env.actions(state)
            action_off = agent_off.epsilon_greedy(state, actions)
            intermediate_state, reward_off, done, info = env.step(action_off)
            if done: # offensive agent wins or duel
                reward_def = -reward_off
                agent_off.Q.update(state, action_off, intermediate_state, reward_off) 
                agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def)
            else: # turn of defensive agent
                actions = env.actions(intermediate_state)
                reward_def = reward_off
                # Need to udpate the Q value of defensive agent after the first round
                if game_round > 1:
                    agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def, actions)
                game_round += 1
                action_def = agent_def.epsilon_greedy(intermediate_state, actions)
                next_state, reward_def, done, info = env.step(action_def)
                if done: # defensive agent wins or duel
                    reward_off = -reward_def
                    agent_def.Q.update(intermediate_state, action_def, next_state, reward_def)
                    agent_off.Q.update(state, action_off, next_state, reward_off)
                else: 
                    actions = env.actions(next_state)
                    agent_off.Q.update(state, action_off, next_state, reward_off, actions)
                    last_inter_state = intermediate_state[:]
            logging.debug(f"Offensive: state:{state}, action:{action_off}, reward:{reward_off}, next_state: {intermediate_state}")
            logging.debug(f"Defensive: state:{intermediate_state}, action:{action_def}, reward:{reward_def}, next_state: {next_state}")
            logging.debug(f"Offensive Q sum: {agent_off.Q.sum()}, Defensive Q sum: {agent_def.Q.sum()}")
            state = next_state[:]

        env.reset()
    with open("Q/offensive.pkl", "wb") as f:
        pickle.dump(agent_off.Q, f)
    with open("Q/defensive.pkl", "wb") as f:
        pickle.dump(agent_def.Q, f)
#    print(agent_off.Q)
#    print(agent_def.Q)
#    print(game_round)

