import sys
import time
import logging
import threading
import EnergyDataHarvest
from datetime import datetime

logger = logging.getLogger("appLogger")

class Threads:
    __currentYear = datetime.now().year
    __currentMonth = datetime.now().month
    __currentDay = datetime.now().day
    __databaseInstance = None

    def __init__(self, databaseInstance):
        this.__databaseInstance = databaseInstance

        ## Create new instances of the scrappers
        this.__energieNB = EnergyDataHarvest.EnergieNB(self.__databaseInstance)
        this.__archives = EnergyDataHarvest.Archives(self.__databaseInstance)
        this.__interruption = EnergyDataHarvest.Interrput(self.__databaseInstance)
        this.__forecast = EnergyDataHarvest.Forecast(self.__databaseInstance)

        ## Open browsers for the threads
        this.__energieNB.openBrowser()
        this.__archives.openBrowser()
        this.__interruption.openBrowser()
        this.__forecast.openBrowser()

    ## Loop to run the scrapping of energy data page that is updated every 5 minutes.
    def __realTime(self):
        data = []
        while True:
            data = energieNB.getNRGData(data)
            time.sleep(300)
        logger.warning("RealTime thread have exited, the associated page will not be scrapped anymore.")
        return

    def __interruptions(self):
        data = []

        ## Check once a day
        while True:
            data = interruption.getInterrupt(data)
            time.sleep(86400)
        logger.warning("Interruptions thread have exited, the associated page will not be scrapped anymore.")
        return

    def __archives(self):
        currentMonth = __currentMonth
        currentYear = __currentYear
        sys.stdout.flush()

        try:
            lastDownloadedFile = archives.getAllArchive()
        except:
            logger.error("Error while getting all the reports for the archives")
        while True:
            logger.info("Executing scrapping for the archives")
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
        logger.warning("archivesThread thread have exited, the associated page will not be scrapped anymore.")
        return


    ##################################  FORECAST REGION  ###########################
    def __forecast5Days(self):
        try:
            forecast.getForecast5DayAll()
        except:
            logger.error("Error while getting all the reports for the 5 days forecast")
        while True:
            ## Sleep 24 hours
            time.sleep(86400)
            logger.info("Executing scrapping for the daily - 5 days forecast")
            forecast.getForecast5DayLast()
        logger.warning("dailyThread thread have exited, the associated page will not be scrapped anymore.")
        return

    def __forecastHourly(self):
        try:
            forecast.getForecastHourlyAll()
        except:
            logger.error("Error while getting all the reports for the hourly forecast")
        while True:
            ## Sleep 1 hour
            time.sleep(3600)
            logger.info("Executing scrapping for the hourly forecast")
            forecast.getForecastHourlyLast()
        logger.warning("hourlyThread thread have exited, the associated page will not be scrapped anymore.")
        return

    def __forecastEighteenMonths(self):
        try:
            forecast.getForecastEighteenMonthsAll()
        except Exception as error:
            logger.error("Error while getting all the reports for the trimestrial (18 months) forecast")

    ## Uncomment these lines if the page start to be updated again
        # while True:
        #     ## Sleep 1 hour
        #     time.sleep(3600)
        #     logger.info("Executing scrapping for the trimestrial (18 months) forecast")
        #     forecast.getForecastEighteenMonthsLast()
        # logger.warning("trimestrialThread thread have exited, the associated page will not be scrapped anymore.")
        logger.info("Exiting thread \"forecast18Months\", the page don't seem to be updated since 2015")
        return

    def __forecastWeekly(self):
        try:
            forecast.getForecastWeeklyAll()
        except:
            logger.error("Error while getting all the reports for the weekly forecast")
        while True:
            ## Sleep 1 week (File added every friday)
            time.sleep(604800)
            logger.info("Executing scrapping for the weekly forecast")
            forecast.getForecastWeeklyLast()
        logger.warning("weeklyThread thread have exited, the associated page will not be scrapped anymore.")
        return



    def initThreads(self):
        ## Create and start realTime thread
        realTimeThread = threading.Thread(target=realTime, args=(self.__energieNB,))
        try:
            realTimeThread.start()
            logger.info("Thread RealTime started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"realTimeThread\"")

        ## Create and start interruption thread
        interruptionThread = threading.Thread(target=interruptions, args=(self.__interruption,))
        try:
            interruptionThread.start()
            logger.info("Thread interruptions started")
            print(printColors.HEADER + "Thread interruptions started" + printColors.ENDC)
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"interruptionThread\"")

        # ## Create and start archives thread
        archivesThread = threading.Thread(target=archives, args=(self.__archives,))
        try:
            archivesThread.start()
            logger.info("Thread archives started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"archivesThread\"")

        ## Create and start forecast daily 5days thread
        dailyThread = threading.Thread(target=forecast5Days, args=(self.__forecast,))
        try:
            dailyThread.start()
            logger.info("Thread daily-5days forecast started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"dailyThread\"")

        ## Create and start forecast hourly thread
        hourlyThread = threading.Thread(target=forecastHourly, args=(self.__forecast,))
        try:
            hourlyThread.start()
            logger.info("Thread hourly forecast started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"hourlyThread\"")

        ## Create and start forecast 18months thread
        trimestrialThread = threading.Thread(target=forecastEighteenMonths, args=(self.__forecast,))
        try:
            trimestrialThread.start()
            logger.info("Thread trimestrial forecast started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"trimestrialThread\"")

        ## Create and start forecast weekly thread
        weeklyThread = threading.Thread(target=forecastWeekly, args=(self.__forecast,))
        try:
            weeklyThread.start()
            logger.info("Thread weekly forecast started")
            sys.stdout.flush()
        except RuntimeError:
            logger.critical("Cannot start the thread \"weeklyThread\"")


    ## Define a method to close all the opened browsers
    def closeAllBrowsers(self):
        if (self.__energieNB != None):
            self.__energieNB.quitBrowser()
        if (self.__archives != None):
            self.__archives.quitBrowser()
        if (self.__interruption != None):
            self.__interruption.quitBrowser()
        if (self.__forecast != None):
            self.__forecast.quitBrowser()
