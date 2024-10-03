import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time
import threading

# Load environment variables
load_dotenv()

# Configure both brokers and act as middleman for picos

# HiveMQ configuration
HIVEMQ_BROKER = os.getenv('HIVEMQ_BROKER')        
HIVEMQ_PORT = int(os.getenv('HIVEMQ_PORT', '1883'))
HIVEMQ_USERNAME = os.getenv('HIVEMQ_USERNAME')    
HIVEMQ_PASSWORD = os.getenv('HIVEMQ_PASSWORD')   

# Local Mosquitto configuration - this pi is hosting
MOSQUITTO_BROKER = "localhost"  
MOSQUITTO_PORT = 1883           

# Topic mappings
local_to_remote_topic = {
    'home/door/light': 'discord_bot/door/light/alert',
}
remote_to_local_topic = {
    'discord_bot/door/light/control': 'home/door/light/control',
}

# Define global clients
local_client = None
hivemq_client = None

# Need callbacks for both Mosquitto/ local and HiveMQ

# Callback on Mosquitto message received 
def on_local_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Local Mosquitto message received: {topic} -> {payload}")

    # If message needs to be forwarded to HiveMQ and bot
    if topic in local_to_remote_topic:
        remote_topic = local_to_remote_topic[topic]
        hivemq_client.publish(remote_topic, payload)
        print(f"Forwarded message: {remote_topic} -> {payload}")

# Callback for when a message is received on the HiveMQ broker
def on_hivemq_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"HiveMQ message received: {topic} -> {payload}")

    # If message needs to be forwarded to Mosquitto
    if topic in remote_to_local_topic:
        local_topic = remote_to_local_topic[topic]
        local_client.publish(local_topic, payload)
        print(f"Forwarded message to Mosquitto: {local_topic} -> {payload}")

# Setup MQTT client for local Mosquitto broker
def setup_local_client():
    global local_client
    local_client = mqtt.Client("Mosquitto_Client")
    local_client.on_message = on_local_message

    # Connec
    local_client.connect(MOSQUITTO_BROKER, MOSQUITTO_PORT)
    print("Connected to local Mosquitto broker")

    # Subscribe to the topics to relay from Mosquitto
    for local_topic in local_to_remote_topic.keys():
        local_client.subscribe(local_topic)
        print(f"Subscribed to local Mosquitto topic: {local_topic}")

    # Start the Mosquitto client loop in a separate thread
    local_client.loop_start()

# Setup MQTT client for HiveMQ
def setup_hivemq_client():
    global hivemq_client
    hivemq_client = mqtt.Client("HiveMQ_Client")

    # Set HiveMQ credentials
    hivemq_client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)

    hivemq_client.on_message = on_hivemq_message

    # Connect to HiveMQ broker
    hivemq_client.connect(HIVEMQ_BROKER, HIVEMQ_PORT)
    print("Connected to HiveMQ broker")

    # Subscribe to the topics to relay from HiveMQ
    for remote_topic in remote_to_local_topic.keys():
        hivemq_client.subscribe(remote_topic)
        print(f"Subscribed to HiveMQ topic: {remote_topic}")

    # Start the HiveMQ client loop in a separate thread
    hivemq_client.loop_start()

# Start both MQTT clients in parallel
def start_clients():
    setup_local_client()
    setup_hivemq_client()

    # Keep the main thread alive
    while True:
        time.sleep(1)

# Run the script
if __name__ == "__main__":
    start_clients()
