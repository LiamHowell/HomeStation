# HomeStation - Liam Howell - https://github.com/LiamHowell/HomeStation
import homestation

from PiicoDev_Unified import sleep_ms

from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_VEML6030 import PiicoDev_VEML6030


# Create PiicoDev sensor objects
atmo = PiicoDev_BME280()
lght = PiicoDev_VEML6030()


import secrets
# Configure your WiFi SSID and password
ssid = secrets.ssid_s
password = secrets.password_s


def atmoList():
    tempC, presPa, humRH = atmo.values()
    return tempC, presPa/100, humRH #[degC,hPa,RH]


sensorData = {
    ".Atmo": atmoList,
    "Temperature :": ['Atmo',0],
    "Pressure: ": ['Atmo',1],
    "Humidity: ": ['Atmo',2],
    "Light: ": lght.read,
}


homestation.homestation_Run(ssid,password,sensorData)


'''
Project Write-up: https://core-electronics.com.au/projects/homestation/

Hosts a live and easy to use,self hosted dashboard from a Pico W

Adapted from the adaptation:
https://core-electronics.com.au/projects/wifi-garage-door-controller-with-raspberry-pi-pico-w-smart-home-project/
    Adapted from examples in: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
'''