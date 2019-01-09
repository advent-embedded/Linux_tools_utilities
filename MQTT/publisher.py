import paho.mqtt.publish as publish
 
MQTT_SERVER = "192.168.0.38"
MQTT_PATH = "inTopic"
 
publish.single(MQTT_PATH, "Hello World!", hostname=MQTT_SERVER)

'''
client = mqtt.Client() #create new instance
client.connect(broker_address) #connect to broker
client.publish("house/main-light","OFF")#publish
'''
