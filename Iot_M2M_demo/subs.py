"""Subscribes to  'ambience/temperature' and controls GPIO Ex. Relay

.. moduleauthor:: Sosaley Technologies <mail@sosaley.in>
   Web:: www.sosaley.in

"""
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

MQTT_SERVER = "192.168.1.25"
SUBS_TOPIC = "ambience/temperature"
PUB_TOPIC = "response/relay"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(SUBS_TOPIC)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    receivedStr = str(msg.payload)
    val = receivedStr.split("=",1)[1] 
    data = float(val)
    print data
    if data < 23.0:
      GPIO.output(3,GPIO.HIGH)
      client.publish(PUB_TOPIC,"Realy Triggered") 
    else:
      GPIO.output(3,GPIO.HIGH)
    # more callbacks, etc
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
 

client.loop_forever()
