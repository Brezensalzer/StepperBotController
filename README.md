# StepperBotController
Two wheeled rover with stepper motors for precision movement. This is the control center of the project. The whole rover is 
"layered" in three slices:

- the chassis layer: https://github.com/Brezensalzer/StepperBotChassis
- the control layer: https://github.com/Brezensalzer/StepperBotController
- the sensor layer: https://github.com/Brezensalzer/StepperBotLidar2
- the ground station code: https://github.com/Brezensalzer/StepperBotGroundStation

The on-board SBC is a Beaglebone Green Wireless, it runs the mqRpcServer.py script. The script connects to a RabbitMQ Server on a Linux Machine and listens for incoming command messages.
On the Linux box a simple command line client mqRpcClient (nothing fancy, it's a proof of concept) is used to control the rover and to plot the LIDAR scans in map.

<p align="center">
  <img src="./StepperBotController.jpg" width="400"/>
</p>

# Experimental anaglyphic stereo video stream
An ELP stereo usb webcam was added to the StepperBot/Beaglebone. After compiling OpenCV 3.4 on the Beaglebone (takes ca. 10h) it is possible to stream the anaglyphic stereo view as MJPEG to a connected web browser.
This is somewhat pathetic. The Beaglebone runs at 100% CPU load with a 320x240 pixel video stream at 10 fps. But it works!
"Give me all what you have Scotty!" - "I'll try it captain, but I don't think the machine can take it!"
