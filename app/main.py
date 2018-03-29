"""
Main app file
"""

from cpp import maths


def run():
    print('2 + 2 = %d' % maths.add(2, 2))
    print('8 - 6 = %d' % maths.sub(8, 6))
