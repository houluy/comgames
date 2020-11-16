from .agent import agent_list
from .env import Env
import logging


class Trainer:
    def __init__(self, game_name, algo="QLearning"):
        self.env = Env(game_name)
        self.agent = agent_list[algo]()
        self.basic_info = f"{game_name}-{algo}"
        self.logger = logging.getLogger(__name__)
        print(self.basic_info)


