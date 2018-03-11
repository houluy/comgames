from colorline import cprint
from functools import partial

MAX_LENGTH = 50

eprint = partial(cprint, color='r', bcolor='c', mode='highlight')
input_print = partial(cprint, color='g', bcolor='k', end='')
nprint = partial(cprint, color='r', bcolor='b')

