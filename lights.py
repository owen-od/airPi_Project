#!/usr/bin/env python

import bme680
import time
from gpiozero import LED
from time import sleep
import presence_detector

# create instance of LED light
red = LED(18)

# create instance of the sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# Oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the sensor data.The higher the oversampling, the greater
# the reduction in noise (with accuracy loss)
sensor.set_temperature_oversample(bme680.OS_8X)
# filter protects against transient changes in conditions
sensor.set_filter(bme680.FILTER_SIZE_3)

# find known devices that are detected on the network to see if user is at home
devices_found = presence_detector.find_devices()
print ("Devices found: ", devices_found)

# Script will run if devices are on network indicating user at home. 
# LED light will turn on if temperature falls below a certain threshold, 
# and the devices are detected on the network, alerting the user to take action.
# If devices no longer on network, light will temporarily turn off. 
if devices_found:
    print("Owen's devices on network - running lights script:")
    try:
        while True:
            # check if devices still on network
            devices_found = presence_detector.find_devices()
            # if not, print message and turn light off
            if not devices_found:
                print("User devices not currently on network")
                red.off()
            else:
            # else if devices on network, and temp below limit, turn light on to alert user and print message
                if sensor.get_sensor_data():
                    if sensor.data.temperature < 17:
                        red.on()
                        output = 'Warning: the temperature is {0:.2f} C'.format(
                            sensor.data.temperature)
                        print(output)
                    # if temp high enough, turn LED off and print message to console
                    else:
                        red.off()
                        print('The temperature is high enough- it is currently {0:.2f} C'.format(
                            sensor.data.temperature) )
            time.sleep(20)
    except KeyboardInterrupt:
        red.off()
        pass
else:
    print("Owen's devices not on network - not running lights script")


