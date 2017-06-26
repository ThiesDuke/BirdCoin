from picamera import PiCamera
from time import sleep

camera= PiCamera()
camera.hflip= True
camera.vflip= True
camera.start_preview(alpha=10)
camera.capture('/home/pi/Desktop/image.jpg')
camera.stop_preview()

