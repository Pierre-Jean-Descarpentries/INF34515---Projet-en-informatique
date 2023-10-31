#!/bin/python3

import sys
import time
import EnergyDataHarvest

## Run command until stop asked (ctrl+c)
def realTime():
    while True:
        EnergyDataHarvest.getNRGData()
        time.sleep(300)

def main() -> int:
    command = input("> ")

    if (command.lower() == "run realtime"):
        realTime()
    elif (command.lower() == "run interupt"):
        EnergyDataHarvest.getInterrupt()
    return (0)

if (__name__ == '__main__'):
    sys.exit(main())
