# RPi_Home: DIY Smart Home Automation

## Welcome!

Thanks for checking out my smart home project! This project can transform your apartment into a smart home using a few types of Raspberry Pi's and various IoT devices.

## Overview 

### Background
For a little background, this project began as a way to just turn on a fan when it got hot. I wanted to get a notifcation when it got too hot at home when I was out and a way to turn on a fan to help lower the temperature for my dog while I'm not home. I had a Raspberry Pi sitting around, so I attached a temperature sensor, and then made a Discord bot to alert me. I deployed the bot on Heroku and used HiveMQ for an MQTT broker. Next, I bought a Sonoff R2, soldered on some headers, flashed it with Tasmota, attached a box fan, set up a local Mosquitto server for MQTT communication between the R2 and Raspberry Pi, looped in some commands to the bot, and I had my working pipeline. 

After getting my original idea set up, I got working on, and am actively adding pieces to, other components to turn my apartment into a DIY smart home. I currently have one Raspberry Pi 4b that hosts the local Mosquitto server and handles the commands from the Discord bot, and it also has a local SQLite database to back up data readings. I have a second Pi 4b that does the temperature readings and is allowed to send alerts to the Discord bot directly, while also storing its data in a local SQLite database and sending it to the brain Pi for backup storage. Right now, a Pico W is also set up with a motion sensor by my door to turn on a lamp connected to a Sonoff R2 when I get home and when I leave. The lamp is also commandable from the bot. 

Stay tuned for additional functionalities added, and feel free to use this code base for your own smart home. The common code is separated out and shared amongst the devices, allowing for easy reuse betwen devices. Next up includes some code for a Pico connected to a moisture sensor for plant watering alert, adding a main application/ home dashboard for my computer, and using a hosted database for a central source of data and API for the computer app to interface with.

If you have any ideas for further expansions or improvements, please let me know!