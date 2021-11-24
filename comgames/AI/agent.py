import random
import logging
import pathlib

from .Q import Q, EligibilityTrace
from .config import config


base_path = pathlib.Path("comgames/Q")


agent_list = {}
def push(cls):
    agent_list[cls.__name__] = cls
    return cls


class Agent:
    def __init__(self, env, new=False):
        self.logger = logging.getLogger(__name__)
        self.env = env
        self.Q_file = base_path / f"{self.env.game_name}/{self.__class__.__name__}/Q.pkl"
        # Check path existance
        if not self.Q_file.parent.exists():
            self.Q_file.parent.mkdir(parents=True)
        self.initialize_Q_table(new)
        # Parameters
        self.alpha = 0.3
        self.epsilon = 0.1
        self.start_epsilon = 1
        self.epsilon_decay_rank = 10 # Totally 10 steps to decay
        self.epsilon_decay = self.start_epsilon / self.epsilon_decay_rank
        self.current_epsilon = self.start_epsilon
        self.gamma = 0.99

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

    def decayed_epsilon_greedy(self, state, actions, current_episode, total_episodes):
        episode_steps = total_episodes // self.epsilon_decay_rank
        current_rank = current_episode // episode_steps
        current_epsilon = self.start_epsilon - current_rank * self.epsilon_decay
        return self.epsilon_greedy(state, actions, epsilon=current_epsilon)

    def epsilon_greedy(self, state, actions, epsilon=None):
        if epsilon is None:
            epsilon = self.epsilon
        rand = random.random()
        if rand < self.epsilon:
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

    def act(self, board):
        state = self.env.observation()
        actions = self.env.actions(state)
        action = self.greedy(state, actions)
        return action


class TDAgent(Agent):
    def __init__(self, env, new=True):
        super().__init__(env, new)

    def update(self, state, action, target):
        current_Q = self.Q[(state, action)]
        self.Q[(state, action)] = current_Q + self.alpha*(target - current_Q)
        return self.Q[(state, action)]


class DoubleTDAgent(Agent):
    def __init__(self, env, new=True):
        super().__init__(env, new)
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
    def __init__(self, env, new=True):
        super().__init__(env, new)

    def update_Q(self, state, action, reward, done=False, next_state=None, next_actions=None):
        if done:
            target = reward
        else:
            next_action = self.epsilon_greedy(next_state, next_actions)
            next_Q = self.Q[(next_state, next_action)]
            target = reward + self.gamma * next_Q
        return self.update(state, action, target)


@push
class ExpectedSARSA(TDAgent):
    def __init__(self, new=True):
        super().__init__(new)

    def update_Q(self, state, action, reward, done=False, next_state=None, next_actions=None):
        if done:
            target = reward
        else:
            next_a_len = len(next_actions)
            target = 0
            for next_action in next_actions:
                target += self.Q[(next_state, next_action)]
            target = reward + self.gamma * target / next_a_len
        return self.update(state, action, target)


@push
class QLearning(TDAgent):
    def __init__(self, env, new=True):
        super().__init__(env, new)
        #self.params = config.get(game_name).get("Q_learning")
        #self.num_episodes = self.params.get('num_episodes')
        #self.min_epsilon = self.params.get("min_epsilon")
        #self.epsilon = self.params.get("epsilon")
        #self.epsilon_decay = self.params.get("epsilon_decay")

    def update_Q(self, state, action, reward, done=False, next_state=None, next_actions=None):
        if done:
            target = reward
        else:
            for ind, a in enumerate(next_actions):
                if ind == 0:
                    max_nQ = self.Q[(next_state, a)]
                else:
                    temp_Q = self.Q[(next_state, a)]
                    if temp_Q > max_nQ:
                        max_nQ = temp_Q
            target = reward + self.gamma * max_nQ
        self.update(state, action, target)


#@push
#class EligibilityTraceSARSAS(TDAgent):
#    def __init__(self, new=True):
#        super().__init__(new)
#        if new:
#            self.eligibility_trace = EligibilityTrace()
#
#    def update_Q(self, state, action, reward, done=False, next_state=None, next_actions=None):
#        if done:
#            target = reward
#        else:
#            for ind, a in enumerate():
#                
