from paho.mqtt.client import Client
import json
from board import Pin
import adafruit_dht
import time
from sqlite3 import Cursor, Connection

class Sensor:
    def __init__(self, name):
        self.name = name

    def publishData(self, data: dict, client: Client, topic: str):
        try:
            client.publish(topic=topic, data=json.dumps(data))
        except RuntimeError as error:
            print(f"Sensor error: {error}")

    def sendAlert(self, message: str, client: Client, topic: str):
        try:
            client.publish(topic=topic, payload=message)
        except RuntimeError as error:
            print(f"Alert error: {error}")

    def readData(self, clients: dict[str, Client]=None):
        raise NotImplementedError



class TemperatureSensorDHT22(Sensor):
    def __init__(self, pin: Pin):
        self.sensor = adafruit_dht.DHT22(pin=pin)
        self.cursor = None
        self.conn = None
        self.temperature_readings = []
        self.humidity_readings = []
        self.fan_state = False

    
    def setCursor(self, cursor: Cursor):
        self.cursor = cursor
    
    def setConn(self, conn: Connection):
        self.conn = conn

    def getReading(self) -> dict:
        try:
            temperature = self.sensor.temperature * (9/5) + 32  # Convert to Fahrenheit
            humidity = self.sensor.humidity
            if temperature and humidity:
                return {'temperature' : temperature, 'humidity' : humidity}
            else:
                return {}
        except RuntimeError as error:
            print(f"Sensor {self.name} error: {error}")
            return {}

    # The clients for this should not include those for alerts 
    def readData(self, clients: dict[str, Client]):
        while True:
            try:
                if len(data.keys()) == 2:
                    data = self.getReading()
                    for topic, client in clients.items():
                        self.publishData(data=data, client=client, topic=topic)
                else:
                    print("Sensor failure. Check wiring.")
            except RuntimeError as error:
                print(f"Sensor error: {error}")
            time.sleep(3)

    
    def process_data(self, threshold: int, high_threshold: int, alert_client: Client, alert_topic: str):
        minute_counter = 0
        fan_alert_sent = False

        while True:
            time.sleep(60)  # Wait for one minute
            if self.temperature_readings and self.humidity_readings:
                avg_temp = sum(self.temperature_readings) / len(self.temperature_readings)
                avg_hum = sum(self.humidity_readings) / len(self.humidity_readings)

                # Store in database
                if self.cursor and self.conn:
                    self.cursor.execute("INSERT INTO readings (temperature, humidity) VALUES (?, ?)", (avg_temp, avg_hum))
                    self.conn.commit()

                # Clear lists for next minute
                self.temperature_readings.clear()
                self.humidity_readings.clear()

                minute_counter += 1

                # Every 5 minutes, check thresholds
                if minute_counter >= 5:
                    minute_counter = 0
                    # Retrieve last 5 averages
                    if self.cursor and self.conn:
                        self.cursor.execute("SELECT AVG(temperature), AVG(humidity) FROM readings ORDER BY id DESC LIMIT 5")
                        avg_5min_temp, avg_5min_hum = self.cursor.fetchone()
                        print(f"5-min Avg Temp: {avg_5min_temp:.1f}°F, Humidity: {avg_5min_hum:.1f}%")

                        # Send an alert if temperature exceeds thresholds
                        if avg_5min_temp > threshold and not self.fan_state and not fan_alert_sent:
                            # Send alert via MQTT (Discord bot will pick this up)
                            self.sendAlert(f"High temperature alert: {avg_5min_temp:.1f}°F", alert_client, alert_topic)
                            fan_alert_sent = True
                        elif avg_5min_temp > high_threshold:
                            # Send very high alert
                            self.sendAlert(f"Very high temperature alert: {avg_5min_temp:.1f}°F", alert_client, alert_topic)
                            fan_alert_sent = True
                        elif avg_5min_temp <= threshold:
                            fan_alert_sent = False  # Reset alert flag
            else:
                print("No data collected in the past minute.")

 