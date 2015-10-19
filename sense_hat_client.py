#! /usr/bin/python
"""
Created 10/17/15 by Greg Griffes
Send sense hat data to UDP server inside the house

to run at startup:
sudo nano /etc/rc.local
add the line before the exit:
/home/pi/projects/sense_hat_client/sense_hat_client.sh &
"""

###################################################################
# Libraries
###################################################################
import sys, os, socket, time, subprocess
import webcolors
#from sense_hat import SenseHat
import RPi.GPIO as GPIO
#import pygame
from raspbot_functions import getCPUtemperature

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

# start of stuff needed to get wifi signal strength
def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching=match(line,keyword)
        if matching!=None:
            return matching
    return None

def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None

def parse_cell(cell):
    """Applies the rules to the bunch of text describing a cell and returns the
    corresponding dictionary"""
    parsed_cell={}
    for key in rules:
        rule=rules[key]
        parsed_cell.update({key:rule(cell)})
    return parsed_cell

def print_table(table):
    widths=map(max,map(lambda l:map(len,l),zip(*table))) #functional magic

    justified_table = []
    for line in table:
        justified_line=[]
        for i,el in enumerate(line):
            justified_line.append(el.ljust(widths[i]+2))
        justified_table.append(justified_line)
    
    for line in justified_table:
        for el in line:
            print el,
        print

def print_cells(cells):
    table=[columns]
    for cell in cells:
        cell_properties=[]
        for column in columns:
            cell_properties.append(cell[column])
        table.append(cell_properties)
    print_table(table)

def get_name(cell):
    return matching_line(cell,"ESSID:")[1:-1]

def get_quality(cell):
    quality = matching_line(cell,"Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3) + " %"

def get_channel(cell):
    return matching_line(cell,"Channel:")

def get_signal_level(cell):
    # Signal level is on same line as Quality data so a bit of ugly
    # hacking needed...
    level = matching_line(cell,"Quality=").split("Signal level=")[1]
    level = level.split()[0].split('/')
    return str(int(round(float(level[0]) / float(level[1]) * 100))).rjust(3) + " %"

def get_encryption(cell):
    enc=""
    if matching_line(cell,"Encryption key:") == "off":
        enc="Open"
    else:
        for line in cell:
            matching = match(line,"IE:")
            if matching!=None:
                wpa=match(matching,"WPA Version ")
                if wpa!=None:
                    enc="WPA v."+wpa
        if enc=="":
            enc="WEP"
    return enc

def get_address(cell):
    return matching_line(cell,"Address: ")

rules={"Name":get_name,
       "Quality":get_quality,
       "Channel":get_channel,
       "Encryption":get_encryption,
       "Address":get_address,
       "Signal":get_signal_level
       }

###############################
#
# Start of main line program
#
###############################
if __name__ == '__main__':  #test code

    DEBUG = True
#    sense = SenseHat()
#    sense.show_message("Hello")
#    sense.set_imu_config(True, True, True)  # compass only
    
    UDP_client = UDPClient(33333)
    interface = "wlan0"

##    cells=[[]]
##    parsed_cells=[]
##
##    proc = subprocess.Popen(["iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True)
##    out, err = proc.communicate()
##    for line in out.split("\n"):
##        cell_line = match(line,"Cell ")
##        if cell_line != None:
##            cells.append([])
##            line = cell_line[-27:]
##        cells[-1].append(line.rstrip())
##
##    cells=cells[1:]
##    for cell in cells:
##        parsed_cells.append(parse_cell(cell))
##    signal_level = get_signal_level(parsed_cells)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.IN)

##    host_name = socket.gethostname()
##    host_ip = socket.gethostbyname(host_name)
##    print host_ip

##    sense.set_rotation(0)
##    red = webcolors.name_to_rgb("red")
##    yellow = webcolors.name_to_rgb("yellow")
##    green = webcolors.name_to_rgb("green")
##    white = webcolors.name_to_rgb("white")
##    blue = webcolors.name_to_rgb("blue")
##    gold = webcolors.name_to_rgb("gold")

    #############################
    # Main while loop
    #############################
    try:
        done = False
        return_string = "null event"

        print "pool and spa client running..."
        
        while not done:                 # The main loop

##            for event in pygame.event.get():
##                if event.type == KEYDOWN:
##                    done = True

            return_string = "valve=pool"

            if (not GPIO.input(20)):
                return_string = "valve=spa"
##                sense.show_message("SPA!", text_colour=yellow, back_colour=red)                
##                time.sleep(1)
##                sense.clear()
##                return_string += (","+host_ip)

##            else:
##                sense.clear()
##                
##            humidity = sense.get_humidity()
##            return_string += (",humid=%0.0f" % humidity)
##
##            tempc = sense.get_temperature()
##            tempf = c2f(tempc)
##            return_string += (",tempe=%0.0f" % tempf)
##
##            pressure = sense.get_pressure()
##            return_string += (",press=%0.0f" % pressure)
##
##            orientation = sense.get_orientation_degrees()
##            return_string += (",pitch={pitch},roll={roll},yaw={yaw}".format(**orientation))

            CPU_TEMP = getCPUtemperature()
            return_string += (",cpu_temp=%0.0f" % CPU_TEMP)
            
##            return_string += (",wifi_signal=%0.0f" % signal_level)

            print(return_string)
            
            UDP_client.sendMessage(return_string)
            time.sleep(5)

    #############################
    # End main while loop
    #############################

    except KeyboardInterrupt:
        print 'Keyboard Interrupt Exception!'
#        sense.clear()

    except IOError:
        print 'I/O Error Exception! Quitting'
#        sense.clear()

