from PicoCommon import MotionLightPico

# Init pico and run!
def main():
    motion_light_pico = MotionLightPico(
        device_id="0",
        name="LivingRoomMotionPico",
        server="10.0.0.170",
        port=1883,
        topic="cmnd/home/door/light/POWER",
        wifi_ssid="Your_WiFi_SSID",
        wifi_password="Your_WiFi_Password"
    )
    motion_light_pico.run()

# Run
main()