"""Publish Ambience Temperature & Humidityscp 

.. moduleauthor:: Sosaley Technologies <mail@sosaley.in>
   Web:: www.sosaley.in

"""

import Adafruit_DHT
import paho.mqtt.client as mqtt

MQTT_SERVER = "192.168.1.25"
PUB_TOPIC = "hall/ambience"

client = mqtt.Client()
client.connect(MQTT_SERVER, 1883, 60)
client.loop_start()

while True:
  humidity, temperature = Adafruit_DHT.read_retry(11, 4)
  payload = 'Temp={0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)
  client.publish(PUB_TOPIC, payload)
