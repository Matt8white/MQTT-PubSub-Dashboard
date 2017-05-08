import paho.mqtt.client as mqtt
import argparse
import socket

# Input parser
parser = argparse.ArgumentParser()
parser.add_argument('--mqtt_address', type=str, default="localhost")
parser.add_argument('--mqtt_port', type=int, default=1883)
parser.add_argument('--carbon_address', type=str, default="127.0.0.1")
parser.add_argument('--carbon_port', type=int, default=2003)
args = parser.parse_args()

mqtt_address = args.mqtt_address
mqtt_port = args.mqtt_port
carbon_address = args.carbon_address
carbon_port = args.carbon_port


def send_msg(message):
    """
    Sends a properly formatted message to graphite DB
    
    Parameters
    ----------
    message: The message to be sent
    
    Returns
    -------
    Nothing
    """
    print('sending to graphite message:\n%s' % message)
    sock = socket.socket()
    sock.connect((carbon_address, carbon_port))
    sock.sendall(message)
    sock.close()


def on_connect(client, userdata, flags, rc):
    """
    Handles the connection to the message broker

    Parameters
    ----------
    client: The client who wants to connect to the broker
    userdata: The private user data
    flags: Response flags sent by the broker
    rc: The connection result

    Returns
    -------
    Nothing
    """
    print("Connected with result code " + str(rc))
    client.subscribe([("topic/cpu", 0),
                      ("topic/memory", 0),
                      ("topic/disk_usage", 0),
                      ("topic/disk_reads", 0),
                      ("topic/disk_writes", 0),
                      ("topic/status", 0)])


def on_message(client, userdata, msg):
    """
    Handles the received message
    
    Parameters
    ----------
    client: The client who has received the message
    userdata: The private user data
    msg: Content of the message, divided in topic and payload
    
    Returns
    -------
    Nothing
    """
    if msg.topic.decode() == "topic/status" and msg.payload.decode() == "Quit":
        client.disconnect()
    else:
        message = msg.topic.decode().replace('/', '.') + ' ' + msg.payload.decode() + '\n'
        send_msg(message)


# Connecting to MQTT message broker
client = mqtt.Client()
client.connect(mqtt_address, mqtt_port, 60)

# Assigning actions (functions) to events
client.on_connect = on_connect
client.on_message = on_message

# Loops until a "client.disconnect() function is called
client.loop_forever()
