from setuptools import setup, find_packages

from codecs import open
from os import path
import src

here = path.abspath(path.dirname(__file__))

setup(
    name='comgames',
    version=src.__version__,
    description='Play games in Linux Command-line with AI',
    url='https://github.com/houluy/comgames',
    author='Houlu',
    author_email='houlu8674@bupt.edu.cn',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='games, command-line',
    install_requires=[
        'chessboardCLI>=1.3.5',
        'colorline>=1.0.3',
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'comgames = src.main:main',
        ],
    }
)
