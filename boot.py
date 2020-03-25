# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import machine
machine.freq()          # get the current frequency of the CPU
machine.freq(160000000) # set the CPU frequency to 160 MHz
#machine.freq(80000000) # set the CPU frequency to 80 MHz

import gc
#import webrepl
#webrepl.start()
gc.collect()

