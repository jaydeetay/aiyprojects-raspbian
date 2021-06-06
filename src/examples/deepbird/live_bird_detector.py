#!/usr/bin/env python3
# Attempt to detect birds in the camera.

import io

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection

from PIL import Image, ImageDraw

from picamera import PiCamera


def main():
    pic_cnt = 0
    with PiCamera() as camera:
        # Configure camera
        camera.resolution = (1640, 922)  # Full Frame, 16:9 (Camera v2)
        camera.start_preview()
        print("Running")

        # Do inference on VisionBonnet
        with CameraInference(face_detection.model()) as inference:
            for result in inference.run():
                faces = face_detection.get_faces(result)
                if len(faces) >= 1:
                    print("Found %d faces!" % len(faces))
                    stream = io.BytesIO()
                    camera.capture(stream, format='jpeg')
                    stream.seek(0)
                    image = Image.open(stream)
                    drawer = ImageDraw.Draw(image)
                    for face in faces:
                        bb = face.bounding_box
                        print("Bounding box:", bb)
                        x, y, w, h = bb # This might need rescaling
                        drawer.rectangle((x, y, x + w, y + h))
                    image.save("face%d.jpg" % pic_cnt)
                    pic_cnt = pic_cnt + 1

        # Stop preview
        camera.stop_preview()


if __name__ == '__main__':
  main()


