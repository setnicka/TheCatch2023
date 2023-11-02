#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
meow
"""

UNITE = 1
UNITED = 2
meeow = [
  [80, 81],
  [-4, 13],
  [55, 56],
  [133, 134],
  [-8, -7, -5],
  [4, 5],
  [5, 6],
  [6, 7],
  [7, 8],
  [15, -1],
  [11, 12],
  [13, 14],
  [17, 18],
  [18, 19],
  [15, 21],
  [22, 23],
  [26, 27],
  [44, 45],
  [48, 49],
  [31, -29],
  [50, 51],
  [60, 61],
  [72, 73],
  [73, 74],
  [19, 2, 20]]


def meow(kittens_of_the_world):
    """
    meowwwwww meow
    """
    print('meowwww ', end='')
    if kittens_of_the_world < UNITED:
        return kittens_of_the_world
    return meow(kittens_of_the_world - UNITE) + meow(kittens_of_the_world - UNITED)


def meowmeow(meow):
    """
    meow meow meow
    """
    meeoww = ''
    for meoww in meeow:
        print('meowwww ', end='')
        meeoww = f"{meeoww}{chr(int(''.join(str(meow)[m] for m in meoww)))}"
    return meeoww

# MEOF
