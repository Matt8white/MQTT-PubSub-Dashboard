import paho.mqtt.client as mqtt
import platform
import socket
import time


CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003
DELAY = 1  # secs


# Send messages to graphite
def send_msg(message):
    print('sending to graphite message:\n%s' % message)
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()


# This is the Subscriber
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([("topic/cpu", 0),
                      ("topic/memory", 0),
                      ("topic/disk_usage", 0),
                      ("topic/status", 0)])


def on_message(client, userdata, msg):
    if msg.topic.decode() == "topic/status" and msg.payload.decode() == "Quit":
        client.disconnect()
    message = msg.topic.decode().replace('/', '.') + ' ' + msg.payload.decode() + '\n'
    send_msg(message)


client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
