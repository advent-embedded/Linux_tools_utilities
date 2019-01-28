import Rpi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.OUT)
while True:
    GPIO.output(3,GPIO.HIGH)
    print "Pin HIGH"
    sleep(3)
    GPIO.output(3,GPIO.LOW)
    print "Pin LOW"
    sleep(3)
