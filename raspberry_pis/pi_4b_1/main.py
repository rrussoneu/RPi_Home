# This Pi has the job of being the temperature sensor and turning on or off a fan
# It has a local database as well for storing its data

from dotenv import load_dotenv
import os
import adafruit_dht
import board
import sqlite3
import paho.mqtt.client as paho
from paho import mqtt
import json
import time
import threading

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

# Data lists for storing sensor readings
temperature_readings = []
humidity_readings = []

# Read the data from the sensor every 3 seconds and send real time updates for potential visualization
def read_sensor():
    while True:
        try:
            temperature = dhtDevice.temperature * (9/5) + 32  # Convert to Fahrenheit
            humidity = dhtDevice.humidity
            if temperature and humidity:
                temperature_readings.append(temperature)
                humidity_readings.append(humidity)
                print(f"Temp={temperature:.1f}°F Humidity={humidity:.1f}%")

                # Publish real-time data to MQTT
                data = json.dumps({
                    'temperature': temperature,
                    'humidity': humidity,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                mqtt_client.publish("home/sensor/data", data)
            else:
                print("Sensor failure. Check wiring.")
        except RuntimeError as error:
            print(f"Sensor error: {error}")
        time.sleep(3)


# Store the average data every minute and check thresholds every 5 minutes
def process_data():
    minute_counter = 0
    fan_alert_sent = False

    while True:
        time.sleep(60)  # Wait for one minute
        if temperature_readings and humidity_readings:
            avg_temp = sum(temperature_readings) / len(temperature_readings)
            avg_hum = sum(humidity_readings) / len(humidity_readings)

            # Store in database
            cursor.execute("INSERT INTO readings (temperature, humidity) VALUES (?, ?)", (avg_temp, avg_hum))
            conn.commit()

            # Clear lists for next minute
            temperature_readings.clear()
            humidity_readings.clear()

            minute_counter += 1

            # Every 5 minutes, check thresholds
            if minute_counter >= 5:
                minute_counter = 0
                # Retrieve last 5 averages
                cursor.execute("SELECT AVG(temperature), AVG(humidity) FROM readings ORDER BY id DESC LIMIT 5")
                avg_5min_temp, avg_5min_hum = cursor.fetchone()
                print(f"5-min Avg Temp: {avg_5min_temp:.1f}°F, Humidity: {avg_5min_hum:.1f}%")

                # Send an alert if temperature exceeds thresholds
                if avg_5min_temp > TEMP_THRESHOLD and not FAN_STATE and not fan_alert_sent:
                    # Send alert via MQTT (Discord bot will pick this up)
                    send_alert(f"High temperature alert: {avg_5min_temp:.1f}°F")
                    fan_alert_sent = True
                elif avg_5min_temp > TEMP_HIGH_THRESHOLD:
                    # Send very high alert
                    send_alert(f"Very high temperature alert: {avg_5min_temp:.1f}°F")
                    fan_alert_sent = True
                elif avg_5min_temp <= TEMP_THRESHOLD:
                    fan_alert_sent = False  # Reset alert flag
        else:
            print("No data collected in the past minute.")

# Publish alerts to MQTT
def send_alert(message):
    mqtt_client.publish("home/alerts", message)
    print(f"Alert sent: {message}")

# Start threads
sensor_thread = threading.Thread(target=read_sensor)
sensor_thread.start()

processing_thread = threading.Thread(target=process_data)
processing_thread.start()          