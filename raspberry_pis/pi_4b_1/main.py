# This Pi has the job of being the temperature sensor and turning on or off a fan
# It has a local database as well for storing its data

from dotenv import load_dotenv
import os
import adafruit_dht
import board
import sqlite3
import paho.mqtt.client as paho
from paho import mqtt

load_dotenv()

# Env vars
MQTT_BROKER = os.getenv('MQTT_BROKER')           
MQTT_PORT = int(os.getenv('MQTT_PORT', '8883'))  
MQTT_USERNAME = os.getenv('MQTT_USERNAME')    
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')  

if not MQTT_BROKER:
    raise ValueError("Environment variable 'MQTT_BROKER' is not set or is empty.")

# Validate MQTT_PORT
try:
    MQTT_PORT = int(MQTT_PORT)
except ValueError:
    raise ValueError(f"Invalid MQTT_PORT value: {MQTT_PORT}. It must be an integer.")


# Thresholds for readings
TEMP_THRESHOLD = 70.5  # About 75°F (24 - set low for test)
TEMP_HIGH_THRESHOLD = 80  # About 79°F
HUMIDITY_THRESHOLD = 60.0

# Fan state
FAN_STATE = False

# Init DHT22 sensor for reading temperature and humidity
dhtDevice = adafruit_dht.DHT22(board.D4)

# Database setup
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL
)''')
conn.commit()

# MQTT setup
mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe("home/fan/cmd")
        print("Subscribed to home/fan/cmd")
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")


def on_message(client, userdata, msg):
    global FAN_STATE
    command = msg.payload.decode()
    print(f"Received command: {command}")
    if command == 'turn on':
        if not FAN_STATE:
            FAN_STATE = True
            print("Fan turned ON")
            # Add code to physically turn on the fan when set up !!!!!!!!!!!!!!!!!!!
        else:
            print("Fan is already ON")
    elif command == 'turn off':
        if FAN_STATE:
            FAN_STATE = False
            print("Fan turned OFF")
            # Add code to physically turn off the fan when set up !!!!!!!!!!!!!!!!!
        else:
            print("Fan is already OFF")


mqtt_client.connect(MQTT_BROKER, 8883)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.loop_start()