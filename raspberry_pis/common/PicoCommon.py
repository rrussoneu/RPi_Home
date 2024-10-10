from machine import ADC, Pin
import time
from umqtt.simple import MQTTClient

# To Do:
#  - Switch to this MQTT library https://github.com/peterhinch/micropython-mqtt
#  - Add status checking with Tasmota

class PicoW:
    def __init__(
        self, 
        device_id='', 
        name='', 
        mqtt_server='', 
        mqtt_port=1883, 
        mqtt_topic='', 
        wifi_ssid='', 
        wifi_password='', 
        mqtt_callback=None
    ):

        # Unique ID and name, maybe just go to name 
        self.device_id = device_id
        self.name = name

        # MQTT set up
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_client = MQTTClient(self.device_id, self.mqtt_server, self.mqtt_port)

        # Wi-Fi setup
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.wlan = network.WLAN(network.STA_IF)

        self.mqtt_callback = mqtt_callback if mqtt_callback else self.default_mqtt_callback

   
    def connect_to_wifi(self):
            self.wlan.active(True)
            self.wlan.connect(self.wifi_ssid, self.wifi_password)
            while not self.wlan.isconnected():
                print("Connecting to WiFi...")
                time.sleep(1)
            print("Connected to WiFi")

    def connect_to_mqtt(self):
        self.mqtt_client.set_callback(self.mqtt_callback)
        try:
            self.mqtt_client.connect()
            self.mqtt_client.subscribe(self.mqtt_topic)
            print(f"Connected to MQTT broker at {self.mqtt_server}")
        except OSError as e:
            print("Error connecting to MQTT, retrying...")
            self.reconnect_mqtt()

    def default_mqtt_callback(self, topic, msg):
        print(f"Received message on topic {topic}: {msg}")

    def send_mqtt_message(self, message, topic=None):
        if topic is None:
            topic = self.mqtt_topic
        try:
            self.mqtt_client.publish(topic, message)

        except OSError as e:
            print("Error publishing message, attempting to reconnect")
            self.reconnect_mqtt()

    def reconnect_mqtt(self):
        try:
            print("Reconnecting to MQTT...")
            self.mqtt_client.connect()
            self.mqtt_client.subscribe(self.mqtt_topic)
        except OSError as e:
            print("Failed to reconnect, trying again in 5s")
            time.sleep(5)
            self.reconnect_mqtt()
    
    def setup(self):
        self.connect_to_wifi()
        self.connect_to_mqtt()
   

class PicoWLight(PicoW):
    def __init__(
        self, 
        device_id='', 
        name='', 
        server='',
        port=1883,
        topic='', 
        wifi_ssid='', 
        wifi_password='',  
        mqtt_callback=None
    ):
        super().__init__(
            device_id=device_id, 
            name=name, 
            mqtt_server=server, 
            mqtt_port=port, 
            mqtt_topic=topic, 
            wifi_ssid=wifi_ssid, 
            wifi_password=wifi_password, 
            mqtt_callback=mqtt_callback
        )

        self.light_on = False
        
    # Callback for light on vs off
    def mqtt_callback(self, topic, msg):
        if topic == self.mqtt_topic:
            if msg == b'ON' and not self.light_on:
                self.light_on = True
            elif msg == b'OFF' and self.light_on:
                self.light_on = False

class MotionLightPico(PicoWLight):
    def __init__(
        self,
        pir_pin,
        device_id='',
        name='',
        server='',
        port=1883,
        topic='',
        wifi_ssid='PUTHERE',
        wifi_password='PUTHERE',
        mqtt_callback=None,
        cooldown_period=45
    ):
        super().__init__(
            device_id=device_id,
            name=name,
            server=server,
            port=port,
            topic=topic,
            wifi_ssid=wifi_ssid,
            wifi_password=wifi_password,
            mqtt_callback=mqtt_callback
        )
        
        # Initialize the PIR motion sensor
        self.pir = Pin(pir_pin, Pin.IN)
        
        # Cooldown management
        self.cooldown_period = cooldown_period  # In seconds
        self.last_motion_time = 0
        self.in_cooldown = False

    def mqtt_callback(self, topic, msg):
        super().mqtt_callback(topic, msg)


    def run(self):
        """
            Main Loop:
                - Sense motion
                - Turn light on or off
        """
        self.setup()
        print("Starting motion main loop")
        while True:
            current_time = time.time()
            try:
                motion_detected = self.pir.value() == 1
                if motion_detected and not self.in_cooldown:
                    print("Motion detected")
                    self.last_motion_time = current_time
                    if not self.light_on:
                        self.send_mqtt_message("ON")
                        self.light_on = True
                        self.in_cooldown = True
                        print("Light turned ON")
                    else:
                        self.send_mqtt_message("OFF")
                        self.light_on = False
                        self.in_cooldown = True
                        print("Light turned OFF")
                elif self.in_cooldown and (current_time - self.last_motion_time > self.cooldown_period):
                    self.in_cooldown = False
                    print("Cooldown period ended")

                # Check for new MQTT messages
                self.mqtt_client.check_msg()
            except OSError as e:
                print("MQTT connection lost. Attempting to reconnect...")
                self.reconnect_mqtt()

            time.sleep(0.1)  # Small delay to avoid busy loop



class PlantPico(PicoW):
    def __init__(
        self, 
        device_id='', 
        name='', 
        mqtt_server='', 
        mqtt_port=1883, 
        mqtt_topic='', 
        wifi_ssid='', 
        wifi_password=''
    ):
        
        super().__init__(
            device_id=device_id,
            name=name,
            mqtt_server=mqtt_server,
            mqtt_port=mqtt_port,
            mqtt_topic=mqtt_topic,
            wifi_ssid=wifi_ssid,
            wifi_password=wifi_password,
            mqtt_callback=self.mqtt_callback
        )
        
        # Initialize sensor pins, will use the same for each pico
        self.analog_pin = ADC(Pin(26))
        self.power_pin = Pin(21, Pin.OUT)
        self.digital_pin = Pin(22, Pin.IN)
        
        # Alert flag
        self.alert_sent = False
        
        # For averaging readings
        self.readings = []
        self.average_interval = 30 * 60  # 30 minutes in seconds
        self.reading_interval = self.average_interval / 10  # 3 minute wait per reading
        self.last_average_time = time.time()

        # Daily reset for alert
        self.daily_reset_interval = 24 * 60 * 60  # 24 hours in seconds
        self.last_daily_reset = time.time()

    # Sends to brain Pi for database writing
    def send_average_reading(self):
        if len(self.readings) == 0:
            print("No readings")
            return
        
        # Send average reading
        average_analog = sum(self.readings) / len(self.readings)
        message = f"{average_analog:.2f}"
        self.send_mqtt_message(self.mqtt_topic, message)

        # Reset readings
        self.readings = []  

    def run(self):
        """
            Main loop:
                - Sensor reading
                - Reading averaging  
        """
        self.setup()
        while True:
            current_time = time.time()
            
            # Check if it's time to send the average reading
            if current_time - self.last_average_time >= self.average_interval:
                self.send_average_reading()
                self.last_average_time = current_time

            # Check if it's time to reset the alert flag
            if current_time - self.last_daily_reset >= self.daily_reset_interval:
                self.reset_alert_flag()
                self.last_daily_reset = current_time

            # Turn on sensor and wait to stabilize
            self.power_pin.on()
            time.sleep(0.5)

            # Read sensor values
            analog_value = self.analog_pin.read_u16()
            digital_value = self.digital_pin.value()

            # Add to readings for averaging
            self.readings.append(analog_value)
            if len(self.readings) > 10:
                self.readings.pop(0)  # Maintain only the last 10 readings


            # Check if plant needs watering
            if analog_value > 40000 and digital_value == 1 and not self.alert_sent:
                self.send_mqtt_message(self.mqtt_topic, "Water plant!")
                self.alert_sent = True
                print("Alert sent: Water plant!")

            # Turn off sensor to prevent electrolysis
            self.power_pin.off()

            # Wait before the next reading
            time.sleep(self.reading_interval)