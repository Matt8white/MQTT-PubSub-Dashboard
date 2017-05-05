import paho.mqtt.client as mqtt
import psutil
# print psutil.cpu_times()

# This is the Publisher

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish("topic/test", "Hello world!")
client.disconnect()
