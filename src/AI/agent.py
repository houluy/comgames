import random
import logging
import pathlib

from .Q import Q
from .config import config


agent_list = {}
def push(cls):
    agent_list[cls.__name__] = cls
    return cls


class Agent:
    def __init__(self, new):
        self.logger = logging.getLogger(__name__)
        self.Q_file = pathlib.Path(f"Q/{self.__class__.__name__}/Q_value.pkl")
        self.initialize_Q_table(new)

    def initialize_Q_table(self, new):
        """
        Initialize Q table for agent
        @new: boolean
            True: return an empty Q table
            False: load from self.Q_file
        """
        if new:
            self.Q = Q()
        else:
            with open(self.Q_file) as f:
                self.Q = pickle.load(f)

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


class TDAgent(Agent):
    def __init__(self, new=True):
        super().__init__(new)

    def update(self, state, action, target):
        current_Q = self.Q[(state, action)]
        self.Q[(state, action)] = current_Q + self.alpha*(target - current_Q)
        return self.Q[(state, action)]


class DoubleTDAgent(Agent):
    def __init__(self, new=True):
        super().__init__(new)
        self.Q1 = self.Q
        self.Q2 = Q()
        # black technology
        self.__class__.Q = property(lambda self: self.Q1 + self.Q2)

    def double_update(self, state, action, target, update_Q):
        current_Q = update_Q[(state, action)]
        update_Q[(state, action)] = current_Q + self.alpha * (target - current_Q)
        return update_Q[(state, action)]


@push
class SARSA(TDAgent):
    def __init__(self, new=True):
        super().__init__(new)

    def update_Q(self, state, action, reward, next_state, next_actions):
        next_action = self.epsilon_greedy(next_state, next_actions)
        next_Q = self.Q[(next_state, next_action)]
        target = reward + self.gamma * next_Q
        return self.update(state, action, target)


@push
class ExpectedSARSA(TDAgent):
    def __init__(self, new=True):
        super().__init__(new)

    def update_Q(self, state, action, reward, next_state, next_actions):
        next_a_len = len(next_actions)
        target = 0
        for next_action in next_actions:
            target += self.Q[(next_state, next_action)]
        target = self.gamma * target / next_a_len
        return self.update(state, action, target)


@push
class QLearning(TDAgent):
    def __init__(self, new=True):
        super().__init__(new)
        #self.params = config.get(game_name).get("Q_learning")
        #self.num_episodes = self.params.get('num_episodes')
        #self.min_epsilon = self.params.get("min_epsilon")
        #self.epsilon = self.params.get("epsilon")
        #self.epsilon_decay = self.params.get("epsilon_decay")

    def update_Q(self, state, action, reward, next_state, next_actions):
        for ind, a in enumerate(next_actions):
            if ind == 0:
                max_nQ = self.Q[(next_state, a)]
            else:
                temp_Q = self.Q[(next_state, a)]
                if temp_Q > max_nQ:
                    max_nQ = temp_Q
        target = reward + self.gamma * max_nQ
        self.update(state, action, target)


