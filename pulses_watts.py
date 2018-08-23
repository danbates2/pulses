#!/usr/bin/env python2
"""

Modified as a initial test script to explore pulse counting on a Pi, this script
just posts via a socket interfacer but will be the basis for a in-built emonhub
pulse counting interfacer.

Currently counts pulses from 0 when started so a whaccumulator will be needed
in emoncms to handle resets until the current meter reading is persisted so that
counting can continue from where it left off, a manual correction technique
will be required to correct for any downtime too.

this will post no quicker than the interval set, if set for 5secs and pulse is
every 1sec then the current total will be sent each 5secs. if pulse was every
10secs then the update would be every 10 secs as no empty data is sent, ie when
the 10sec pulse occurs the ">5secs" allows imediate update. can be used in
conjunction with emonhub's reporter (send) interval if a short interval is
prefered so that more timestamps are recorded eg update every 1sec to emonhub
but only update emoncms every 10s etc

Add the following interfacer to emonhub.conf
        [[Pulse]]
        Type = EmonHubSocketInterfacer
        [[[init_settings]]]
                port_nb = 50012
        [[[runtimesettings]]]
                timestamped = True
                pubchannels = ToEmonCMS,

and if needed open the port in the firewall
        sudo ufw allow 50012
        sudo ufw -f enable



see http://openenergymonitor.org/emon/node/1732#comment-27749 re gas pulses



"""
__author__ = 'Paul Burnell (pb66)'
# modified by Daniel Bates 2018

import RPi.GPIO as GPIO
import time
import socket

# a "pulse" is 1 unit of measurement use emonHub scales and unit to define
# eg if 100 pulses is 1m3, ie 0.01m3 each then emonHub should use scale = 0.01 and unit = m3
# Therefore "pulse_id" becomes an accumulating "total used" and should follow the meter reading

nodeid = 18
nodeid_w = 17
valueid = 1
bounce = 1
interval = 5
lastsend = 0
host = "localhost" #emonbase1"
port = 50012
pulse_pin1 = 21
pulse_pin2 = 15

pulse_id = {1:0,2:0}
watts_id = {1:0,2:0}

previousIntervalTime1 = 0
previousIntervalTime2 = 0
###
pulses_per_kWh = 500.0 # on Elster meter expressed as imp/kWh
const_calc1 = 3600.0 / pulses_per_kWh # for example 500 imp/kWh results in a 7.2s interval at 1kW
const_calc2 = 1000 * const_calc1 # Watts per 1s
###
intervalToPowerConstant = int(const_calc2)
#print str(intervalToPowerConstant)

def eventHandler1(channel):
    global eventTime1
    eventTime1 = time.time()
    processpulse(1,1)
    print "event1"
def eventHandler2(channel):
    global eventTime2
    eventTime2 = time.time()
    processpulse(2,1)
    print "event2"


def processpulse(channel,status):
    global pulse_id
    global frame
    global lastsend
    if status:
        pulse_id[channel] += 1
        print("Channel "+ str(channel) + "  on : " + str(pulse_id[channel]))

        # calculate watts
        global previousIntervalTime1
        global intervalToPowerConstant

        interval1 = eventTime1 - previousIntervalTime1
        print "interval1: " + str(interval1)
      
        watts1 = float(intervalToPowerConstant) / float(interval1)
        print "watts1: " + str(watts1)
      
        watts_id[1] = watts1
      
        previousIntervalTime1 = eventTime1

    t = time.time()
    f = ' '.join((str(t), str(nodeid), str(pulse_id[1]), str(pulse_id[2]), str(watts_id[1])))
    if t > (lastsend + interval):
        lastsend = t
        print f
        send(f)


def send(f):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    f = f + '\r\n'
    s.send(f)
    s.close()


GPIO.setmode(GPIO.BOARD)
GPIO.setup(pulse_pin1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(pulse_pin1, GPIO.RISING, callback=eventHandler1, bouncetime=bounce)
GPIO.setup(pulse_pin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(pulse_pin2, GPIO.RISING, callback=eventHandler2, bouncetime=bounce)

try: # CTRL+C to break - requires graceful exit
    while True:
        time.sleep(5) # the value doesn't matter.
except KeyboardInterrupt:
    GPIO.cleanup() # clean up GPIO on CTRL+C exit
    exit()

GPIO.cleanup()
