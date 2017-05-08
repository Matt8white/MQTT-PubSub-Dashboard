import paho.mqtt.client as mqtt
import time
import psutil

client = mqtt.Client()
client.connect("localhost", 1883, 60)
start_time = int(time.time())
while int(time.time()) - start_time < 300:  # TODO put this as parameter
    client.publish("topic/cpu", str(psutil.cpu_percent()) + ' ' + str(int(time.time())))
    client.publish("topic/memory", str(psutil.virtual_memory()[2]) + ' ' + str(int(time.time())))
    # client.publish("topic/memory", int(time.time()))
    # client.publish("topic/disk_usage", int(time.time()))
    time.sleep(1)
client.publish("topic/status", "Quit")
client.disconnect()
