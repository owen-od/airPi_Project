#!/usr/bin/python3

from flask import Flask, request, render_template
from flask_cors import CORS
import json
import netatmo
import bme680
import requests
from dotenv import dotenv_values

#load configuration values from .env file
config = dotenv_values(".env")

# create Flask app instance and apply CORS
app = Flask(__name__)
CORS(app)

#create an instance of the BME680 sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

#create instance of netatmo weather station using credentials in .env file
ws = netatmo.WeatherStation({
    'client_id': config["net_client_id"],
    'client_secret': config["net_client_secret"],
    'username': config["net_username"],
    'password': config["net_password"],
    'device': config["net_device"]})

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data. The higher to oversampling, the greater
#the reduction in noise (with accuracy loss)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)

#filter protects against transient changes in conditions
sensor.set_filter(bme680.FILTER_SIZE_3)

# This route will render the status.html page containing a summary of the data and the different routes
@app.route('/')
def index():
    # get latest data from Netatmo devices
    ws.get_data()
    data = ws.devices
    # get temperature data from Netatmo devices and BME680 sensor and assign to variables
    bedroomTemp = data[0]['dashboard_data']['Temperature']
    balconyTemp = data[0]["modules"][0]['dashboard_data']['Temperature']
    officeTemp = round(sensor.data.temperature, 2)
    # get humidity data from Netatmo devices and BME680 sensor and assign to variables
    bedroomHumidity = data[0]['dashboard_data']['Humidity']
    balconyHumidity = data[0]["modules"][0]['dashboard_data']['Humidity']
    officeHumidity = round(sensor.data.humidity, 2)
    # get pressure data from Netatmo devices and BME680 sensor and assign to variables
    bedroomPressure = data[0]['dashboard_data']['Pressure']
    officePressure = round(sensor.data.pressure, 2)
    # get CO2 data from Netatmo device and assign to variable
    bedroomCO2 = data[0]['dashboard_data']['CO2']
    # render status.html page to display data
    return render_template('status.html', officeTemp=officeTemp, bedroomTemp=bedroomTemp, balconyTemp=balconyTemp,
     officeHumidity=officeHumidity, bedroomHumidity=bedroomHumidity, balconyHumidity=balconyHumidity,
      bedroomCO2=bedroomCO2, officePressure=officePressure, bedroomPressure=bedroomPressure)

# This route uses the BME680 sensor to get readings from the AirPi in the office
@app.route('/home/office', methods=['GET'])
def office_environment():
    temperature = round(sensor.data.temperature, 2)
    humidity = round(sensor.data.humidity, 2)
    pressure = round(sensor.data.pressure, 2)
    msg = json.dumps({"temperature": temperature,
                     "humidity": humidity, "pressure": pressure})
    return str(msg)+"\n"

# This route uses the Netatmo indoor moudule to get readings from the bedroom 
@app.route('/home/bedroom', methods=['GET'])
def room_environment():
    ws.get_data()
    data = ws.devices
    temperature = data[0]['dashboard_data']['Temperature']
    humidity = data[0]['dashboard_data']['Humidity']
    pressure = data[0]['dashboard_data']['Pressure']
    CO2 = data[0]['dashboard_data']['CO2']
    msg = json.dumps({"temperature": temperature,
                     "humidity": humidity, "pressure": pressure, "CO2": CO2})
    return str(msg)+"\n"

# This route uses the Netatmo outdoor module to get readings from the balcony
@app.route('/home/balcony', methods=['GET'])
def balcony_environment():
    ws.get_data()
    data = ws.devices
    temperature = data[0]["modules"][0]['dashboard_data']['Temperature']
    humidity = data[0]["modules"][0]['dashboard_data']['Humidity']
    msg = json.dumps({"temperature": temperature, "humidity": humidity})
    return str(msg)+"\n"

# This route uses openweathermap api to get weather data for the latitude and longitude indicated (set to local area) 
@app.route('/home/city', methods=['GET'])
def city_environment():
    api_key = config["ow_api_key"]
    lat = "53.347"
    lon = "-6.285"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (
        lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    weather = data["current"]["weather"][0]["main"]
    temp = data["current"]["temp"]
    pressure = data["current"]["pressure"]
    humidity = data["current"]["humidity"]
    wind_speed = data["current"]["wind_speed"]
    msg = json.dumps({"weather": weather, "temperature": temp,
                     "humidity": humidity, "pressure": pressure, "wind_speed": wind_speed})
    return str(msg)+"\n"

# Run API on port 5000, set debug to True
app.run(host='0.0.0.0', port=5000, debug=True)
