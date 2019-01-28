#!/usr/bin/python
import threading
import time
from collections import deque

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from Tkinter import *

import paho.mqtt.client as mqtt


MQTT_SERVER = "192.168.43.207"
MQTT_PATH = "outTopic"

'''try:
    from Tkinter import *
    import ttk
except ImportError:
    from tkinter import *
    import tkinter.ttk as ttk
    '''
# plot class
class AccelPlot():
    # constr
    def __init__(self, maxLen, server, subsTopic, mqttCommand, clientid=None):
        self.ax = deque([0.0] * maxLen)
        self.ay = deque([0.0] * maxLen)
        self.az = deque([0.0] * maxLen)
        self.server = server
        self.cmdButton = mqttCommand
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
         
    def mqttStart(self):
        self._mqttc.publish("inTopic", "ON")
        self.cmdButton.configure(text="Stop Strength Test", command = self.mqttStop)

    def mqttStop(self):
        self._mqttc.publish("inTopic", "OFF")
        self.cmdButton.configure(text="Start Strength Test", command = self.mqttStart) 
    def startMic(self):
        pass
    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        print data
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
        
if __name__ == "__main__":
    master = Tk()
    #master.geometry("1200x500")
    #master.geometry("400x300")
    fStrengthval = IntVar(value=100)
    fFinessval = IntVar(value=100)


    titleFrame = LabelFrame(master)
    titleFrame.grid(row=0, column=0,columnspan =4, pady=10,padx=20)

    titleInfo = Label(titleFrame, text="MEMS BASED BUNDLE FIBER AND FIBER FITNESS TESTER",fg="blue", justify =LEFT, font=("Calibri", 20))
    titleInfo.grid(row=0,column=0, padx=10, pady=10)

    graphFrame = LabelFrame(master, background="white")
    graphFrame.grid(row=1, column=0,padx=20, columnspan=3)
    #graphFrame.grid_rowconfigure(0, weight=0, minsize=200)
    #graphFrame.grid_columnconfigure(0, weight=0, minsize=400)
    #graphFrame.grid_columnconfigure(1, weight=1, minsize=400)
    

    Fig = plt.Figure(figsize=(6,6))
    SubPlot = Fig.add_subplot(111,frameon=False) 
    SubPlot.set_xlim([0,100])
    SubPlot.set_ylim([0,3])
    #SubPlot.autoscale(False, tight=False)
    
    canvas = FigureCanvasTkAgg(Fig, master=graphFrame)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)
    plot_widget.configure(height=420, width=700)
    #canvas.draw()
    
    a0, = SubPlot.plot([], [])
    a1, = SubPlot.plot([], [])
    a2, = SubPlot.plot([], [])

    buttonFrame = Frame(master)
    buttonFrame.grid(row=1, column=3, padx=10, pady=1)
    buttonFrame.grid_rowconfigure(0, weight=1, minsize=200)
    buttonFrame.grid_columnconfigure(0, weight=1, minsize=300)

    resultFrame = LabelFrame(master, text="Result", fg="brown", font=("Calibri", 12))
    resultFrame.grid(row=2, column=0, padx=10, columnspan=4)
    resultFrame.grid_columnconfigure(0, weight=0, minsize=400)
    resultFrame.grid_columnconfigure(0, weight=1, minsize=400)
    resultFrame.grid_rowconfigure(0, weight=1, minsize=100)

    startstopMQTT = Button(buttonFrame, text="Start Strength Test", fg="green", font=("Calibri", 12, 'bold'))
    startstopMQTT.grid(row=0, column =0,pady=10)

    startMic = Button(buttonFrame, text="Start Mic Testing", fg="green", font=("Calibri", 12,'bold'))
    startMic.grid(row=1, column =0,pady=10)

    labelStat = Label(resultFrame, text="Statistics", font=("Calibri", 14, 'bold'), fg="brown")
    labelStat.grid(row=1, column =0,sticky=W,pady=5)
    labelFStrength = Label(resultFrame, text="Bundle Fiber Strength",fg="brown", font=("Calibri", 12, 'bold'))
    labelFStrength.grid(row=0, column =1,padx=40, sticky=W)
    labelFFMic = Label(resultFrame, text="Fiber Fineness (Mic)",fg="brown", font=("Calibri", 12, 'bold'))
    labelFFMic.grid(row=2, column =1,padx=40,pady=10, sticky=W)

    valFStrength = Label(resultFrame, textvariable=fStrengthval,fg="brown", font=("Calibri", 12, 'bold'))
    valFFiness = Label(resultFrame, textvariable=fFinessval,fg="brown", font=("Calibri", 12, 'bold'))
    valFStrength.grid(row=0, column=2, sticky=W)
    valFFiness.grid(row=2, column=2, sticky=W)
    
    accelPlot = AccelPlot(maxLen=100, server=MQTT_SERVER,subsTopic=MQTT_PATH, mqttCommand=startstopMQTT)
    startstopMQTT.configure(command=accelPlot.mqttStart)
    startMic.configure(command=accelPlot.startMic)
    accelPlot.thread.start()
    
    anim = animation.FuncAnimation(Fig, accelPlot.update,fargs=(a0, a1, a2), interval=20)



    master.mainloop()
	
