from comgames.AI.env import Env

import unittest

class TestTictactoeEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("tictactoe")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0, 0, 0, 0, 0, 0, 0, 0, 0])

class TestFourinarowEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("fourinarow")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0 for _ in range(7*7)])

