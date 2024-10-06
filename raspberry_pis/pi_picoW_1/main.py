import network
import time
import machine
from umqtt.simple import MQTTClient


# MQTT setup
mqtt_server = ""
mqtt_port = 1883  
mqtt_topic_alert = 'local/door_light/alert'
mqtt_topic_control = 'cmnd/home/door/light/POWER'

client_id = "pico_w"



# Wifi connection
ssid = 'PUTHERE'
password = 'PUTHERE'

# Motion sensor
pir = machine.Pin(16, machine.Pin.IN)


# Flags to keep track of the light state and cooldown state
light_on = False
in_cooldown = False


# Cooldown period of 45 seconds
cooldown_period = 45 
last_motion_time = 0  # Timestamp of the last motion detection

# Global MQTT client object
mqtt_client = None

# Connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)

# Publish MQTT message
def send_mqtt_message(topic, message):
    try:
        mqtt_client.publish(topic, message)
    except OSError as e:
        reconnect_mqtt()

# Handle the MQTT messages received 
def mqtt_callback(topic, msg):
    global light_on
    if topic == b'mqtt_topic_control':
        if msg == b'on' and not light_on:
            send_mqtt_message(mqtt_topic_alert, "ON")
            light_on = True
        elif msg == b'off' and light_on:
            send_mqtt_message(mqtt_topic_alert, "OFF")
            light_on = False

# Subscribe to topic for light control
def mqtt_subscribe():
    global mqtt_client
    mqtt_client.set_callback(mqtt_callback)
    try:
        mqtt_client.connect()
        mqtt_client.subscribe(mqtt_topic_control)
    except OSError as e:
        reconnect_mqtt()

# Reconnect to MQTT broker in case of failure
def reconnect_mqtt():
    global mqtt_client
    try:
        mqtt_client.connect()
        mqtt_client.subscribe(mqtt_topic_control)
    except OSError as e:
        time.sleep(5) 

# Main logic for motion detection
def main():
    global mqtt_client, light_on, last_motion_time, in_cooldown
    print("Connecting to wifi")
    # Connect to wifi
    connect_to_wifi()
    print("Connected to wifi")
    
    
    # Set up MQTT client
    mqtt_client = MQTTClient(client_id, mqtt_server, port=mqtt_port, keepalive=60)
    
    # Subscribe to light control topic
    mqtt_subscribe()
    
    on_boot = False
    while True:
        current_time = time.time()
        try:
            if pir.value() == 1 and not in_cooldown:  # Motion detected
                if on_boot == False:
                    on_boot = True
                else:
                    
                    print("Motion detected")
                    last_motion_time = current_time 
                    if not light_on:
                        send_mqtt_message(mqtt_topic_alert, "ON")
                        light_on = True
                        in_cooldown = True
                    
                    elif light_on:
                        send_mqtt_message(mqtt_topic_alert, "OFF")
                        light_on = False
                        in_cooldown = True
    
            elif in_cooldown and (current_time - last_motion_time > cooldown_period):
                in_cooldown = False 
            
            # Check for new MQTT messages
            mqtt_client.check_msg()
        except OSError as e:
            reconnect_mqtt()

        time.sleep(0.1)  # Small delay to avoid busy loop

# Run
main()