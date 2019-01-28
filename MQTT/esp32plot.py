import threading
import time
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import paho.mqtt.client as mqtt

MQTT_SERVER = "192.168.0.38"
MQTT_PATH = "outTopic"


# plot class
class AccelPlot():
    # constr
    def __init__(self, maxLen, server, subsTopic, clientid=None):
        self.ax = deque([0.0] * maxLen)
        self.ay = deque([0.0] * maxLen)
        self.az = deque([0.0] * maxLen)
        self.server = server
        self.subsTopic = subsTopic
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self.receivedMsg = " "
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.maxLen = maxLen

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        pass

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        pass

    def mqtt_on_publish(self, mqttc, obj, mid):
        pass

    def mqtt_on_message(self, mqttc, obj, msg):
        self.receivedMsg = msg.payload
        #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        assert (len(data) == 3)
        self.addToBuf(self.ax, data[0])
        self.addToBuf(self.ay, data[1])
        self.addToBuf(self.az, data[2])

    def run(self):
        self._mqttc.connect(self.server, 1883, 60)
        self._mqttc.subscribe(self.subsTopic, 0)
        rc = 0
        while rc == 0:
            rc = self._mqttc.loop()

    # update plot
    def update(self, frameNum, a0, a1, a2):
        try:
            #line = self.ser.readline()
            data = [float(val) for val in self.receivedMsg.split(",")]
            print data
            if (len(data) == 3):
                self.add(data)
                a0.set_data(range(self.maxLen), self.ax)
                a1.set_data(range(self.maxLen), self.ay)
                a2.set_data(range(self.maxLen), self.az)
        except KeyboardInterrupt:
            print('exiting')

        return a0,

def main():
    # plot parameters
    accelPlot = AccelPlot(maxLen=100, server=MQTT_SERVER,subsTopic=MQTT_PATH)
    #accelPlot.run()
    accelPlot.thread.start()

    print('plotting data...')

    # set up animation
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 100), ylim=(0, 4))
    a0, = ax.plot([], [])
    a1, = ax.plot([], [])
    a2, = ax.plot([], [])
    anim = animation.FuncAnimation(fig, accelPlot.update,
                                   fargs=(a0, a1, a2),
                                   interval=20)

    # show plot
    plt.show()
    print('exiting.')


# call main
if __name__ == '__main__':
    main()
