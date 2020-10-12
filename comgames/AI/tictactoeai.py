import random
from collections import defaultdict, UserDict
from collections.abc import Iterable, MutableSequence
import logging
import pickle
import json


fmt = "%(message)s"
logging.basicConfig(
    level=logging.DEBUG, format=fmt, filename="logs.log"
)

import comgames.game
from .config import tictactoe


class Env:
    def __init__(self):
        self.game = comgames.game.Game("tictactoe")
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


class Value(UserDict):
    def __init__(self):
        super().__init__()

    def _state2str(self, state):
        return ''.join([str(x) for x in state])
    
    def __setitem__(self, key, value):
        if super().__getitem__(key) < value:
            super().__setitem__(self._state2str(key), value)


class Q(UserDict):
    def __init__(self, gamma=0.9999, alpha=0.9):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

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
        else:
            max_nQ = self[(next_state,)]
        self[key] = current_Q + self.alpha*(reward + self.gamma * max_nQ - current_Q)

    def sum(self):
        val = 0
        for k, v in self.data.items():
            val += v
        return val

    def __add__(self, other):
        for key, value in self.data.items():
            if other[key] != 0:
                self[key] = (other[key] + value)/2
        for key, value in other.data.items():
            if self[key] == 0:
                self[key] = value
        return self


class Agent:
    def __init__(self, dumped_qfile=None):
        if dumped_qfile is None:
            gamma = tictactoe.get("Q_learning").get("gamma")
            alpha = tictactoe.get("Q_learning").get("alpha")
            self.Q = Q(gamma=gamma, alpha=alpha)
        else:
            with open(dumped_qfile, 'rb') as f:
                self.Q = pickle.load(f)

    @classmethod
    def by_Q(cls, Q_dic: Q):
        """Initialize an agent with Q instance"""
        inst = cls()
        inst.Q = Q_dic
        inst.gamma, inst.alpha = Q_dic.gamma, Q_dic.alpha
        return inst

    def epsilon_greedy(self, state, actions, epsilon=0.1):
        rand = random.random()
        if rand < epsilon:
            return random.choice(actions)
        else:
            return self.greedy(state, actions)

    def greedy(self, state, actions):
        for ind, a in enumerate(actions):
            if ind == 0:
                action, maxQ = [a], self.Q[(state, a)]
            else:
                q_value = self.Q[(state, a)]
                if q_value > maxQ:
                    action, maxQ = [a], q_value
                elif q_value == maxQ:
                    action.append(a) # randomly choose an action if Q value is equivalent
                else:
                    continue
        if len(action) == 1:
            return action[0]
        else:
            return random.choice(action)


def Q_learning_train():
    params = tictactoe.get("Q_learning")
    epsilon = 1
    min_epsilon = params.get("min_epsilon")
    epsilon_decay = params.get("epsilon_decay")
    num_episodes = params.get("num_episodes")
    env = Env()
    agent_off = Agent()
    agent_def = Agent()

    # Records
    # Records all Q values
    offensive_Q_list = [0 for _ in range(num_episodes)]
    defensive_Q_list = [0 for _ in range(num_episodes)]
    Q_list = [0 for _ in range(num_episodes)]

    # Records the winning status
    offensive_win = 0
    defensive_win = 0
    tie_count = 0

    for e in range(num_episodes):
        state = env.observation()
        done = 0
        game_round = 0
        while done == 0:
            game_round += 1
            actions = env.actions(state)
            action_off = agent_off.epsilon_greedy(state, actions, epsilon)
            intermediate_state, reward_off, done, info = env.step(action_off)
            if done: # offensive agent wins or tie
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
                action_def = agent_def.epsilon_greedy(intermediate_state, actions, epsilon)
                next_state, reward_def, done, info = env.step(action_def)
                if done: # defensive agent wins or tie
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
        epsilon = max(min_epsilon, epsilon*epsilon_decay)
        env.reset()
        # Record current Q sum
        offensive_Q_list[e] = agent_off.Q.sum()
        defensive_Q_list[e] = agent_def.Q.sum()
        Q_list[e] = offensive_Q_list[e] + defensive_Q_list[e]

    trained_Q = agent_off.Q + agent_def.Q     
    with open("Q/Q_value.pkl", "wb") as f:
        pickle.dump(trained_Q, f)
    with open("Q/offensive_Q_sum.json", "w") as f:
        json.dump(offensive_Q_list, f)
    with open("Q/defensive_Q_sum.json", "w") as f:
        json.dump(defensive_Q_list, f)
    with open("Q/Q_sum.json", "w") as f:
        json.dump(Q_list, f)
    logging.info(f"Offensive wins for {offensive_win} times, defensive wins for {defensive_win} times, ties for {tie_count} times")
  

def run(turn="offensive"):
    with open("Q/Q_value.pkl", "rb") as f:
        trained_Q = pickle.load(f)
    agent = Agent.by_Q(trained_Q)
    env = Env()
    done = 0
    game_round = 0
    env.game.board.print_pos()
    state = env.observation()
    while done == 0:
        game_round += 1
        if turn == "offensive":
            actions = env.actions(state) 
            action = agent.greedy(state, actions)
        elif turn == "defensive":
            action = env.game.input_pos() # Be careful, no exception handlers here
        state, _, done, info = env.step(action)
        env.game.board.print_pos(coordinates=[action])
        env.game.celebrate(done)
        if done:
            break
        if turn == "offensive":
            action = env.game.input_pos() # Be careful, no exception handlers here
        elif turn == "defensive":
            actions = env.actions(state) 
            action = agent.greedy(state, actions)
        next_state, _, done, info = env.step(action)
        env.game.board.print_pos(coordinates=[action])
        env.game.celebrate(done)
        state = next_state[:]
    


