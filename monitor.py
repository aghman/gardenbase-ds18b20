import configparser
import sys
import time
from datetime import datetime

import board
import busio
import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "hEwSGkJMW1Nua6jfNL3q63IlUB2hgUWjfcorFQsw9cwUbKSepzwbZUgLgj3uSAz2oQXxHMcra61gWf2PT1DBgA=="
org = "home"
bucket = "garden"
location = "garden-base-beta"


configParser = configparser.ConfigParser()
nextDataType = ""

serialPort = serial.Serial(
 port='/dev/ttyACM0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

client = InfluxDBClient(url="http://es:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

if __name__ == '__main__':
    try:
        while True:
            soil_temperature = serialPort.readline().decode('utf-8')
            soil_temperature = soil_temperature.replace("b'","")
            soil_temperature = soil_temperature.replace("\r\n","")
            if soil_temperature:
                print(soil_temperature)
                temp_parts = soil_temperature.split(":")
                print(temp_parts)
                for iPart in temp_parts:
                    if iPart == "SM":
                        nextDataType = iPart
                    elif iPart == "TF":
                        nextDataType = iPart
                    else: #data
                        if nextDataType == "SM":
                            moist_point = Point("soil_moisture")\
                                .tag("deviceLocation", location)\
                                .field("value", int(iPart))\
                                .time(datetime.utcnow(), WritePrecision.NS)
                            write_api.write(bucket, org, moist_point) 
                        elif nextDataType == "SM": 
                            temp_point = Point("soil_temp")\
                                .tag("deviceLocation", location)\
                                .field("value", float(iPart))\
                                .time(datetime.utcnow(), WritePrecision.NS)
                            write_api.write(bucket, org, temp_point) 

            time.sleep(1)

    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nShutting down gardenbase-snakeberry...")
        sys.exit(0)
