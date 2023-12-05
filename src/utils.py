import os
import sys
import time
import numpy as np
import sqlalchemy as db
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

class Utils:
    __networkDataConnection = None
    __interruptionsConnection = None

    __interruptionTable = None
    __realTimeDateTable = None
    __informationArchiveTable = None
    __chargePrevisionWeeklyTable = None
    __chargePrevisionEighteenMonthsTable = None
    __chargePrevisionHourlyTable = None
    __chargePrevisionDailyTable = None

    def __init__(self):
        self.__loadDatabase()

    @staticmethod
    def getDownloadedFileName(driver, waitTime):
        WebDriverWait(driver,10).until(EC.new_window_is_opened)
        driver.switch_to.window(driver.window_handles[-1])
        driver.get("about:downloads")

        endTime = time.time()+waitTime
        while True:
            try:
                fileName = driver.execute_script("return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")
                if (fileName):
                    driver.back()
                    return fileName
            except:
                pass
            time.sleep(1)
            if time.time() > endTime:
                break
        driver.back()
        return (None)

    @staticmethod
    def readFile(filePath) -> np.array:
        try:
            print(filePath)
            arr = np.loadtxt(filePath, delimiter=",", dtype=str)
            arr = arr[1:]
            return (arr)
        except Exception as error:
            print(printColors.FAIL + "Error while opening file: {}\n".format(filePath)+ printColors.ENDC, error, file=sys.stderr)
            return (None)

    @staticmethod
    def toDate(baseDate) -> str:
        date = "{}-{}-{} {}:{}:{}".format(baseDate[0:4], baseDate[4:6], baseDate[6:8], baseDate[8:10], baseDate[10:12], baseDate[12:14])
        return (date)

    def __loadDatabase(self):
        print(printColors.HEADER + "Creating databases engine" + printColors.ENDC)
        interruptionsDB = db.create_engine("mysql://{}:{}@{}:3306/interruptions".format(os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"), os.environ.get("MYSQL_DATABASE_HOST")))
        networkDataDB = db.create_engine("mysql://{}:{}@{}:3306/networkData".format(os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"), os.environ.get("MYSQL_DATABASE_HOST")))
        print(printColors.OKGREEN + "Databases engine created" + printColors.ENDC)

        metadata = None

        try:
            print(printColors.HEADER + "Connecting engines" + printColors.ENDC)
            self.__interruptionsConnection = interruptionsDB.connect()
            print(printColors.OKBLUE + "Interruptions database connected" + printColors.ENDC)
            self.__networkDataConnection = networkDataDB.connect()
            print(printColors.OKBLUE + "Netword Data database connected" + printColors.ENDC)
            print(printColors.OKGREEN + "All databases connected" + printColors.ENDC)

            print(printColors.OKBLUE + "Extracting metadata" + printColors.ENDC)
            metadata = db.MetaData()
            print(printColors.OKGREEN + "Metadata extracted" + printColors.ENDC)

            print(printColors.HEADER + "Connecting tables" + printColors.ENDC)
            self.__interruptionTable = db.Table("interruption", metadata, autoload_with=interruptionsDB)
            print(printColors.OKBLUE + "Interruptions table connected" + printColors.ENDC)
            self.__realTimeDateTable = db.Table("realTimeData", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "realTimeData table connected" + printColors.ENDC)
            self.__informationArchiveTable = db.Table("informationArchive", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "informationArchive table connected" + printColors.ENDC)
            self.__chargePrevisionDailyTable = db.Table("chargePrevisionDaily", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "chargePrevisionDaily table connected" + printColors.ENDC)
            self.__chargePrevisionHourlyTable = db.Table("chargePrevisionHourly", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "chargePrevisionHourly table connected" + printColors.ENDC)
            self.__chargePrevisionEighteenMonthsTable = db.Table("chargePrevisionEighteenMonths", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "chargePrevisionWeekly table connected" + printColors.ENDC)
            self.__chargePrevisionWeeklyTable = db.Table("chargePrevisionWeekly", metadata, autoload_with=networkDataDB)
            print(printColors.OKBLUE + "chargePrevisionWeekly table connected" + printColors.ENDC)
            print(printColors.OKGREEN + "All tables connected" + printColors.ENDC)

        except:
            print(printColors.FAIL + "Error while creating the tables connections.\nExiting..." + printColors.ENDC, file=sys.stderr)
            sys.exit(84)


    def saveForecast5DaysInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            for content in file:
                for line in content:
                    values.append({
                        "hours": toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )

            ## Create query
            query = db.insert(self.__chargePrevisionDailyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            print(printColors.FAIL + "Error while adding values of file \"{}\" in the \"chargePrevisionDaily\" table".format(filePath) + printColors.ENDC, file=sys.stderr)

    def saveForecastHourlyInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            for content in file:
                for line in content:
                    values.append({
                        "hours": toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )

            ## Create query
            query = db.insert(self.__chargePrevisionHourlyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            print(printColors.FAIL + "Error while adding values of file \"{}\" in the \"chargePrevisionHourly\" table".format(filePath) + printColors.ENDC, file=sys.stderr)

    def saveForecastEighteenInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            for content in file:
                for line in content:
                    values.append({
                        "hours": toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )

            ## Create query
            query = db.insert(self.__chargePrevisionEighteenMonthsTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            print(printColors.FAIL + "Error while adding values of file \"{}\" in the \"chargePrevisionEighteenMonths\" table".format(filePath) + printColors.ENDC, file=sys.stderr)

    def saveForecastWeeklyInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            for content in file:
                for line in content:
                    values.append({
                        "hours": toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )

            ## Create query
            query = db.insert(self.__chargePrevisionWeeklyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            print(printColors.FAIL + "Error while adding values of file \"{}\" in the \"chargePrevisionWeekly\" table".format(filePath) + printColors.ENDC, file=sys.stderr)

    def saveArchiveInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            for content in file:
                for line in content:
                    values.append({
                        "hours": line[0],
                        "chargeNB": line[1],
                        "demandeNB": line[2],
                        "isoNe": line[3],
                        "nmisa": line[4],
                        "quebec": line[5],
                        "novaScotia": line[6],
                        "pei": line[7],
                        "filePath": filePath
                        }
                    )
            ## Create query
            query = db.insert(self.__informationArchiveTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            print(printColors.FAIL + "Error while adding values of file \"{}\" in the \"informationArchive\" table".format(filePath) + printColors.ENDC, file=sys.stderr)

    def saveRealtimeInDatabase(self, data):
        values = []
        try:
        ## Append new values in the values array
            for line in data:
                values.append({
                    "chargeNB": line[0],
                    "demandeNB": line[1],
                    "isoNe": line[2],
                    "emec": line[3],
                    "mps": line[4],
                    "quebec": line[5],
                    "novaScotia": line[6],
                    "pei": line[7],
                    "reserveMarginAsync10Min": line[8],
                    "reserveMarginSync10Min": line[9],
                    "reserveMargin30Min": line[10]
                    }
                )

            ## Create query
            query = db.insert(self.__realTimeDateTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
            return (True)
        except Exception as error:
            print(printColors.FAIL + "Error while adding values from real time data in the \"realTimeData\" table: " + printColors.ENDC, error, file=sys.stderr)
            return (False)

    def saveInterruptionsInDatabase(self, data):
        values = []
        try:
            ## Append new values in the values array
            for line in data:
                query = db.select(self.__interruptionTable).where(self.__interruptionTable.c.id == line[0])
                if (self.__interruptionsConnection.execute(query).all() == []):
                    values.append({
                        "id": line[0],
                        "status": line[1],
                        "debut": line[2],
                        "fin": line[3]
                        }
                    )

            if (values == []):
                return (True)
            ## Create query
            query = db.insert(self.__interruptionTable).values(values)
            ## Execute query
            self.__interruptionsConnection.execute(query)
            ## Commit changes
            self.__interruptionsConnection.commit()
            return (True)
        except Exception as error:
            print(printColors.FAIL + "Error while adding values from interruptions in the \"interruption\" table: " + printColors.ENDC, error, file=sys.stderr)
            return (False)
