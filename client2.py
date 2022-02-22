import paho.mqtt.client as mqtt
import socket
s = socket.socket()
from selenium import webdriver
import subprocess
import threading
driver = webdriver.Chrome()

class sub:
    def startScreen():
        subprocess.call(["./automate3.sh"])
        # driver = webdriver.Chrome()
        # driver.get('https://desktop-6k6p7n0/WebRH/container_webrh.html')
        # print(driver.get_cookies())
        # time.sleep(5)
        # driver.find_element_by_id('changeScreen').clear()
        # time.sleep(1)
        # driver.find_element_by_id('changeScreen').send_keys('Screen_2')
        # driver.find_element_by_xpath("//input[@type='button' and @value='go']").click()

    def __init__(self):
        self.client = mqtt.Client('sappu2')

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
      
    def on_subscribe(client, userdata, mid, granted_qos):
        print('achu da')

    def on_message(self, client, userdata, msg):
        print("Client: ", msg.payload.decode())
        #subprocess.call(["./automate3.sh"])
        if(msg.payload.decode() == "Screen 1"):
            driver.get('https://desktop-6k6p7n0/WebRH/container_webrh.html')
            print(driver.get_cookies())
            driver.find_element_by_id('changeScreen').clear()
            driver.find_element_by_id('changeScreen').send_keys('Screen_1')
            driver.find_element_by_xpath("//input[@type='button' and @value='go']").click()
        elif(msg.payload.decode() == "Screen 2"):
            driver.get('https://desktop-6k6p7n0/WebRH/container_webrh.html')
            print(driver.get_cookies())
            driver.find_element_by_id('changeScreen').clear()
            driver.find_element_by_id('changeScreen').send_keys('Screen_2')
            driver.find_element_by_xpath("//input[@type='button' and @value='go']").click()

    def connect(self):
        self.client.connect("localhost", 1883)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.subscribe()

    def subscribe(self):
        relay = 0
        self.client.subscribe('screen', 1)
        while relay == 0:
            self.client.loop()

if __name__ == "__main__":
    s = sub()
    t = threading.Thread(target=s.connect())
    t.start()