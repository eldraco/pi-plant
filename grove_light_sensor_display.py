#!/usr/bin/env python
#
# GrovePi Example for using the Grove Light Sensor and the LED together to turn the LED On and OFF if the background light is greater than a threshold.
# Modules:
# 	http://www.seeedstudio.com/wiki/Grove_-_Light_Sensor
# 	http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#
'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time
from grovepi import *
import grovepi 
from grove_rgb_lcd import *
from math import isnan
import Adafruit_IO
from dotenv import load_dotenv

print('Starting')


# Connect to Adafruit mqtt server
load_dotenv('.env')
client.run(os.getenv('ADAFRUITUSER'))
client.run(os.getenv('ADAFRUITKEY'))
client.run(os.getenv('ADAFRUITTOPIC'))

AIOclient = Adafruit_IO.MQTTClient(ADAFRUITUSER, ADAFRUITKEY)
AIOclient.connect()

dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# Connect the Grove Light Sensor to analog port A0
# SIG,NC,VCC,GND
light_sensor = 0

sound_sensor = 1

# Connect the LED to digital port D4
# SIG,NC,VCC,GND
led = 4

# Turn on LED once sensor exceeds threshold resistance
threshold = 10

#Start and initialize the OLED
setRGB(0,255,0)


grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(led,"OUTPUT")

print('Sensors Setup')

while True:
    try:
        # Get sensor value
        light_value = grovepi.analogRead(light_sensor)
        AIOclient.publish('Light', light_value)

        # Get sound sensor
        sound_value = grovepi.analogRead(sound_sensor)
        AIOclient.publish('Sound', sound_value)

        # Get temp and hum value
        [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
        AIOclient.publish('Temperature', temp)
        AIOclient.publish('Humidity', hum)

        # check if we have nans
        # if so, then raise a type error exception
        if isnan(temp) is True or isnan(hum) is True:
            raise TypeError('nan error')

        # Calculate resistance of sensor in K
        resistance = (float)(1023 - light_value) * 10 / light_value

        if resistance > threshold:
            # Send HIGH to switch on LED
            grovepi.digitalWrite(led,1)
        else:
            # Send LOW to switch off LED
            grovepi.digitalWrite(led,0)

        text = (
                f'L:{light_value:3} T:{str(temp):4}C\n'
                f'H:{str(hum)} S:{sound_value}'
               )
        setText_norefresh(text)
        #setText_norefresh("L:" + str(sensor_value) + "\n" + "Resistance :" + str(resistance) )

        #print("sensor_value = %d resistance = %.2f" %(sensor_value,  resistance))

        time.sleep(10)

    except (IOError, TypeError) as e:
        print(str(e))
        # and since we got a type error
        # then reset the LCD's text
        setText("")

    except KeyboardInterrupt as e:
        print(str(e))
        # since we're exiting the program
        # it's better to leave the LCD with a blank text
        setText("")
        break

