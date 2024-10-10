import os
from common.RPi4 import RPi4
from common.Sensor import TemperatureSensorDHT22
import board
import sqlite3
import paho.mqtt.client as paho
from paho import mqtt
from common.topics import *
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Env vars
MQTT_BROKER = os.getenv('MQTT_BROKER')           
MQTT_PORT = int(os.getenv('MQTT_PORT', '8883'))  
MQTT_USERNAME = os.getenv('MQTT_USERNAME')    
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')  
MOSQUITTO_BROKER=os.getenv('MOSQUITTO_BROKER')
MOSQUITTO_PORT=int(os.getenv('MOSQUITTO_PORT', '1883'))



# Thresholds for readings
TEMP_THRESHOLD = 60.5  # About 75°F (24 - set low for test)
TEMP_HIGH_THRESHOLD = 80  # About 79°F
HUMIDITY_THRESHOLD = 60.0


# On connect for mosquitto
def on_local_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to Mosquitto MQTT broker")
    else:
        print(f"Failed to connect to Mosquitto MQTT broker, return code {rc}")

# On message for Mosquitto
def on_local_on_message(client, userdata, msg):
    temperature_sensor = userdata  # Get the sensor 
    command = msg.payload.decode()
    print(f"Received command: {command}")
    if command == 'ON':
        with temperature_sensor.lock: # Lock for fan state access across threads
            if not temperature_sensor.fan_state:
                temperature_sensor.fan_state = True
                print("Fan set to on")
            else:
                print("Fan is already ON")
    elif command == 'OFF':
        with temperature_sensor.lock:
            if temperature_sensor.fan_state:
                temperature_sensor.fan_state = False
                print("Fan set to off")
            else:
                print("Fan is already OFF")

# On connect for HiveMQ
def hivemq_on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to HiveMQ MQTT broker")
        client.subscribe(BOT_LIVING_ROOM_FAN_CONTROL)
        print("Subscribed to fan commands")
    else:
        print(f"Failed to connect to HiveMQ MQTT broker, return code {rc}")

# On message for HiveMQ - now the other pi handles the forwarding for simplicity
def hivemq_on_message(client, userdata, msg):
    pass

def main():
        # Database Set Up
    conn = sqlite3.connect('local_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL
    )''')
    conn.commit()


    # Pi/ sensor set up
    pi = RPi4(device_id=1,name="living_room_pi")

    temperature_sensor = TemperatureSensorDHT22(pin=board.D26, name="living_room_dht")
    temperature_sensor.setCursor(cursor=cursor)
    temperature_sensor.setConn(conn=conn)
    pi.addSensor(sensor_name=temperature_sensor.name, sensor=temperature_sensor)
    pi.addClient("local_mosquitto", broker=MOSQUITTO_BROKER, port=MOSQUITTO_PORT, on_connect=on_local_connect, on_message=on_local_on_message, tls=False, client_id="")
    pi.addClient("hivemq_client", broker=MQTT_BROKER, port=MQTT_PORT, on_connect=hivemq_on_connect, on_message=hivemq_on_message, tls=True, client_id="", username=MQTT_USERNAME, password=MQTT_PASSWORD)
    pi.startClients()

    # Set userdata for local client to the sensor
    local_client = pi.getClient('local_mosquitto')
    local_client.user_data_set(temperature_sensor)

    temperature_sensor.run(data_clients={REAL_TIME_LIVING_ROOM_TEMP: pi.getClient('hivemq_client')}, threshold=TEMP_THRESHOLD, high_threshold=TEMP_HIGH_THRESHOLD, alert_client=pi.getClient('local_mosquitto'), alert_topic=HOME_ALERTS, local_client=pi.getClient('local_mosquitto'), local_topic=HOME_LIVING_ROOM_TEMP)
    
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
