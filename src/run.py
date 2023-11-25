#!/usr/bin/env python3
# Strange shebang because python3 isn't located at the same place in my computer and the container

import os
import sys
import time
import threading
import sqlalchemy as db
import EnergyDataHarvest

class printColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


## Loop to run the scrapping of energy data page that is updated every 5 minutes.
def realTime():
    while True:
        EnergyDataHarvest.getNRGData()
        time.sleep(300)

def loadDatabase():
    print(printColors.HEADER + "Creating databases engine" + printColors.ENDC)
    interruptionsDB = db.create_engine("mysql://{}:{}@{}:3306/interruptions".format(os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"), os.environ.get("MYSQL_DATABASE_HOST")))
    networkDataDB = db.create_engine("mysql://{}:{}@{}:3306/networkData".format(os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"), os.environ.get("MYSQL_DATABASE_HOST")))
    print(printColors.OKGREEN + "Databases engine created" + printColors.ENDC)

    interruptionTable = None
    networkDataTable = None
    informationArchiveTable = None
    metadata = None

    try:
        print(printColors.HEADER + "Connecting engines" + printColors.ENDC)
        interruptionsDB.connect()
        print(printColors.OKBLUE + "Interruptions database connected" + printColors.ENDC)
        networkDataDB.connect()
        print(printColors.OKBLUE + "Netword Data database connected" + printColors.ENDC)
        print(printColors.OKGREEN + "All databases connected" + printColors.ENDC)

        print(printColors.OKBLUE + "Extracting metadata" + printColors.ENDC)
        metadata = db.MetaData()
        print(printColors.OKGREEN + "Metadata extracted" + printColors.ENDC)

        print(printColors.HEADER + "Connecting tables" + printColors.ENDC)
        interruptionTable = db.Table("interruption", metadata, autoload_with=interruptionsDB)
        print(printColors.OKBLUE + "Interruptions table connected" + printColors.ENDC)
        interruptionTable = db.Table("realTimeData", metadata, autoload_with=networkDataDB)
        print(printColors.OKBLUE + "realTimeData table connected" + printColors.ENDC)
        interruptionTable = db.Table("informationArchive", metadata, autoload_with=networkDataDB)
        print(printColors.OKBLUE + "informationArchive table connected" + printColors.ENDC)
        print(printColors.OKGREEN + "All tables connected" + printColors.ENDC)


    except:
        print(printColors.FAIL + "Error while creating the tables connections.\nExiting..." + printColors.ENDC)
        sys.exit(84)

    return ((interruptionTable, networkDataTable, informationArchiveTable))

def main() -> int:
    # realTimeThread = threading.Thread(target=realTime);
    #
    # try:
    #     realTimeThread.start();
    # except RuntimeError:
    #     print("Cannot start the thread \"realTimeThread\"");

    # tables = loadDatabase()
    # energieNB = EnergyDataHarvest.EnergieNB(tables[0], tables[1], tables[2])

    energieNB = EnergyDataHarvest.EnergieNB()
    energieNB.openBrowser()
    energieNB.getReport()
    energieNB.quitBrowser()

if (__name__ == '__main__'):
    sys.exit(main())
