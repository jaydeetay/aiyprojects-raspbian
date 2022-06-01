#!/usr/bin/env python3
# Attempt to detect birds in the camera.

import argparse
import contextlib
import io
import logging
import signal
import sys
import threading
import time

from aiy.vision.inference import CameraInference, InferenceEngine
from aiy.leds import Leds, Pattern, Color
from aiy.vision.models import inaturalist_classification

from PIL import Image, ImageDraw

from picamera import PiCamera

from camera_utils import Photographer
from sound_utils import Player, LedAnimator

logger = logging.getLogger(__name__)

#JOY_SCORE_HIGH = 0.85
#JOY_SCORE_LOW = 0.10

WHO_LET_THE_SOUND = (
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
        'B4e',)
BEEP_SOUND = ('E6q', 'C6q')

#FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'

BUZZER_GPIO = 22


@contextlib.contextmanager
def stopwatch(message):
    try:
        logger.info('%s...', message)
        begin = time.monotonic()
        yield
    finally:
        end = time.monotonic()
        logger.info('%s done. (%fs)', message, end - begin)

def run_inference(num_frames, on_loaded, threshold):
    """Yields (faces, (frame_width, frame_height)) tuples."""
    with CameraInference(inaturalist_classification.model(inaturalist_classification.BIRDS)) as inference: # Other options INSECTS and PLANTS
        on_loaded()
        for result in inference.run(num_frames):
            yield inaturalist_classification.get_classes(result, top_k = 1, threshold = threshold)

"""
def threshold_detector(low_threshold, high_threshold):
    Yields 'low', 'high', and None events.
    assert low_threshold < high_threshold

    event = None
    prev_score = 0.0
    while True:
        score = (yield event)
        if score > high_threshold > prev_score:
            event = 'high'
        elif score < low_threshold < prev_score:
            event = 'low'
        else:
            event = None
        prev_score = score


def moving_average(size):
    window = collections.deque(maxlen=size)
    window.append((yield 0.0))
    while True:
        window.append((yield sum(window) / len(window)))


def svg_overlay(faces, frame_size, joy_score):
    width, height = frame_size
    doc = svg.Svg(width=width, height=height)

    for face in faces:
        x, y, w, h = face.bounding_box
        doc.add(svg.Rect(x=int(x), y=int(y), width=int(w), height=int(h), rx=10, ry=10,
                         fill_opacity=0.3 * face.face_score,
                         style='fill:red;stroke:white;stroke-width:4px'))

        doc.add(svg.Text('Joy: %.2f' % face.joy_score, x=x, y=y - 10,
                         fill='red', font_size=30))

    doc.add(svg.Text('Faces: %d Avg. joy: %.2f' % (len(faces), joy_score),
            x=10, y=50, fill='red', font_size=40))
    return str(doc)


 






"""
def bird_detector(num_frames, image_format, image_folder, confidence_threshold, preview_alpha):
    print("Don't forget to sudo systemctl stop joy_detection_demo")
    print("Detecting birds yo")

    done = threading.Event()
    def stop():
        logger.info('Stopping...')
        done.set()

    signal.signal(signal.SIGINT, lambda signum, frame: stop())
    signal.signal(signal.SIGTERM, lambda signum, frame: stop())

    logger.info('Starting services...')
    with contextlib.ExitStack() as stack:
        leds = stack.enter_context(Leds())
        player = stack.enter_context(Player(gpio=BUZZER_GPIO, bpm=60))
        photographer = stack.enter_context(Photographer(image_format, image_folder))
        animator = stack.enter_context(LedAnimator(leds))
        animator.update_confidence(0.0)
        # Forced sensor mode, 1640x1232, full FoV. See:
        # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
        # This is the resolution inference run on.
        # Use half of that for video streaming (820x616).
        camera = stack.enter_context(PiCamera(sensor_mode=4, resolution=(820, 616)))
        #stack.enter_context(PrivacyLed(leds))

        #server = None
        #if enable_streaming:
        #    server = stack.enter_context(StreamingServer(camera, bitrate=streaming_bitrate,
        #                                                 mdns_name=mdns_name))

        def model_loaded():
            logger.info('Model loaded.')
            player.play(WHO_LET_THE_SOUND)

            
        if preview_alpha > 0:
            camera.start_preview(alpha=preview_alpha)

        
        current_bird = None
        for classes in run_inference(num_frames, model_loaded, confidence_threshold):
            if classes and classes[0][0] != 'background':
                name = classes[0][0]
                confidence = classes[0][1]
                animator.update_confidence(confidence)
                if name != current_bird:
                    current_bird = name
                    player.play(BEEP_SOUND)
                    print("I see a '%s' with a confidence of %0.3f" % (name, confidence))
                    photographer.shoot(camera, "%s:%0.2f" % (name[0:20], confidence))
            else:
                animator.update_confidence(0)
                if current_bird:
                    print("I see nothing")
                current_bird = None

            if done.is_set():
                break
        

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--num_frames', '-n', type=int, default=None,
                        help='Number of frames to run for')
    #parser.add_argument('--preview_alpha', '-pa', type=preview_alpha, default=0,
    #                    help='Video preview overlay transparency (0-255)')
    parser.add_argument('--image_format', default='jpeg',
                        choices=('jpeg', 'bmp', 'png'),
                        help='Format of captured images')
    parser.add_argument('--image_folder', default='~/birds',
                        help='Folder to save captured images')
    parser.add_argument('--blink_on_error', default=True, action='store_true',
                        help='Blink red if error occurred')
    parser.add_argument('--confidence_threshold', default=0.6,
                        help='How confident it''s a bird before taking a pic?')
    #parser.add_argument('--enable_streaming', default=False, action='store_true',
    #                    help='Enable streaming server')
    #parser.add_argument('--streaming_bitrate', type=int, default=1000000,
    #                    help='Streaming server video bitrate (kbps)')
    #parser.add_argument('--mdns_name', default='',
    #                    help='Streaming server mDNS name')
    args = parser.parse_args()

    try:
        bird_detector(args.num_frames, args.image_format, args.image_folder, args.confidence_threshold, preview_alpha=200)
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.exception('Exception while running joy demo.')
        if args.blink_on_error:
            with Leds() as leds:
                leds.pattern = Pattern.blink(100)  # 10 Hz
                leds.update(Leds.rgb_pattern(Color.RED))
                time.sleep(1.0)

    return 0

if __name__ == '__main__':
    sys.exit(main())


