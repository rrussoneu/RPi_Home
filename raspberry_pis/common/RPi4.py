
from paho.mqtt.client import Client
import paho.mqtt.client as paho
from common.Sensor import Sensor
import ssl

class RPi4:
    def __init__(self, device_id, name):
        self.device_id = device_id # ID for device
        self.name = name # Name for device
        self.sensors = {} # Dict of sensors attached
        self.mqtt_clients = {} # Dictionary of MQTT clients
    
    def addClient(self, client_name, broker, port, on_connect, on_message, tls=True, client_id="", username=None, password=None, protocol=paho.MQTTv5, subscriptions=[]):
        new_client = paho.Client(client_id=client_id, protocol=protocol)
        if tls:
            new_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        if username and password:
            new_client.username_pw_set(username=username, password=password)
        new_client.on_connect=on_connect
        new_client.on_message=on_message
        new_client.connect(broker, port)
        self.mqtt_clients[client_name] = new_client

    def startClients(self):
        for client in self.mqtt_clients.values():
            client.loop_start()

    def getClient(self, name: str) -> Client:
        return self.mqtt_clients[name]

    def sensorRead(self, sensor_name: str, clients: dict[str, Client]):
        self.sensors[sensor_name].readData(clients)

    def addSensor(self, sensor_name: str, sensor: Sensor):
        self.sensors[sensor_name] = sensor

        


        





