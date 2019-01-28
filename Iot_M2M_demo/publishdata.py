"""Publish all Data (Thermocouple Temp, Ambience Temp & Humidity

.. moduleauthor:: Sosaley Technologies <mail@sosaley.in>
   Web:: www.sosaley.in

"""
import time
import sys
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
import paho.mqtt.client as mqtt
 
MQTT_SERVER = "192.168.225.47"
MQTT_TOPIC1 = "boilerplate/temperature"
MQTT_TOPIC2 = "ambience/temperature"
MQTT_TOPIC3 = "ambience/humidity"
INTERVAL=2

SPI_PORT   = 0
SPI_DEVICE = 0
sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

next_reading = time.time() 
client = mqtt.Client()
client.connect(MQTT_SERVER, 1883, 60)
client.loop_start()
try:
	while True:
		temp = sensor.readTempC()
		humidity, temperature = Adafruit_DHT.read_retry(11, 4)
		bTemp = 'Temp={0:0.1F}'.format(temp) 
		aTemp = 'Temp={0:0.1F}' .format(temperature)
		aHumid = 'Humid={0:0.1F}'.format (humidity) 
		print bTemp
		print aTemp
		print aHumid
		client.publish(MQTT_TOPIC1, bTemp)
		client.publish(MQTT_TOPIC2, aTemp)
		client.publish(MQTT_TOPIC3, aHumid)

        	next_reading += INTERVAL
	        sleep_time = next_reading-time.time()
        	if sleep_time > 0:
        	    time.sleep(sleep_time)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
