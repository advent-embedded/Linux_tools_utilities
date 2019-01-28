#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0


# Raspberry Pi hardware SPI configuration.
SPI_PORT   = 0
SPI_DEVICE = 0
sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Loop printing measurements every second.
print 'Press Ctrl-C to quit.'
while True:
	temp = sensor.readTempC()
	payload =  'Thermocouple Temperature: {0:0.3F}°C / {1:0.3F}°F'.format(temp, c_to_f(temp))
        print payload
	time.sleep(0.5)
