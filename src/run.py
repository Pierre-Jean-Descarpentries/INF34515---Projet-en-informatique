#!/usr/bin/env python3
## Strange shebang because python3 isn't located at the same place in my computer and the container

import os
import sys
import time
import threading
import EnergyDataHarvest
from datetime import datetime
from utils import Utils, printColors

__currentYear = datetime.now().year
__currentMonth = datetime.now().month
__currentDay = datetime.now().day

## Loop to run the scrapping of energy data page that is updated every 5 minutes.
def realTime(energieNB):
    data = []
    while True:
        data = energieNB.getNRGData(data)
        time.sleep(300)
    print(printColors.HEADER + "RealTime thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return

def interruptions(interruption):
    data = []

    ## Check once a day
    while True:
        data = interruption.getInterrupt(data)
        time.sleep(86400)
    print(printColors.HEADER + "Interruptions thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return

def archives(archives):
    currentMonth = __currentMonth
    currentYear = __currentYear
    sys.stdout.flush()

    try:
        lastDownloadedFile = archives.getAllArchive()
    except:
        print(printColors.FAIL + "Error while getting all the reports for the archives" + printColors.ENDC, file=sys.stderr)
    while True:
        downloadedFile = archives.getArchive(currentMonth, currentYear)
        ## If no file has been downloaded, return
        if (lastDownloadedFile == None or lastDownloadedFile == downloadedFile):
            ## Sleep 1 day
            time.sleep(86400)
            continue
        lastDownloadedFile = downloadedFile
        ## Calculate the next month
        currentMonth += 1
        if (currentMonth == 13):
            currentMonth = 1
            currentYear += 1
        ## Calculate the delta time between the execution time and next month
        toWait = datetime.datetime(currentYear, currentMonth, 1) - datetime.datetime.now()
        ## Sleep until next month
        time.sleep(toWait)
    print(printColors.HEADER + "archivesThread thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return


##################################  FORECAST REGION  ###########################
def forecast5Days(forecast):
    try:
        forecast.getForecast5DayAll()
    except:
        print(printColors.FAIL + "Error while getting all the reports for the forecast 5 days forecast" + printColors.ENDC, file=sys.stderr)
    while True:
        ## Sleep 24 hours
        time.sleep(86400)
        print(printColors.HEADER + "{}: Executing scrapping for the daily - 5 days forecast".format(datetime.now()) + printColors.ENDC, file=sys.stderr)
        forecast.getForecast5DayLast()
    print(printColors.HEADER + "dailyThread thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return

def forecastHourly(forecast):
    try:
        forecast.getForecastHourlyAll()
    except:
        print(printColors.FAIL + "Error while getting all the reports for the hourly forecast" + printColors.ENDC, file=sys.stderr)
    while True:
        ## Sleep 1 hour
        time.sleep(3600)
        print(printColors.HEADER + "{}: Executing scrapping for the hourly forecast".format(datetime.now()) + printColors.ENDC, file=sys.stderr)
        forecast.getForecastHourlyLast()
    print(printColors.HEADER + "hourlyThread thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return

def forecastEighteenMonths(forecast):
    try:
        forecast.getForecastEighteenMonthsAll()
    except Exception as error:
        print(printColors.FAIL + "Error while getting all the reports for the trimestrial (18 months) forecast days" + printColors.ENDC, file=sys.stderr)

## Uncomment these lines if the page start to be updated again
    # while True:
    #     ## Sleep 1 hour
    #     time.sleep(3600)
    #     forecast.getForecastEighteenMonthsLast()
    # print(printColors.HEADER + "trimestrialThread thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    print(printColors.HEADER + "Exiting thread \"forecast18Months\", the page don't seem to be updated since 2015" + printColors.ENDC)
    return

def forecastWeekly(forecast):
    try:
        forecast.getForecastWeeklyAll()
    except:
        print(printColors.FAIL + "Error while getting all the reports for the weekly forecast" + printColors.ENDC, file=sys.stderr)
    while True:
        ## Sleep 1 week (File added every friday)
        time.sleep(604800)
        print(printColors.HEADER + "{}: Executing scrapping for the weekly forecast".format(datetime.now()) + printColors.ENDC, file=sys.stderr)
        forecast.getForecastWeeklyLast()
    print(printColors.HEADER + "weeklyThread thread have exited, the associated page will not be scrapped anymore. Data may be lost . . ." + printColors.ENDC)
    return



def initThreads(energieNBHarvest, archivesHarvest, interruptionHarvest, forecastHarvest):
    ## Create and start realTime thread
    realTimeThread = threading.Thread(target=realTime, args=(energieNBHarvest,))
    try:
        realTimeThread.start()
        print(printColors.HEADER + "Thread RealTime started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"realTimeThread\"" + printColors.ENDC, file=sys.stderr);

    ## Create and start interruption thread
    interruptionThread = threading.Thread(target=interruptions, args=(interruptionHarvest,))
    try:
        interruptionThread.start()
        print(printColors.HEADER + "Thread interruptions started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"interruptionThread\"" + printColors.ENDC, file=sys.stderr);

    # ## Create and start archives thread
    archivesThread = threading.Thread(target=archives, args=(archivesHarvest,))
    try:
        archivesThread.start()
        print(printColors.HEADER + "Thread archives started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"archivesThread\"" + printColors.ENDC, file=sys.stderr);

    ## Create and start forecast daily 5days thread
    dailyThread = threading.Thread(target=forecast5Days, args=(forecastHarvest,))
    try:
        dailyThread.start()
        print(printColors.HEADER + "Thread daily-5days forecast started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"dailyThread\"" + printColors.ENDC, file=sys.stderr);

    ## Create and start forecast hourly thread
    # hourlyThread = threading.Thread(target=forecastHourly, args=(forecastHarvest,))
    try:
        hourlyThread.start()
        print(printColors.HEADER + "Thread hourly forecast started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"hourlyThread\"" + printColors.ENDC, file=sys.stderr);

    ## Create and start forecast 18months thread
    trimestrialThread = threading.Thread(target=forecastEighteenMonths, args=(forecastHarvest,))
    try:
        trimestrialThread.start()
        print(printColors.HEADER + "Thread trimestrial forecast started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"trimestrialThread\"" + printColors.ENDC, file=sys.stderr);

    ## Create and start forecast weekly thread
    weeklyThread = threading.Thread(target=forecastWeekly, args=(forecastHarvest,))
    try:
        weeklyThread.start()
        print(printColors.HEADER + "Thread weekly forecast started" + printColors.ENDC)
        sys.stdout.flush()
    except RuntimeError:
        print(printColors.FAIL + "Cannot start the thread \"weeklyThread\"" + printColors.ENDC, file=sys.stderr);

    sys.stdout.flush()
    sys.stderr.flush()
    ## Wait for all threads to finish or crash:
    realTimeThread.join()
    interruptionThread.join()
    archivesThread.join()
    dailyThread.join()
    weeklyThread.join()
    hourlyThread.join()
    trimestrialThread.join()
    print(printColors.FAIL + "All threads have exited. Data may be lost . . ." + printColors.ENDC)


def main() -> int:

    ## Create the directories to store the downloaded files
    try:
        os.mkdir("Downloads")
        os.mkdir("Downloads/archive")
        os.mkdir("Downloads/predictions")
        os.mkdir("Downloads/predictions/daily-5days")
        os.mkdir("Downloads/predictions/hourly")
        os.mkdir("Downloads/predictions/18months")
        os.mkdir("Downloads/predictions/weekly-28Days")
    except:
        pass

    utils = Utils()
    energieNB = EnergyDataHarvest.EnergieNB(utils)
    archives = EnergyDataHarvest.Archives(utils)
    interruption = EnergyDataHarvest.Interrput(utils)
    forecast = EnergyDataHarvest.Forecast(utils)

    ## Open browsers
    energieNB.openBrowser()
    archives.openBrowser()
    interruption.openBrowser()
    forecast.openBrowser()

    initThreads(energieNB, archives, interruption, forecast)

    ## Close browsers when finished
    energieNB.quitBrowser()
    archives.quitBrowser()
    interruption.quitBrowser()
    forecast.quitBrowser()

    print(printColors.HEADER + "All threads have finished, exiting." + printColors.ENDC)
    return (0)

if (__name__ == '__main__'):
    sys.exit(main())
