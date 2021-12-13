#!/usr/bin/env python

import bme680
import time

import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import sys
import logging
from dotenv import dotenv_values

#load MQTT configuration values from .env file
config = dotenv_values(".env")

#configure Logging
logging.basicConfig(level=logging.INFO)

# Define event callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connection Result: " + str(rc))

def on_publish(client, obj, mid):
    logging.info("Message Sent ID: " + str(mid))

mqttc = mqtt.Client(client_id=config["clientId"])

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# parse mqtt url for connection details
url_str = sys.argv[1]
print(url_str)
url = urlparse(url_str)
base_topic = url.path[1:]

# Configure MQTT client with user name and password
mqttc.username_pw_set(config["username"], config["password"])
# Load CA certificate for Transport Layer Security
mqttc.tls_set("./broker.thingspeak.crt")

#Connect to MQTT Broker
mqttc.connect(url.hostname, url.port)
mqttc.loop_start()

#Set Thingspeak Channel to publish to
topic = "channels/"+config["channelId"]+"/publish"

#create an instance of the sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the sensor data.
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)

#filter protects against transient changes in conditions
sensor.set_filter(bme680.FILTER_SIZE_3)

#enable and change gas measurement settings
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

#publish data to thingspeak using MQQT protocol
print('\n\nPublishing:')
try:
    while True:
        if sensor.get_sensor_data():
            # get temp, humidity and pressure from sensor
            temperature = round(sensor.data.temperature,2)
            humidity = round(sensor.data.humidity,2)    
            pressure = round(sensor.data.pressure,2)
            # add data to payload
            payload=f"field1={temperature}&field2={humidity}&field3={pressure}"

            # if the sensor heat is stable
            if sensor.data.heat_stable:
                #get gas resistance reading
                gas_resistance = round(sensor.data.gas_resistance,2)
                #get air quality reading from file
                with open('airquality.txt') as f:
                    for line in f:
                        pass
                    air_quality = line
                #add data to payload
                payload=f"field1={temperature}&field2={humidity}&field3={pressure}&field4={gas_resistance}&field5={air_quality}"
                #publish data to thingspeak 
                mqttc.publish(topic, payload)

            else:
                #publish data to thingpeak
                mqttc.publish(topic, payload)
        #pause for amount of time specified in .env file
        time.sleep(int(config["transmissionInterval"]))

except KeyboardInterrupt:
    pass
