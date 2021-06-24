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
from service_utils import Service
from picamera import PiCamera
import os
import time

class Photographer(Service):
    """A service used to take photos from the camera and save them to disk."""
    def __init__(self, format, folder):
        super().__init__()
        assert format in ('jpeg', 'bmp', 'png')

        #self._font = ImageFont.truetype(FONT_FILE, size=25) 
        self._format = format
        self._folder = folder

    def _make_filename(self, timestamp, annotated):
        path = '%s/%s_annotated.%s' if annotated else '%s/%s.%s'
        return os.path.expanduser(path % (self._folder, timestamp, self._format))

    def process(self, message):
        camera = message
        timestamp = time.strftime('%Y-%m-%d_%H.%M.%S')

        stream = io.BytesIO()
        camera.capture(stream, format=self._format, use_video_port=True)

        filename = self._make_filename(timestamp, annotated=False)
        stream.seek(0)
        with open(filename, 'wb') as file:
            file.write(stream.read())

    def shoot(self, camera):
        self.submit(camera)

if __name__ == "__main__":
    print("How to save a camera shot")
    with PiCamera(sensor_mode=4, resolution=(820, 616)) as camera:
        
    # camera = stack.enter_context(PiCamera(sensor_mode=4, resolution=(820, 616)))
        with Photographer("jpeg", "/tmp") as photographer:
            for i in range(4):
                photographer.shoot(camera)
                time.sleep(1)

    
