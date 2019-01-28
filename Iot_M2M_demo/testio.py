import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(16, GPIO.OUT)
echo none >/sys/class/LEDs/led0/trigger
while True:
	print "B..."
	GPIO.output(16, GPIO.LOW) #dah
	sleep(3)
	GPIO.output(16, GPIO.HIGH)
	sleep(1)
	GPIO.output(16, GPIO.LOW) #dit
	sleep(1)
	GPIO.output(16, GPIO.HIGH)
	sleep(1)
	GPIO.output(16, GPIO.LOW) #dit
	sleep(1)
	GPIO.output(16, GPIO.HIGH)
	sleep(1)
	GPIO.output(16, GPIO.LOW) #dit
	sleep(1)
	GPIO.output(16, GPIO.HIGH) 
