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
from .Q_learning.Q import Q
from .env import Env


class Value(UserDict):
    def __init__(self):
        super().__init__()

    def _state2str(self, state):
        return ''.join([str(x) for x in state])
    
    def __setitem__(self, key, value):
        if super().__getitem__(key) < value:
            super().__setitem__(self._state2str(key), value)




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
    


