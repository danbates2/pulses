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

try:
    import RPi.GPIO as GPIO
    rpi = True
except:
    rpi = False
    print('RPi.GPIO not installed')
import time
import socket

# a "pulse" is 1 unit of measurement use emonHub scales and unit to define
# eg if 100 pulses is 1m3, ie 0.01m3 each then emonHub should use scale = 0.01 and unit = m3
# Therefore "pulse_id" becomes an accumulating "total used" and should follow the meter reading

nodeid = 18
valueid = 1
bounce = 1
interval = 5
lastsend = 0
host = "localhost" #emonbase1"
port = 50012
pulse_pin1 = 21
pulse_pin2 = 15

pulse_id = {1:0,2:0}

def eventHandler1(channel):
    processpulse(1,GPIO.input(channel))
def eventHandler2(channel):
    processpulse(2,GPIO.input(channel))


#    print("event")

def processpulse(channel,status):
    global pulse_id
    global frame
    global lastsend
    if status: #GPIO.input(channel):
        pulse_id[channel] += 1
        print("Channel "+ str(channel) + "  on : " + str(pulse_id[channel]))
    else:
        print("Channel "+ str(channel) + " off : " + str(pulse_id[channel]))

    t = time.time()
    f = ' '.join((str(t), str(nodeid), str(pulse_id[1]), str(pulse_id[2])))
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


if rpi:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pulse_pin1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pulse_pin1, GPIO.BOTH, callback=eventHandler1, bouncetime=bounce)
    GPIO.setup(pulse_pin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pulse_pin2, GPIO.BOTH, callback=eventHandler2, bouncetime=bounce)


while True:  # CTRL+C to break - requires graceful exit
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
        pass
