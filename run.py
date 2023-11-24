#!/bin/python3

import sys
import time
import threading
import EnergyDataHarvest

## Loop to run the scrapping of energy data page that is updated every 5 minutes.
def realTime():
    while True:
        EnergyDataHarvest.getNRGData()
        time.sleep(300)

def main() -> int:
    realTimeThread = threading.Thread(target=realTime);

    try:
        realTimeThread.start();
    except RuntimeError:
        print("Cannot start the thread \"realTimeThread\"");

if (__name__ == '__main__'):
    sys.exit(main())
