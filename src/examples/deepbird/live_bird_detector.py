#!/usr/bin/env python3
# Attempt to detect birds in the camera.

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection

from picamera import PiCamera


def main():
    with PiCamera() as camera:
        # Configure camera
        camera.resolution = (1640, 922)  # Full Frame, 16:9 (Camera v2)
        camera.start_preview()

        # Do inference on VisionBonnet
        with CameraInference(face_detection.model()) as inference:
            for result in inference.run():
                if len(face_detection.get_faces(result)) >= 1:
                    print("Found %d faces!", len(face_detection.get_faces(result)))
                    camera.capture('faces.jpg')
                    break

        # Stop preview
        camera.stop_preview()


if __name__ == '__main__':
  main()


