# A Bird Detector

Building on the provided bird classifier to automatically photograph
and upload pictures of birds.

First version is just me messing about with the APIs.

## Setting up your development environment.

It's highly recommended to not develop on the Pi Zero itself, which
is a little underpowered for the task. Instead, ssh into it from another
machine for your everyday commandline work. For example, if you haven't changed the defaults:
    
    ssh pi@raspberrypi

(password `raspberry`).

## Running the detector

If you haven't already, shut down any existing demos on the raspberry pi.  Something like:

    sudo systemctl stop joy_detection_demo
    
You can then run the demo with:

    ./live_bird_detector.py
    
If you get complaints about lack of resources related to the camera it's likely that you haven't stopped the joy demo or something has a lock on it.  You can run

    python3 reset_stuck_camera.py
    
to fix it.

## APIs

The APIs are documented here https://aiyprojects.readthedocs.io/en/latest/.


