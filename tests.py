#import unittest
#import tests.test_env
#
#suite = unittest.TestSuite()
#suite.addTest(tests.test_env.TestTictactoeEnv("test_observation"))
#suite.addTest(tests.test_env.TestTictactoeEnv("test_actions"))
#suite.addTest(tests.test_env.TestTictactoeEnv("test_step"))
#suite.addTest(tests.test_env.TestFourinarowEnv("test_observation"))
#suite.addTest(tests.test_env.TestFourinarowEnv("test_actions"))
#suite.addTest(tests.test_env.TestFourinarowEnv("test_step"))
#runner = unittest.TextTestRunner()
#runner.run(suite)

from src.AI.train import Trainer

train = Trainer("tictactoe")

