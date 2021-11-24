#import comgames.AI.tictactoeai as ttt
#
#ttt.Q_learning_train()
#ttt.run()
#ttt.run("defensive")
from comgames.__version__ import __version__
import comgames.play.main as m
import argparse

available_games = [
    'fourinarow',
    'Gomoku',
    'tictactoe',
    'Reversi',
]

available_algos = [
    "QLearning",
    "SARSA",
    "ExpectedSARSA",
]

game_list = '\n- '.join([
    '',
    *available_games
])

description = f"Board games: {game_list}"

parser = argparse.ArgumentParser(description=description, prefix_chars='-+')
parser.add_argument('-v', '--version', help='show version', version=__version__, action='version')
parser.add_argument('-g', '--game', help='Game name', choices=available_games, default='tictactoe')
parser.add_argument('--host', help='Host a game online')
parser.add_argument('-p', '--port', help='Port', type=int, default=9999)
parser.add_argument('-c', '--connect', help='Connect to a server, \'host:port\'')
parser.add_argument('--ai', help='Play with AI.', action="store_true")
parser.add_argument('-t', '--train', help='Train an agent.', action="store_true")
parser.add_argument('-a', '--algorithm', help='Specify algorithms', choices=available_algos)
#parser.add_argument('-n', '--new', help='Create a new agent.', action="store_true")

args = parser.parse_args()

#m.main(args)
m.main(args)

