# Just a simple program ripped off from the examples to
# get started.

import math
import time

from aiy.leds import (Leds, Pattern, PrivacyLed, RgbLeds, Color)
import aiy.toneplayer

def main():
    who_let_the_dogs = [
        'G5q',
        'G5e',
        'G5e',
        'G5q',
        'G5q',
        'B4q',
        're',
        'B4e',
        're',
        'B4e',
        'rs',
        'B4e',
    ]

    player = aiy.toneplayer.TonePlayer(22)
    player.play(*who_let_the_dogs)


if __name__ == '__main__':
    main()