import configparser
import sys
import time
from datetime import datetime

import board
import busio
import qwiic_soil_moisture_sensor
import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "U6weeGnzUsmhiALh2pZl-1NmK6HishVa9IidtuL1o12MGC4HgKu23Iot_Ow5qFLH_kIG3Pd2ga_T1QKvFPM4NA=="
org = "home"
bucket = "environmental"
location = "change_me"


configParser = ConfigParser.RawConfigParser()

mySoilSensor = qwiic_soil_moisture_sensor.QwiicSoilMoistureSensor()
serialPort = serial.Serial(
 port='/dev/ttyUSB0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

client = InfluxDBClient(url="http://es:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

def initSoilMoistureSensor():
    if mySoilSensor.is_connected == False:
    		print("The Qwiic Soil Moisture Sensor device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

    mySoilSensor.begin()

if __name__ == '__main__':
    try:
        initSoilMoistureSensor()
        while True:
            soil_temperature = serialPort.readline(1)
            # throw away leftovers
            serialPort.reset_input_buffer()
            print(soil_temperature)

            mySoilSensor.read_moisture_level()
            soil_moisture = mySoilSensor.level
            print (soil_moisture)
            mySoilSensor.led_on()
            time.sleep(0.5)
            mySoilSensor.led_off()

            moist_point = Point("soil_moisture")\
                .tag("deviceLocation", location)\
                .field("value", soil_moisture)\
                .time(datetime.utcnow(), WritePrecision.NS)
            soiltemp_point = Point("soil_temperature")\
                .tag("deviceLocation", location)\
                .field("tempF", soil_temperature)\
                .time(datetime.utcnow(), WritePrecision.NS)
            time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)
