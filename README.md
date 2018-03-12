# Play board games in Linux Command-line

[![PyPI](https://img.shields.io/pypi/pyversions/Django.svg?style=plastic)]()
[![CocoaPods](https://img.shields.io/cocoapods/l/AFNetworking.svg?style=plastic)]()
[![PyPI](https://img.shields.io/pypi/status/Django.svg?style=plastic)]()
[![](https://img.shields.io/badge/version-1.1-ff69b4.svg?style=plastic)]()
[![](https://github.com/houluy/logo/blob/master/Logo.png)]()

## Installation
Use `pip` to install this tool

    pip install comgames


## Usage
Run `comgames` directly to start the game. Then, input the game name to play.  
Or `comgames -g {game}` to play.

Supported game list:  

+ fourinarow
+ Gomoku
+ tictactoe
+ Reversi
+ normal

Normal game allows player to set the size of board and number of winning.

## Version 1.2
Add support for online playing, please refer to `comgames -h` to see the help.

### Server
To host a game, use  

`comgames -g fourinarow --host localhost -p 9876`

### Client
To connect to a server, use  

`comgames -c localhost:9876`

## Full docs
Refer to [here](http://chessboardm.readthedocs.io/en/latest/)
