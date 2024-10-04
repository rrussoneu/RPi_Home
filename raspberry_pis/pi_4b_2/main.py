import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time
import threading
from ..common.topics import *
from ..common.RPi4 import RPi4
import sqlite3
import json

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
    HOME_DOOR_LIGHT: BOT_DOOR_LIGHT_ALERT,
}
remote_to_local_topic = {
    BOT_DOOR_LIGHT_CONTROL: HOME_DOOR_LIGHT_CONTROL
}

non_relay_local_topics = [HOME_LIVING_ROOM_TEMP]

conn = sqlite3.connect('local_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS temperature_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    source TEXT
)''')
conn.commit()

pi = RPi4(device_id=0,name="relay_pi")

# Callback on Mosquitto message received 
def on_local_message(client, userdata, msg):
    topic = msg.topic
    print(f"Local Mosquitto message received: {topic} -> {payload}")

    # If message needs to be forwarded to HiveMQ and bot
    if topic in local_to_remote_topic:
        remote_topic = local_to_remote_topic[topic]
        payload = msg.payload.decode()
        hivemq_client.publish(remote_topic, payload)
        print(f"Forwarded message: {remote_topic} -> {payload}")
    else:
        # Save the reading form the living room temp sensor into database
        if topic == HOME_LIVING_ROOM_TEMP:
            data = json.loads(msg.payload.decode())
            temperature = data['temperature']
            humidity = data['humidity']
            timestamp = data['timestamp']
            cursor.execute("INSERT INTO temperature_readings (temperature, humidity, timestamp, source) VALUES (?, ?, ?, ?)", (temperature, humidity, timestamp, topic))


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

# Connection to local broker
def on_local_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        # Subscribe to relay topics
        for local_topic in local_to_remote_topic.keys():
            client.subscribe(local_topic)
        
        # Subscribe to non-relay topics
        for local_topic in non_relay_local_topics:
            client.subscribe(local_topic)
    else:
        print(f"Failed to connect to Mosquitto MQTT broker, return code {rc}")

# Connection to HiveMQ broker
def on_hivemq_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        # Subscribe to relay topics
        for remote_topic in remote_to_local_topic.keys():
            hivemq_client.subscribe(remote_topic)
            print(f"Subscribed to HiveMQ topic: {remote_topic}")
            
        # Subscribe to bot fan controls to store the command history in database
        hivemq_client.subscribe(BOT_LIVING_ROOM_FAN_CONTROL)
        # Subscribe to other Pi's temperature readings to store in database
        hivemq_client.subscribe(HOME_LIVING_ROOM_TEMP)
    else:
        print(f"Failed to connect to HiveMQ, return code {rc}")


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

    # Subscribe to the topics to relay from HiveMQ to Picos
    for remote_topic in remote_to_local_topic.keys():
        hivemq_client.subscribe(remote_topic)
        print(f"Subscribed to HiveMQ topic: {remote_topic}")
        
    # Subscribe to bot fan controls to store the command history in database
    hivemq_client.subscribe(BOT_LIVING_ROOM_FAN_CONTROL)
    # Subscribe to other Pi's temperature readings to store in database
    hivemq_client.subscribe(HOME_LIVING_ROOM_TEMP)

    # Start the HiveMQ client loop in a separate thread
    hivemq_client.loop_start()

pi.addClient("local_mosquitto", broker=MOSQUITTO_BROKER, port=MOSQUITTO_PORT, on_connect=on_local_connect, on_message=on_local_message, tls=False, client_id="Mosquitto_Client")
pi.addClient("hivemq_client", broker=HIVEMQ_BROKER, port=HIVEMQ_PORT, on_connect=on_hivemq_connect, on_message=on_hivemq_message, tls=True, client_id="HiveMQ_Client", username=HIVEMQ_USERNAME, password=HIVEMQ_PASSWORD)

def main():
    pi.startClients()
    while True: # Keep the main thread alive while the clients run on separate ones
        time.sleep(1)


# Run the script
if __name__ == "__main__":
    main()
