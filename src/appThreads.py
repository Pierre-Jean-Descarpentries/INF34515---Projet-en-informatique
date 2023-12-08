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
    __energieNB = None
    __archivesObject = None
    __interruption = None
    __forecast = None

    def __init__(self, databaseInstance):
        self.__databaseInstance = databaseInstance

        ## Create new instances of the scrappers
        self.__energieNB = EnergyDataHarvest.EnergieNB(self.__databaseInstance)
        self.__archivesObject = EnergyDataHarvest.Archives(self.__databaseInstance)
        self.__interruption = EnergyDataHarvest.Interrput(self.__databaseInstance)
        self.__forecast = EnergyDataHarvest.Forecast(self.__databaseInstance)

        ## Open browsers for the threads
        self.__archivesObject.openBrowser()
        self.__forecast.openBrowser()

    ## Loop to run the scrapping of energy data page that is updated every 5 minutes.
    def __realTime(self):
        data = []
        while True:
            data = self.__energieNB.getNRGData(data)
            time.sleep(300)
        logger.warning("RealTime thread have exited, the associated page will not be scrapped anymore.")
        return

    def __interruptions(self):
        data = []

        ## Check once a day
        while True:
            data = self.__interruption.getInterrupt(data)
            time.sleep(86400)
        logger.warning("Interruptions thread have exited, the associated page will not be scrapped anymore.")
        return

    def __archives(self):
        currentMonth = self.__currentMonth
        currentYear = self.__currentYear
        lastDownloadedFile = None

        try:
            lastDownloadedFile = self.__archivesObject.getAllArchive()
            logger.warning("All archives extracted") # A changer en info
        except Exception as error:
            logger.error("Error while getting all the reports for the archives %s", error)
        try:
            while True:
                logger.info("Executing scrapping for the archives")
                downloadedFile = self.__archivesObject.getArchive(currentMonth, currentYear)
                ## If no file has been downloaded, return
                if (downloadedFile == None or lastDownloadedFile == downloadedFile):
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
        except Exception as error:
            logger.error("archivesThread error: %s", error)
            logger.warning("archivesThread thread have exited, the associated page will not be scrapped anymore.")
        return


    ##################################  FORECAST REGION  ###########################
    def __forecast5Days(self):
        try:
            self.__forecast.getForecast5DayAll()
            logger.warning("All daily forecast extracted") # A changer en info
        except Exception as error:
            logger.error("Error while getting all the reports for the 5 days forecast %s", error)
        try:
            while True:
                ## Sleep 24 hours
                time.sleep(86400)
                logger.info("Executing scrapping for the daily - 5 days forecast")
                self.__forecast.getForecast5DayLast()
        except Exception as error:
            logger.error("dailyThread error: %s", error)
            logger.warning("dailyThread thread have exited, the associated page will not be scrapped anymore.")
        return

    def __forecastHourly(self):
        try:
            self.__forecast.getForecastHourlyAll()
            logger.warning("All hourly forecast extracted") # A changer en info
        except Exception as error:
            logger.error("Error while getting all the reports for the hourly forecast %s", error)
        try:
            while True:
                ## Sleep 1 hour
                time.sleep(3600)
                logger.info("Executing scrapping for the hourly forecast")
                self.__forecast.getForecastHourlyLast()
        except Exception as error:
            logger.error("hourlyThread error: %s", error)
            logger.warning("hourlyThread thread have exited, the associated page will not be scrapped anymore.")
        return

    def __forecastEighteenMonths(self):
        try:
            self.__forecast.getForecastEighteenMonthsAll()
        except Exception as error:
            logger.error("Error while getting all the reports for the trimestrial (18 months) forecast")

    ## Uncomment these lines if the page start to be updated again
        # try:
            # while True:
            #     ## Sleep 1 hour
            #     time.sleep(3600)
            #     logger.info("Executing scrapping for the trimestrial (18 months) forecast")
            #     self.__forecast.getForecastEighteenMonthsLast()
        # except Exception as error:
            # logger.error("trimestrialThread error: %s", error)
            # logger.warning("trimestrialThread thread have exited, the associated page will not be scrapped anymore.")
        logger.info("Exiting thread \"forecast18Months\", the page don't seem to be updated since 2015")
        return

    def __forecastWeekly(self):
        try:
            self.__forecast.getForecastWeeklyAll()
            logger.warning("All weekly forecast extracted") # A changer en info
        except Exception as error:
            logger.error("Error while getting all the reports for the weekly forecast %s", error)
        try:
            while True:
                ## Sleep 1 week (File added every friday)
                time.sleep(604800)
                logger.info("Executing scrapping for the weekly forecast")
                self.__forecast.getForecastWeeklyLast()
        except Exception as error:
            logger.error("weeklyThread error: %s", error)
            logger.warning("weeklyThread thread have exited, the associated page will not be scrapped anymore.")
        return



    def initThreads(self):
        ## Create and start realTime thread
        realTimeThread = threading.Thread(target=self.__realTime)
        try:
            realTimeThread.start()
            logger.info("Thread RealTime started")

        except RuntimeError:
            logger.critical("Cannot start the thread \"realTimeThread\"")

        ## Create and start interruption thread
        interruptionThread = threading.Thread(target=self.__interruptions)
        try:
            interruptionThread.start()
            logger.info("Thread interruptions started")
        except RuntimeError:
            logger.critical("Cannot start the thread \"interruptionThread\"")

        # ## Create and start archives thread
        archivesThread = threading.Thread(target=self.__archives)
        try:
            archivesThread.start()
            logger.info("Thread archives started")
        except RuntimeError:
            logger.critical("Cannot start the thread \"archivesThread\"")

        ## Create and start forecast daily 5days thread
        dailyThread = threading.Thread(target=self.__forecast5Days)
        try:
            dailyThread.start()
            logger.info("Thread daily-5days forecast started")
        except RuntimeError:
            logger.critical("Cannot start the thread \"dailyThread\"")

        ## Create and start forecast hourly thread
        hourlyThread = threading.Thread(target=self.__forecastHourly)
        try:
            hourlyThread.start()
            logger.info("Thread hourly forecast started")
        except RuntimeError:
            logger.critical("Cannot start the thread \"hourlyThread\"")

        ## Create and start forecast 18months thread
        # trimestrialThread = threading.Thread(target=self.__forecastEighteenMonths)
        # try:
        #     trimestrialThread.start()
        #     logger.info("Thread trimestrial forecast started")
        #
        # except RuntimeError:
        #     logger.critical("Cannot start the thread \"trimestrialThread\"")
        #
        # ## Create and start forecast weekly thread
        weeklyThread = threading.Thread(target=self.__forecastWeekly)
        try:
            weeklyThread.start()
            logger.info("Thread weekly forecast started")
        except RuntimeError:
            logger.critical("Cannot start the thread \"weeklyThread\"")
        logger.info("Won't scrapp the 18 month forecast because it hasn't been updated since 2015. The links also open the pdf files in another tab instead of downloading them.")



    ## Define a method to close all the opened browsers
    def closeAllBrowsers(self):
        if (self.__archivesObject != None):
            self.__archivesObject.quitBrowser()
        if (self.__forecast != None):
            self.__forecast.quitBrowser()
