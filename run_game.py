#!/usr/bin/env python3
"""
Dungeon Crawlr - Run this file to play!
"""
import os
import sys

# Make sure we can find the game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dungeon_crawlr.main import main

if __name__ == '__main__':
    main()
