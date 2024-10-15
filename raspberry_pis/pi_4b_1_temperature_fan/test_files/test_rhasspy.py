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
import json

load_dotenv()


MOSQUITTO_BROKER=os.getenv('MOSQUITTO_BROKER')
MOSQUITTO_PORT=int(os.getenv('MOSQUITTO_PORT', '1883'))



# On connect subscribe to the Rhasspy intents
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to Mosquitto")
    client.subscribe('hermes/intent/#')

# On message handle the intent
def on_message(client, userdata, msg):
    intent_payload = json.loads(msg.payload.decode('utf-8'))
    intent_name = intent_payload['intent']['intentName']
    slots = {slot['slotName']: slot['value']['value'] for slot in intent_payload.get('slots', [])}
    if intent_name == 'ChangeLightState':
        light_name = slots.get('name')
        print(f"Light in intent was: {light_name}")
        if light_name == 'door lamp':
            print('here')
            RPi4.publishMessage(client=client, topic=HOME_DOOR_LIGHT_POWER, message=slots.get('state').upper())
    print(f"Received intent: {intent_name}")
    print(f"Slots: {slots}")


def main():
   

    pi = RPi4(device_id=1,name="living_room_pi")
    pi.addClient("local_mosquitto", broker=MOSQUITTO_BROKER, port=MOSQUITTO_PORT, on_connect=on_connect, on_message=on_message, tls=False, client_id="")
    pi.startClients()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
