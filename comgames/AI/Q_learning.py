import random
from collections import defaultdict, UserDict
import logging
import pickle
import json

import comgames.game
from .config import config
from .TD.Q import Q
from .TD.agent import TDAgent
from .env import Env


class Value(UserDict):
    def __init__(self):
        super().__init__()

    def _state2str(self, state):
        return ''.join([str(x) for x in state])
    
    def __setitem__(self, key, value):
        if super().__getitem__(key) < value:
            super().__setitem__(self._state2str(key), value)


class QLearning:
    def __init__(self, game_name):
        self.game_name = game_name
        self.params = config.get(game_name).get("Q_learning")
        self.num_episodes = self.params.get('num_episodes')
        self.min_epsilon = self.params.get("min_epsilon")
        self.epsilon = self.params.get("epsilon")
        self.epsilon_decay = self.params.get("epsilon_decay")
        self.env = Env(game_name)
        self.logger = logging.getLogger(__name__)
        self.Q_file = "Q/Q_value.pkl"

    def train(self):
        # Records all Q values
        offensive_Q_list = [0 for _ in range(self.num_episodes)]
        defensive_Q_list = [0 for _ in range(self.num_episodes)]
        Q_list = [0 for _ in range(self.num_episodes)]

        # Records the winning status
        offensive_win = 0
        defensive_win = 0
        tie_count = 0

        # Two agents
        agent_off = TDAgent(self.game_name)
        agent_def = TDAgent(self.game_name)

        for e in range(self.num_episodes):
            state = self.env.observation()
            done = 0
            game_round = 0
            while done == 0:
                game_round += 1
                actions = self.env.actions(state)
                action_off = agent_off.epsilon_greedy(state, actions, self.epsilon)
                intermediate_state, reward_off, done, info = self.env.step(action_off)
                if done: # offensive agent wins or tie
                    reward_def = -reward_off
                    agent_off.Q.update(state, action_off, intermediate_state, reward_off) 
                    agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def)
                else: # turn of defensive agent
                    actions = self.env.actions(intermediate_state)
                    reward_def = reward_off
                    # Need to udpate the Q value of defensive agent after the first round
                    if game_round > 1:
                        agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def, actions)
                    game_round += 1
                    action_def = agent_def.epsilon_greedy(intermediate_state, actions, self.epsilon)
                    next_state, reward_def, done, info = self.env.step(action_def)
                    if done: # defensive agent wins or tie
                        reward_off = -reward_def
                        agent_def.Q.update(intermediate_state, action_def, next_state, reward_def)
                        agent_off.Q.update(state, action_off, next_state, reward_off)
                    else: 
                        actions = self.env.actions(next_state)
                        agent_off.Q.update(state, action_off, next_state, reward_off, actions)
                        last_inter_state = intermediate_state[:]
                self.logger.debug(f"Offensive: state:{state}, action:{action_off}, reward:{reward_off}, next_state: {intermediate_state}")
                self.logger.debug(f"Defensive: state:{intermediate_state}, action:{action_def}, reward:{reward_def}, next_state: {next_state}")
                self.logger.debug(f"Offensive Q sum: {agent_off.Q.sum()}, Defensive Q sum: {agent_def.Q.sum()}")
                state = next_state[:]
            self.epsilon = max(self.min_epsilon, self.epsilon*self.epsilon_decay)
            self.env.reset()
            # Record current Q sum
            offensive_Q_list[e] = agent_off.Q.sum()
            defensive_Q_list[e] = agent_def.Q.sum()
            Q_list[e] = offensive_Q_list[e] + defensive_Q_list[e]

        trained_Q = agent_off.Q + agent_def.Q
        with open(self.Q_file, "wb") as f:
            pickle.dump(trained_Q, f)
        with open("Q/offensive_Q_sum.json", "w") as f:
            json.dump(offensive_Q_list, f)
        with open("Q/defensive_Q_sum.json", "w") as f:
            json.dump(defensive_Q_list, f)
        with open("Q/Q_sum.json", "w") as f:
            json.dump(Q_list, f)
        self.logger.info(f"Offensive wins for {offensive_win} times, defensive wins for {defensive_win} times, ties for {tie_count} times")


class QLearningET(QLearning):
    """ This is the Q learning with Eligibility Trace """
    pass


class NStepQLearning(QLearning):
    def __init__(self, game_name):
        super().__init__(game_name)

    def train(self):
        # Records all Q values
        offensive_Q_list = [0 for _ in range(self.num_episodes)]
        defensive_Q_list = [0 for _ in range(self.num_episodes)]
        Q_list = [0 for _ in range(self.num_episodes)]

        # Records the winning status
        offensive_win = 0
        defensive_win = 0
        tie_count = 0

        # Two agents
        agent_off = TDAgent(self.game_name)
        agent_def = TDAgent(self.game_name)

        for e in range(self.num_episodes):
            state = self.env.observation()
            done = 0
            game_round = 0
            while done == 0:
                game_round += 1
                actions = self.env.actions(state)
                action_off = agent_off.epsilon_greedy(state, actions, self.epsilon)
                intermediate_state, reward_off, done, info = self.env.step(action_off)
                if done: # offensive agent wins or tie
                    reward_def = -reward_off
                    agent_off.Q.update(state, action_off, intermediate_state, reward_off) 
                    agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def)
                else: # turn of defensive agent
                    actions = self.env.actions(intermediate_state)
                    reward_def = reward_off
                    # Need to udpate the Q value of defensive agent after the first round
                    if game_round > 1:
                        agent_def.Q.update(last_inter_state, action_def, intermediate_state, reward_def, actions)
                    game_round += 1
                    action_def = agent_def.epsilon_greedy(intermediate_state, actions, self.epsilon)
                    next_state, reward_def, done, info = self.env.step(action_def)
                    if done: # defensive agent wins or tie
                        reward_off = -reward_def
                        agent_def.Q.update(intermediate_state, action_def, next_state, reward_def)
                        agent_off.Q.update(state, action_off, next_state, reward_off)
                    else: 
                        actions = self.env.actions(next_state)
                        agent_off.Q.update(state, action_off, next_state, reward_off, actions)
                        last_inter_state = intermediate_state[:]
                self.logger.debug(f"Offensive: state:{state}, action:{action_off}, reward:{reward_off}, next_state: {intermediate_state}")
                self.logger.debug(f"Defensive: state:{intermediate_state}, action:{action_def}, reward:{reward_def}, next_state: {next_state}")
                self.logger.debug(f"Offensive Q sum: {agent_off.Q.sum()}, Defensive Q sum: {agent_def.Q.sum()}")
                state = next_state[:]
            self.epsilon = max(self.min_epsilon, self.epsilon*self.epsilon_decay)
            self.env.reset()
            # Record current Q sum
            offensive_Q_list[e] = agent_off.Q.sum()
            defensive_Q_list[e] = agent_def.Q.sum()
            Q_list[e] = offensive_Q_list[e] + defensive_Q_list[e]

        trained_Q = agent_off.Q + agent_def.Q
        with open(self.Q_file, "wb") as f:
            pickle.dump(trained_Q, f)
        with open("Q/offensive_Q_sum.json", "w") as f:
            json.dump(offensive_Q_list, f)
        with open("Q/defensive_Q_sum.json", "w") as f:
            json.dump(defensive_Q_list, f)
        with open("Q/Q_sum.json", "w") as f:
            json.dump(Q_list, f)
        self.logger.info(f"Offensive wins for {offensive_win} times, defensive wins for {defensive_win} times, ties for {tie_count} times")

