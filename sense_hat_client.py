#! /usr/bin/python
"""
Created 10/17/15 by Greg Griffes
Send sense hat data to UDP server inside the house
"""

###################################################################
# Libraries
###################################################################
import sys, os, socket, time
from sense_hat import SenseHat

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
                print "Sending Message:", message
                self.UDPSock.sendto(message, self.addr)
        except:
            self.UDPSock.close()
            sys.exit(0)

###############################
#
# Start of main line program
#
###############################
if __name__ == '__main__':  #test code

    DEBUG = True
    sense = SenseHat()
    sense.show_message("Hello")

    UDP_client = UDPClient(33333)

    #############################
    # Main while loop
    #############################
    try:
        event_change = False
        return_string = "null event"
        
        while True:                 # The main loop

            sense.show_message("Serve")

            if (event_change):
                print(return_string)
                UDP_client.sendMessage(return_string)
                event_change = False
                
            time.sleep(3)       

    #############################
    # End main while loop
    #############################

    except KeyboardInterrupt:
        print 'Keyboard Interrupt Exception!'

    except IOError:
        print 'I/O Error Exception! Quitting'

