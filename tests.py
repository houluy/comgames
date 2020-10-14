import unittest
import tests.test_env

suite = unittest.TestSuite()
suite.addTest(tests.test_env.TestTictactoeEnv("test_observation"))
suite.addTest(tests.test_env.TestFourinarowEnv("test_observation"))
runner = unittest.TextTestRunner()
runner.run(suite)
