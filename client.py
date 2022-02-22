import paho.mqtt.client as mqtt
import socket
from  main import chat
s = socket.socket()


class sub:
    def __init__(self):
        self.client = mqtt.Client('sappu')

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
      
    def on_subscribe(client, userdata, mid, granted_qos):
        print('achu da')

    def on_message(self, client, userdata, msg):
        # s.connect(('localhost', 5000))
        # s.send(msg.payload.decode())
        print("Client: ", msg.payload.decode())
        return chat(msg.payload.decode())

    def connect(self):
        self.client.connect("localhost", 1883)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.subscribe()

    def subscribe(self):
        relay = 0
        self.client.subscribe('sappu', 1)
        while relay == 0:
            self.client.loop()
