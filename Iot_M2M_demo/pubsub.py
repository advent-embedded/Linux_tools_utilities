"""Publishes all Data (Thermocouple Temp, Ambience Temp & Humidity and Subscribes for response/#

.. moduleauthor:: Sosaley Technologies <mail@sosaley.in>
   Web:: www.sosaley.in

"""
import time
import sys
import threading
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
import paho.mqtt.client as mqtt
 
MQTT_SERVER = "192.168.1.25"
MQTT_TOPIC1 = "boilerplate/temperature"
MQTT_TOPIC2 = "ambience/temperature"
MQTT_TOPIC3 = "ambience/humidity"
MQTT_SUBS = "response/#"
INTERVAL=2

SPI_PORT   = 0
SPI_DEVICE = 0


class myMQTT():
    # constr
    def __init__(self, server, subsTopic, clientid="dataSource"):
        self.server = server
        self.subsTopic = subsTopic
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self.receivedMsg = " "
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        pass

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        pass

    def mqtt_on_publish(self, mqttc, obj, mid):
        pass

    def mqtt_on_message(self, mqttc, obj, msg):
        self.receivedMsg = msg.payload
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def run(self):
        self._mqttc.connect(self.server, 1883, 60)
        self._mqttc.subscribe(self.subsTopic, 0)
        rc = 0
        while rc == 0:
            rc = self._mqttc.loop()

def main():
    # plot parameters
    mqtt = myMQTT(server=MQTT_SERVER,subsTopic=MQTT_SUBS)
    sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
    #accelPlot.run()
    mqtt.thread.start()
    next_reading = time.time() 
    try:
	    while True:
            	    temp = sensor.readTempC()
		    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
		    bTemp = 'Temp={0:0.1f}'.format(temp)
		    aTemp = 'Temp={0:0.1f}' .format(temperature)
		    aHumid = 'Humid={0:0.1f}'.format (humidity)
		    print bTemp
		    print aTemp
		    print aHumid
		    mqtt._mqttc.publish(MQTT_TOPIC1, bTemp)
		    mqtt._mqttc.publish(MQTT_TOPIC2, aTemp)
		    mqtt._mqttc.publish(MQTT_TOPIC3, aHumid)

            next_reading += INTERVAL
	    sleep_time = next_reading-time.time()
            if sleep_time > 0:
        	    time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass

    client.loop_stop()
    client.disconnect()
if __name__ == '__main__':
	main()
