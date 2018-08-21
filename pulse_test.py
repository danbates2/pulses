#!/usr/bin/env python2

import time
import RPi.GPIO as GPIO

def pulse_add(pulse_pin1):
    print('Pulse rising!')
    int PulseCount =+ 1
    print "total pulses:" + str(PulseCount)
    
GPIO.add_event_detect(pulse_pin1, GPIO.RISING, callback=pulse_add)
