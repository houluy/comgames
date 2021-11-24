from .agent import agent_list
from .env import Env
import logging
import pickle
import pathlib
import json
import csv
import pdb


class Trainer:
    def __init__(self, game, algo="QLearning"):
        self.env = Env(game)
        agent_cls = agent_list[algo]
        self.defensive_agent = agent_cls(env=self.env, new=True)
        self.offensive_agent = agent_cls(env=self.env, new=True)
        self.basic_info = f"{self.env.game_name}-{algo}"
        self.stat_path = pathlib.Path(f"comgames/Q/{self.env.game_name}/{algo}/train")
        self.offensive_Q_sum = self.stat_path / "offensive_Q_sum.csv"
        self.defensive_Q_sum = self.stat_path / "defensive_Q_sum.csv"
        self.Q_sum = self.stat_path / "Q_sum.csv"
        self.x_range_file = self.stat_path / "x.csv"
        if not self.stat_path.exists():
            self.stat_path.mkdir(parents=True)
        self.logger = logging.getLogger(__name__)

    def train(self, episodes=10000):
        """
        state changes:

        offensive_state → offensive_next_state == defensive_state → defensive_next_state == offensive_state == last_defensive_state

        """
        self.env.reset()
        ## Only for statistic
        offensive_Q_list = list(range(episodes))
        defensive_Q_list = list(range(episodes))
        Q_list = list(range(episodes))
        offensive_win = 0
        defensive_win = 0
        tie_count = 0
        for eps in range(episodes):
            offensive_state = self.env.observation()
            done = 0
            game_round = 0
            #pdb.set_trace()
            last_defensive_state = None
            action_def = None
            while done == 0:
                game_round += 1
                actions = self.env.actions(offensive_state)
                action_off = self.offensive_agent.decayed_epsilon_greedy(offensive_state, actions, current_episode=eps, total_episodes=episodes)
                offensive_next_state, reward_off, done, info = self.env.step(action_off)
                if done == 1 or done == 2: # offensive agent wins or tie
                    if done == 1:
                        reward_def = -reward_off
                        offensive_win += 1
                    elif done == 2:
                        reward_def = reward_off
                        tie_count += 1
                    self.offensive_agent.update_Q(offensive_state, action_off, reward_off, done=done)
                    self.defensive_agent.update_Q(defensive_state, action_def, reward_def, done=done)
                else: # turn of defensive agent
                    game_round += 1
                    defensive_state = offensive_next_state
                    actions = self.env.actions(defensive_state)
                    reward_def = reward_off # nobody wins, reward is equivalent to zero
                    if game_round > 2:
                        # Here we update the Q value of defensive agent for previous round
                        print(game_round, done)
                        self.defensive_agent.update_Q(last_defensive_state, action_def, reward_def, done, defensive_state, actions) 
                    action_def = self.defensive_agent.decayed_epsilon_greedy(defensive_state, actions, current_episode=eps, total_episodes=episodes)
                    defensive_next_state, reward_def, done, info = self.env.step(action_def)
                    if done == 1 or done == 2:  # Defensive agent wins or tie
                        if done == 1:
                            reward_off = -reward_def
                            defensive_win += 1
                        elif done == 2:
                            reward_off = reward_def
                            tie_count += 1
                        self.defensive_agent.update_Q(defensive_state, action_def, reward_def, done)
                        self.offensive_agent.update_Q(offensive_state, action_off, reward_off, done)
                    else:
                        last_defensive_state = defensive_state[:]
                        offensive_state = defensive_next_state[:]
                self.logger.debug(f"Offensive: state:{offensive_state}, action:{action_off}, reward:{reward_off}, next_state: {offensive_next_state}")
                self.logger.debug(f"Defensive: state:{defensive_state}, action:{action_def}, reward:{reward_def}, next_state: {defensive_next_state}")
                self.logger.debug(f"Offensive Q sum: {self.offensive_agent.Q.sum()}, Defensive Q sum: {self.defensive_agent.Q.sum()}")
            #self.epsilon = max(self.min_epsilon, self.epsilon*self.epsilon_decay)
            self.env.reset()
            # Record current Q sum
            offensive_Q_list[eps] = self.offensive_agent.Q.sum()
            defensive_Q_list[eps] = self.defensive_agent.Q.sum()
            Q_list[eps] = offensive_Q_list[eps] + defensive_Q_list[eps]
        trained_Q = self.offensive_agent.Q + self.defensive_agent.Q
        with open(self.offensive_agent.Q_file, "wb") as f:
            pickle.dump(trained_Q, f)
        with open(self.offensive_Q_sum, "w") as f:
            writer = csv.writer(f)
            for i in offensive_Q_list:
                writer.writerow([i])
        with open(self.defensive_Q_sum, "w") as f:
            writer = csv.writer(f)
            for i in defensive_Q_list:
                writer.writerow([i])
        with open(self.Q_sum, "w") as f:
            writer = csv.writer(f)
            for i in Q_list:
                writer.writerow([i])
        with open(self.x_range_file, "w") as f:
            writer = csv.writer(f)
            for i in range(episodes):
                writer.writerow([i + 1])
        self.logger.info(f"Offensive wins for {offensive_win} times, defensive wins for {defensive_win} times, ties for {tie_count} times")

