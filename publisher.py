import paho.mqtt.client as mqtt
import numpy as np
import argparse
import time
import psutil

# Input parser
parser = argparse.ArgumentParser()
parser.add_argument('--mqtt_address', type=str, default="localhost")
parser.add_argument('--mqtt_port', type=int, default=1883)
parser.add_argument('--run_time', type=int, default=0)
args = parser.parse_args()

mqtt_address = args.mqtt_address
mqtt_port = args.mqtt_port
run_time = args.run_time
# If no run_time is defined the script will run forever
if run_time == 0:
    run_time = np.inf
    
# Connecting to MQTT message broker
client = mqtt.Client()
client.connect(mqtt_address, mqtt_port, 60)

start_time = int(time.time())
while int(time.time()) - start_time < run_time:
    client.publish("topic/cpu", str(psutil.cpu_percent()) + ' ' + str(int(time.time())))
    client.publish("topic/memory", str(psutil.virtual_memory()[2]) + ' ' + str(int(time.time())))
    client.publish("topic/disk_usage", str(psutil.disk_usage('/')[3]) + ' ' + str(int(time.time())))
    client.publish("topic/disk_reads", str(psutil.disk_io_counters()[0]) + ' ' + str(int(time.time())))
    client.publish("topic/disk_writes", str(psutil.disk_io_counters()[1]) + ' ' + str(int(time.time())))
    time.sleep(1)

# Shut all the listening subscribers and disconnects itself
client.publish("topic/status", "Quit")
client.disconnect()
