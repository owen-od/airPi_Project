# AirPi Air Quality Project
This project is a Raspberry Pi air quality monitor (AirPi) built using a Raspberry Pi, Canakit breakout board and bme680 environmental sensor. 

The AirPi device collects data on temperature, humidity, pressure, gas resistance and air quality (as a percentage).

This data is then published to the ThingSpeak platfrom using the MQQT protocol, allowing for the creation of graphs to map the data and reactions to occur (e.g. a tweet to be sent) when certain enviromental limits are passed (e.g the air quality degrades below a certain percentage). 

The data is then accessed and displayed in a companian web application. A prototype of this companian web application is available on glitch here: https://airpi-web-app.glitch.me/ (Link to the code [here](https://glitch.com/edit/#!/airpi-web-app)).

![AirPi Web Application](/images/airpi.png)

To explore the prototype of this web application, use the below login details:
```
email: homer@simpson.com
password: secret
```

While this is the main part of the project, in the bonus section below there are: (i) further instructions on how to connect a light to the AirPi that flashes when the user is home and certain environmental limits are passed; (ii) an api that allows access on the local network to sensor data from the bme680 sensor, connected netatmo air quality monitors and openweathermap API which may be used for further projects. 

## Installation
At command line, you will need to install the following:

```
sudo apt get install y python smbus
sudo apt get install y i2c tools
sudo apt-get install mosquitto
sudo pip3 install paho-mqtt
sudo pip3 install python-dotenv
sudo pip3 install bme680
```

Connect the bme680 sensor to the Raspberry Pi as in the below image:

![Sensor connected to Pi using breadboard](/images/canakit.jpg)

Now we will enable I2C:
```
Enter sudo raspi-config
Select 3, interface options
Select p5, 12C
Enable
```

Now reboot your Raspberry Pi: 
`Sudo reboot`

Check if the sensor has been detected by running at the command line: `sudo i2cdetect y 1`

you should see the below output:
   
         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- 77

This indicates that there is a device at address 0x77.

Now clone this repo into the relevant directory: `git clone https://github.com/owen-od/airPi_Project`

## Configuration
The following assumes that you have created a ThingSpeak account and channel and added a new device. To proceed you will need a list of credentials for your device that includes Client ID, username and password. This can be downloaded from ThingSpeak as a plain text file. 

Create a file called `.env` in your directory. Copy your credentials from the plain text file into this directory. 

Then add the ThingSpeak channel id for your device. Finally, add a transmission interval to the file. This will determine how frequently sensor data is published to ThingSpeak. 

Your `.env` file should now look like the below

```
username = LbbgBrFyDd4lKhEkORo8AAA
clientId = LbbgBrFyDd4lKhEkORo8AAA
password = 6c+vxaw3CVLredzEsheaHy7B
channelId = 1319333
transmissionInterval = 60
```

## How to use this
In order to obtain air quality readings from the local environment, the `indoor-air-quality.py` script should first be run for 5 minutes. This allows the sensor to run for a burn in periord. After 5 minutes have elapsed, it will then use a combination of relative humidity and gas resistance to estimate indoor air quality as a percentage. The latest air quality reading will continuously be updated in a text file, allowing the data to be accessed in other scripts. 

The `thingspeak.py` script may then be run. This will get readings for temperature, humidity, pressure, gas resistance and air quality and publish them to ThingSpeak (every 60 seconds by default. 

The data, and graphs of the data, can then be accessed from ThingSpeak in the web application. 

Note that the above scripts may also be set as a cron job to allow the scripts to run at boot. To do so at the command line run `sudo crontab -e`. Then, **adjusting the paths to match your directories**, enter the below: 
```
@reboot python3 /home/pi/airPi/indoor-air-quality.py
@reboot sleep 300 && python3 /home/pi/airPi/thingspeak.py mqtt://mqtt3.thingspeak.com:8883
```

Note that if a light has also been connected to your airPi (see bonus section below), then the `lights.py` script can also be added to run at boot:
```
@reboot python3 /home/pi/airPi/lights.py
```

## Bonus

**(i) This section describes how to connect an LED to the Raspberry Pi, so that the LED light alerts the user when certain devices are detected on the network (indicating that the user is home) and certain environmental limits are passed.**

This example uses a laptop and a phone to detect the presence of the user at home (the presence of either will mean that the script can run). If the user is home, the LED light will turn on when the temperature drops below a certain limit, notifying the user to take action (e.g. to turn the heating on when the temperature is too low!). When the devices are no longer on the network, the light will temporarily turn off. The light will also turn off when the conditions improve. 

Connect an LED to the AirPi as in the below image:

![LED connected to Raspberry Pi](/images/light.jpg)

Then, you will need to know the MAC addresses of the devices that you wish to use to indicate the presence of the user at home. If you do not know these, run the following command to detect them (replacing the IP address with that of your network): ``sudo nmap 192.168.0.0/24 | grep MAC``

You must then enter the names of the devices and their MAC addresses in the ``presence_detector.py`` script, at line 10. You should also replace the network address at line 16 with your network address. 

Install the GPIOzero library as follows:
```
sudo apt install python3-gpiozero
```
You can now run the script with the following command: 
```
python3 lights.py
```

Note that this will only run when the devices entered in the ``presence_detector.py`` script are detected on the network. 

**(ii) This section describes how to create a simple web api with Flask that may be used to access data from the AirPi and connected netatmo air quality monitors on the local network**

This example uses a Netatmo smart indoor air quality monitor placed in the bedroom, with an additional module located outside on the balcony. The AirPi is located in the home office. 

![Netatmo air quality monitors](/images/netatmo.jpg)

First, in order to use the Netatmo devices, a valid Netatmo account is required. From this account, the following details can be obtained: client ID, client secret, username, password, device MAC address (note that to obtain the client secret and client Id, you must first create an app in your account - see [create your app](https://dev.netatmo.com/apps/createanapp)). 
Your details can then be added to the .env file created above. This should appear as below in the .env file:
```
net_client_id = '1234567890abcdef12345678',
net_client_secret = 'ABCdefg123456hijklmn7890pqrs',
net_username = 'user@mail',
net_password = 'password',
net_device = '70:ee:50:XX:XX:XX'
```

If you wish to use the `http://YOUR_PI_IP:5000/home/city` route to obtain local weather data, you will first need to obtain an API key from [openweathermap](https://openweathermap.org/) (and change the latitude and longitude in the route to your local area). Add the api key to your .env file as below:
```
ow_api_key = 1111bb4340089aaa393990f4fe742222
```

To use the API then you will need to additionally install the following:

```
pip3 install netatmo
pip3 install flask
pip3 install -U flask-cors
```

Then run the script in the terminal: `python3 api.py`

You may now make calls to the API using the specified routes. For example: `http://YOUR_PI_IP:5000/home/office`

A page containing an overview of home environmental data can be accesed with the following route: `http://YOUR_PI_IP:5000/`

If you do not know the IP address of your Raspberry Pi for the above, run the following command in a terminal on the Raspberry Pi to find it: `ip a`

## Project Graphics
![Project Graphics](/images/final_graphics.jpg)

## Contact
Contact me at 20095405@wit.ie