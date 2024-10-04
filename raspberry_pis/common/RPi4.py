
import paho.mqtt.client as paho
from paho import Client, mqtt
from Sensor import Sensor

class RPi4:
    def __init__(self, device_id, name):
        self.device_id = device_id # ID for device
        self.name = name # Name for device
        self.sensors = {} # Dict of sensors attached
        self.mqtt_clients = {} # Dictionary of MQTT clients
    
    def addClient(self, client_name, broker, port, on_connect, on_message, tls=True, client_id="", username=None, password=None, protocol=paho.MQTTv5, subscriptions=[]):
        self.new_client = paho.Client(client_id=client_id, protocol=protocol)
        if tls:
            self.new_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        if username and password:
            self.new_client.username_pw_set(username=username, password=password)
        self.new_client.on_connect=on_connect
        self.new_client.on_message=on_message
        self.new_client.connect(broker, port)
        self.mqtt_clients[client_name] = self.new_client

    def startClients(self):
        for client in self.mqtt_clients:
            client.loop_start()

    def addSensor(self, sensor: Sensor, name: str):
        self.sensors[name] = sensor
    
    def sensorReadContinuous(self, sensor_name: str):
        pass

    def sensorRead(self, sensor_name: str, clients: dict[str, Client]):
        self.sensors[sensor_name].readData(clients)

        


        





