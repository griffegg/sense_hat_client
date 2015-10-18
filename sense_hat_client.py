#! /usr/bin/python
"""
Created 10/17/15 by Greg Griffes
Send sense hat data to UDP server inside the house
"""

###################################################################
# Libraries
###################################################################
import sys, os, socket, time
import webcolors
from sense_hat import SenseHat
import RPi.GPIO as GPIO

#########################
# Local libraries
#########################
# Add the directory containing your module to the Python path (wants absolute paths)
scriptpath = "../utils"
sys.path.append(os.path.abspath(scriptpath))
from processhandler import *

###################################################################
# Globals / Constants
###################################################################

# Command line argument constants
DEBUG = 0               # set this to 1 to see debug messages on monitor
ROAM = 0                # if true, robot will look for a heat signature
RAND = 0                # Causes random head movement when idle
MONITOR = 1             # assume a monitor is attached
CALIBRATION = 0         # don't perform calibration cycle

class UDPClient(object):
    def __init__(self, port):
        self.addr = ('<broadcast>', port)  
        self.UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDPSock.bind(('', 0))
        self.UDPSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def sendMessage(self, message):
        try:
            if len(message):
                message = str(message)
#                print "Sending Message:", message
                self.UDPSock.sendto(message, self.addr)
        except:
            self.UDPSock.close()
            sys.exit(0)

# function for celcius to farenheiht conversion
def c2f (centigrade):
    """
    Convert Centigrade to Fahrenheit
    """
    return 9.0*centigrade/5.0 + 32

###############################
#
# Start of main line program
#
###############################
if __name__ == '__main__':  #test code

    DEBUG = True
    sense = SenseHat()
    sense.show_message("Hello")
    sense.set_imu_config(True, True, True)  # compass only
    
    UDP_client = UDPClient(33333)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.IN)

    sense.set_rotation(0)
    red = webcolors.name_to_rgb("red")
    yellow = webcolors.name_to_rgb("yellow")
    green = webcolors.name_to_rgb("green")
    white = webcolors.name_to_rgb("white")
    blue = webcolors.name_to_rgb("blue")
    gold = webcolors.name_to_rgb("gold")

    #############################
    # Main while loop
    #############################
    try:
        event_change = True
        return_string = "null event"
        
        while True:                 # The main loop

            return_string = "valve=pool"

            if (not GPIO.input(20)):
                return_string = "valve=spa"
                sense.show_message("SPA!", text_colour=yellow, back_colour=red)                
                time.sleep(1)
                sense.clear()
            else:
                sense.clear()
                
            humidity = sense.get_humidity()
            return_string += (",humid=%0.0f" % humidity)

            tempc = sense.get_temperature()
            tempf = c2f(tempc)
            return_string += (",tempe=%0.0f" % tempf)

            pressure = sense.get_pressure()
            return_string += (",press=%0.0f" % pressure)

            orientation = sense.get_orientation_degrees()
            return_string += (",pitch={pitch},roll={roll},yaw={yaw}".format(**orientation))

            print(return_string)
            UDP_client.sendMessage(return_string)

            time.sleep(1)

    #############################
    # End main while loop
    #############################

    except KeyboardInterrupt:
        print 'Keyboard Interrupt Exception!'
        sense.clear()

    except IOError:
        print 'I/O Error Exception! Quitting'
        sense.clear()

