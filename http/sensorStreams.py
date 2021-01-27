from collections import OrderedDict
from mq import *
import sys
import time
import config
import requests
import json
import barometric
import Adafruit_DHT


# Use read_retry method. This will retry up to 15 times to
# get a sensor reading (waiting 2 seconds between each retry).


while True:

    # Get Unix timestamp
    timestamp = int(time.time())

    # Json open
    build_json = {
        "iot2tangle": [],
        "device": str(config.device_id),
        "timestamp": str(timestamp)
    }

    # If Enviromental
    if config.dht11:
        # Set sensor type : Options are DHT11,DHT22 or AM2302
        sensor = Adafruit_DHT.DHT11
        # Set GPIO sensor is connected to
        gpio = 17
        # Get Temp/Press/Hum values
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
        build_json['iot2tangle'].append({
            "sensor": "DHT11-environmental",
            "data": [{
                "Temp": str(temperature)
            }, {
                "Humidity": str(humidity)
            }]
        })
    if config.mq135:
        # Set sensor type : Options are DHT11,DHT22 or AM2302
        mq=MQ();
        perc = mq.MQPercentage()

      
        build_json['iot2tangle'].append({
            "sensor": "MQ135 - Smoke / Gases",
            "data": [{
                "Gas LPG": perc["GAS_LPG"]
            }, {
               "CO": perc["CO"]
            }, {
               "Smoke": perc["SMOKE"]
            }]
        })
    
    if config.bmp180:
        # Get Temp/Press/Altitude values
        bmp = barometric.bmp180()
        temp = bmp.get_temp()
        press = bmp.get_pressure()
        altitude = bmp.get_altitude()

        build_json['iot2tangle'].append({
            "sensor": "BMP180-Enviromental",
            "data": [{
                "Pressure": str(press),
                "Temp": str(temp)
            },{
                "Altitude": str(altitude)
            }]
        })

    # Set Json headers
    headers = {"Content-Type": "application/json"}

    # Send Data to Json server
    try:
        build_json = json.dumps(build_json)
        r = requests.post(config.endpoint, data=build_json, headers=headers)
        r.raise_for_status()
        print(":: Sending datasets ::")
        print("--------------------------------------------------------")
        print(build_json)

    except:

        print("No server listening at " + str(config.endpoint))

        # Interval
        time.sleep(config.relay)
