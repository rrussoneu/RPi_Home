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

# Topic mappings for communication with bot
local_to_remote_topic = {
    HOME_DOOR_LIGHT_POWER: ('Light: ', BOT_DOOR_LIGHT_ALERT),
}
remote_to_local_topic = {
    BOT_DOOR_LIGHT_CONTROL: ('Light: ', HOME_DOOR_LIGHT_POWER),
    BOT_LIVING_ROOM_FAN_CONTROL: ('Fan: ', HOME_LIVING_ROOM_FAN)
}

non_relay_local_topics = [HOME_LIVING_ROOM_TEMP]

# Set up database
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

last_commands = {
    HOME_DOOR_LIGHT_POWER : 'OFF', 
    HOME_LIVING_ROOM_FAN: 'OFF'
    }


# Callback on Mosquitto message received 
def on_local_message(client, userdata, msg):
    try:

        # Get the Pi class stored in userdata to get the hive client for forwarding
        p = userdata
        hivemq_client = p.getClient('hivemq_client')
        
        topic = msg.topic

        # If message needs to be forwarded to HiveMQ and bot
        if topic in local_to_remote_topic:
            # Topic is stored in tuple[1]
            remote_topic = local_to_remote_topic[topic][1]

            

            # The content of the message remains the same
            payload = msg.payload.decode()
            
            if topic in last_commands.keys():
                last_commands[topic] = payload

            print(f"Local Mosquitto message received: {topic} -> {payload}")

            # Message would look something like 'Light: ON' depending on what is being forwarded
            hivemq_client.publish(remote_topic, f"{local_to_remote_topic[topic][0]}{payload}")
            print(f"Forwarded message: {remote_topic} -> {payload}")
            
        # If it isn't being forwarded, it's a reading to put into the database
        else: 
            

            # Save the reading from the living room temp sensor into database every 60 readings, and store in a list until batch insert
            if topic == HOME_LIVING_ROOM_TEMP:
                
                # Store as a tuple
                table_name = 'temperature_readings'
                data = json.loads(msg.payload.decode())
                temperature = data['temperature']
                humidity = data['humidity']
                timestamp = data['timestamp']
                
                # Insert into the RPi4 class for storage
                p.insertDataToWrite(table_name, (temperature, humidity, timestamp, topic))

                # Do batch insert every 60 readings received - should be once per hour
                if len(p.getDataToWrite) >= 60:
                    try:
                        # Returns a list of tuples
                        data_to_insert = p.getDataToWrite(table_name)

                        conn = sqlite3.connect('local_database.db')
                        cursor = conn.cursor()

                        cursor.executemany(f"""
                            INSERT INTO {table_name} (temperature, humidity, timestamp, source) 
                            VALUES (?, ?, ?, ?)
                            """, data_to_insert)

                        conn.commit()
                        conn.close()

                        # Clear up the list after an insert 
                        p.clearDataToWrite(table_name) 
                    except Exception as e:
                        print(f"Error inserting temperature data: {e}")

            
    except Exception as e:
        print(f"Exception in on_local_message: {e}")

# Callback for when a message is received from the HiveMQ broker
def on_hivemq_message(client, userdata, msg):
    try:
        
        # Get the Pi class stored in userdata to get the local mosquitto client for forwarding
        p = userdata
        local_client = p.getClient('local_mosquitto')

        topic = msg.topic
        payload = msg.payload.decode()
        print(f"HiveMQ message received: {topic} -> {payload}")

        # If message needs to be forwarded to Mosquitto to send a command
        if topic in remote_to_local_topic:
            
            # Get the local topic and forward the message along
            local_topic = remote_to_local_topic[topic][1]

            # If device already in the state the command is trying to achieve (like trying to turn the light on but it's already on)
            if last_commands[local_topic] == payload:
                # Just send a message back
                client.publish(BOT_GENERAL_ALERT, f"Already {payload}")
            
            # Otherwise send the command
            else:
                local_client.publish(local_topic, payload)
            
            # Adjust the most recent command
            last_commands[local_topic] = payload 

            #print(f"Forwarded message to Mosquitto: {local_topic} -> {payload}")

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
