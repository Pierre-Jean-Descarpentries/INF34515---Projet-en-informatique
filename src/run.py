#!/usr/bin/env python3
## Strange shebang because python3 isn't located at the same place in my computer and the container

import os
import sys
import logging
from appThreads import Threads
from visualize import Interraction
from databaseUtils import Database

def main() -> int:
    databaseInstance = Database()
    interraction = Interraction(databaseInstance)
    threads = Threads(databaseInstance)

    ## Create and initialize a logger
    logger = logging.getLogger("appLogger")
    basicLogger = logging.FileHandler("app.log", mode='w')
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    basicLogger.setFormatter(formatter)
    logger.addHandler(basicLogger)

    ## Create the directories to store the downloaded files
    try:
        os.mkdir("Downloads")
        os.mkdir("Downloads/archive")
        os.mkdir("Downloads/predictions")
        os.mkdir("Downloads/predictions/daily-5days")
        os.mkdir("Downloads/predictions/hourly")
        os.mkdir("Downloads/predictions/18months")
        os.mkdir("Downloads/predictions/weekly-28Days")
        logger.debug("All downloads directories created")
    except:
        pass

    logger.debug("Starting threads")
    threads.initThreads()
    logger.debug("All threads started")

    interraction.commands()

    logger.debug("Closing browsers")
    threads.closeAllBrowsers()
    logger.debug("All browsers closed")

    return (0)

if (__name__ == '__main__'):
    sys.exit(main())
