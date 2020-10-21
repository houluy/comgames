from comgames.AI.env import Env

import unittest

class TestTictactoeEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("tictactoe")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_actions(self):
        test_state = [1, 2, 0, 1, 2, 0, 1, 2, 0]
        actions = self.env.actions(test_state)
        self.assertEqual(actions, [
            (0, 2), (1, 2), (2, 2)
        ])


class TestFourinarowEnv(unittest.TestCase):
    def setUp(self):
        self.env = Env("fourinarow")

    def test_observation(self):
        observation = self.env.observation()
        self.assertEqual(observation, [0 for _ in range(7*7)])

    def test_actions(self):
        test_state = [0 for _ in range(7*7)]
        actions = self.env.actions(test_state)
        self.assertEqual(actions, [
            i for i in range(7)
        ])
        test_state[0] = 1
        self.assertEqual(self.env.actions(test_state), [i for i in range(1, 7)])
        test_state[1] = 1
        self.assertEqual(self.env.actions(test_state), [i for i in range(2, 7)])
        test_state[2:7] = [1 for _ in range(7 - 2)]
        self.assertEqual(self.env.actions(test_state), [])

    def test_step(self):
        test_state = [0 for _ in range(7*7)]
        actions = self.env.actions(test_state)
        action = actions[0]
        state, reward, done, info = self.env.step(action)
        assert_state = test_state[:]
        assert_state[-7] = 1
        self.assertEqual(state, assert_state)
        self.assertEqual(reward, 0)
        self.assertEqual(done, False)
        # Move to target environment
        self.env.step(1)
        self.env.step(2)
        self.env.step(2)
        self.env.step(3)
        state, reward, done, info = self.env.step(3)
        assert_state = test_state[:]
        assert_state[-7:-3] = [1, 2, 1, 1]
        assert_state[-12:-10] = [2, 2]
        self.assertEqual(state, assert_state)
        # Test win
        self.env.step(2)
        self.env.step(0)
        self.env.step(2)
        state, reward, done, info = self.env.step(1)
        self.assertEqual(done, 1)
        self.assertEqual(reward, 100)

