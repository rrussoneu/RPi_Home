import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time
import threading
from common.topics import *
from common.RPi4 import RPi4
import sqlite3
import json

# Load environment variables
load_dotenv()

# Configure both brokers and act as middleman for picos

# HiveMQ configuration
HIVEMQ_BROKER = os.getenv('MQTT_BROKER')        
HIVEMQ_PORT = int(os.getenv('MQTT_PORT', '1883'))
HIVEMQ_USERNAME = os.getenv('MQTT_USERNAME')    
HIVEMQ_PASSWORD = os.getenv('MQTT_PASSWORD')   

# Local Mosquitto configuration - this pi is hosting
MOSQUITTO_BROKER = "localhost"  
MOSQUITTO_PORT = 1883           

# Topic mappings
local_to_remote_topic = {
    HOME_DOOR_LIGHT_ALERT: BOT_DOOR_LIGHT_ALERT,
}
remote_to_local_topic = {
    BOT_DOOR_LIGHT_CONTROL: HOME_DOOR_LIGHT_POWER
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
conn.close()



# Callback on Mosquitto message received 
def on_local_message(client, userdata, msg):
    try:

        p = userdata
        hivemq_client = p.getClient('hivemq_client')
        topic = msg.topic
        
        conn = sqlite3.connect('local_database.db')
        cursor = conn.cursor()

        # If message needs to be forwarded to HiveMQ and bot
        if topic in local_to_remote_topic:
            remote_topic = local_to_remote_topic[topic]
            payload = msg.payload.decode()
            print(f"Local Mosquitto message received: {topic} -> {payload}")
            hivemq_client.publish(remote_topic, payload)
            print(f"Forwarded message: {remote_topic} -> {payload}")
            if topic == HOME_DOOR_LIGHT_ALERT:
                client.publish(HOME_DOOR_LIGHT_POWER, payload)
        else:
            # Save the reading form the living room temp sensor into database
            if topic == HOME_LIVING_ROOM_TEMP:
                data = json.loads(msg.payload.decode())
                temperature = data['temperature']
                humidity = data['humidity']
                timestamp = data['timestamp']
                cursor.execute("INSERT INTO temperature_readings (temperature, humidity, timestamp, source) VALUES (?, ?, ?, ?)", (temperature, humidity, timestamp, topic))
                conn.commit()
        conn.close()
    except Exception as e:
        print(f"Exception in on_local_message: {e}")

# Callback for when a message is received on the HiveMQ broker
def on_hivemq_message(client, userdata, msg):
    print("AFHDSHAFDSJFJ")
    try:
        p = userdata
        local_client = p.getClient('local_mosquitto')
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"HiveMQ message received: {topic} -> {payload}")

        # If message needs to be forwarded to Mosquitto
        if topic in remote_to_local_topic:
            local_topic = remote_to_local_topic[topic]
            local_client.publish(local_topic, payload)
            print(f"Forwarded message to Mosquitto: {local_topic} -> {payload}")
    except Exception as e:
        print(f"Exception in on_hivemq_message {e}")
# Connection to local broker
def on_local_connect(client, userdata, flags, rc, properties=None):
    try:
        if rc == 0:
            # Subscribe to relay topics
            for local_topic in local_to_remote_topic.keys():
                client.subscribe(local_topic)
                print(f"Subscribed to local topic: {local_topic}")
            
            # Subscribe to non-relay topics
            for local_topic in non_relay_local_topics:
                client.subscribe(local_topic)
                print(f"Subscribed to local topic: {local_topic}")
        else:
            print(f"Failed to connect to Mosquitto MQTT broker, return code {rc}")
    except Exception as e:
        print(f"Exception in on_local_connect: {e}")
# Connection to HiveMQ broker
def on_hivemq_connect(client, userdata, flags, rc, properties=None):
    try:
        if rc == 0:
            # Subscribe to relay topics
            for remote_topic in remote_to_local_topic.keys():
                client.subscribe(remote_topic)
                print(f"Subscribed to HiveMQ topic: {remote_topic}")
                
            # Subscribe to bot fan controls to store the command history in database
            client.subscribe(BOT_LIVING_ROOM_FAN_CONTROL)
            print(f"Subscribed to HiveMQ topic: {BOT_LIVING_ROOM_FAN_CONTROL}")
            
        else:
            print(f"Failed to connect to HiveMQ, return code {rc}")
    except Exception as e:
        print(f"Exception in on_hivemq_connect: {e}")

def main():
    pi = RPi4(device_id=0,name="relay_pi")

    pi.addClient("local_mosquitto", broker=MOSQUITTO_BROKER, port=MOSQUITTO_PORT, on_connect=on_local_connect, on_message=on_local_message, tls=False, client_id="")
    pi.addClient("hivemq_client", broker=HIVEMQ_BROKER, port=HIVEMQ_PORT, on_connect=on_hivemq_connect, on_message=on_hivemq_message, tls=True, client_id="", username=HIVEMQ_USERNAME, password=HIVEMQ_PASSWORD)
    pi.startClients()
    
    while True: # Keep the main thread alive while the clients run on separate ones
        time.sleep(1)


# Run the script
if __name__ == "__main__":
    main()
