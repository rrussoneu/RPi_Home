from machine import ADC, Pin
import time
from umqtt.simple import MQTTClient
from PicoCommon import PlantPico

# Init plant pico and run!
def main():
    pico = PlantPico(
        device_id="p2",
        name="PlantPico1",
        mqtt_server='10.0.0.170',
        mqtt_port=1883,
        mqtt_topic="home/bonsai/alert",
        wifi_ssid='wifihere',
        wifi_password='wifihere'
    )
    pico.run()

if __name__ == "__main__":
    main()


