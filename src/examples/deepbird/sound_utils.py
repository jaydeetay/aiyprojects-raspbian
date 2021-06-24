#!/usr/bin/env python3
# Copyright 2021 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Heavily inspired, even copied from the utilities used to build the
# Joy Detection Demo.

import io
import logging
from service_utils import Service
from aiy.leds import Leds, Color
from aiy.toneplayer import TonePlayer
import os
import time

logger = logging.getLogger(__name__)

class Player(Service):
    """Controls buzzer."""

    def __init__(self, gpio, bpm):
        super().__init__()
        self._toneplayer = TonePlayer(gpio, bpm)

    def process(self, sound):
        try:
            self._toneplayer.play(*sound)
        except:
            logger.exception('Cannot play %s sound', sound)

    def play(self, sound):
        self.submit(sound)

HIGH_COLOR = (0, 255, 0)
LOW_COLOR = (0, 0, 64)

class LedAnimator(Service):
    """Controls RGB LEDs."""

    def __init__(self, leds):
        super().__init__()
        self._leds = leds

    def process(self, confidence):
        if confidence > 0:
            self._leds.update(Leds.rgb_on(Color.blend(HIGH_COLOR, LOW_COLOR, confidence)))
        else:
            self._leds.update(Leds.rgb_off())

    def shutdown(self):
        self._leds.update(Leds.rgb_off())

    def update_confidence(self, confidence):
        self.submit(confidence)

if __name__ == "__main__":
    print("How to play a sound")
        
    with Player(22, 60) as player, LedAnimator(Leds()) as leds:
        player.play(('C5q', 'E5q', 'C6q'))
        leds.update_confidence(0.5)

    
