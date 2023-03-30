import os
import sys

cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, cur_path + "/..")
from src.commands import bot

if __name__ == '__main__':
    bot()
