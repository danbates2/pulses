#!/usr/bin/env python2

import time
import RPi.GPIO as GPIO

def pulse_add(pulse_pin1):
    print('Pulse rising!')
    int PulseCount =+ 1
    print "total pulses:" + str(PulseCount)
    
GPIO.add_event_detect(pulse_pin1, GPIO.RISING, callback=pulse_add)

def main():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pulse_pin1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pulse_pin1, GPIO.RISING, callback=pulse_add, bouncetime=1)

try:
    while True:
        main()
except KeyboardInterrupt:
    pass

if __name__ == "__main__":
        main()
