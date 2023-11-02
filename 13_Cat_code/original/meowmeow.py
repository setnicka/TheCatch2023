#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
meow meow meow
"""


from meow import meow, meowmeow


def meoow():
    """
    meoow
    """
    meoword = ''
    while meoword != 'kittens':
        meoword = input('Who rules the world? ')
        if meoword in ['humans', 'dogs']:
            print('MEOW MEOW!')
    print(meowmeow(meow(sum([ord(meow) for meow in meoword]))))


if __name__ == '__main__':
    meoow()

# MEOF
