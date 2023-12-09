import os
import sys
import logging
import numpy as np
from utils import Utils
import sqlalchemy as db

logger = logging.getLogger("appLogger")

class Database:
    __networkDataConnection = None

    __interruptionTable = None
    __realTimeDateTable = None
    __informationArchiveTable = None
    __chargePrevisionWeeklyTable = None
    __chargePrevisionEighteenMonthsTable = None
    __chargePrevisionHourlyTable = None
    __chargePrevisionDailyTable = None

    def __init__(self):
        self.__loadDatabase()

    def __loadDatabase(self):
        logger.info("Creating databases engine")
        networkDataDB = db.create_engine("mysql://{}:{}@{}:3306/networkData".format(os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"), os.environ.get("MYSQL_DATABASE_HOST")))
        logger.info("Databases engine created")

        metadata = None

        try:
            logger.info("Connecting engines")
            self.__networkDataConnection = networkDataDB.connect()
            logger.info("Netword Data database connected")
            logger.info("All databases connected")

            logger.info("Extracting metadata")
            metadata = db.MetaData()
            logger.info("Metadata extracted")

            logger.info("Connecting tables")
            self.__interruptionTable = db.Table("interruption", metadata, autoload_with=networkDataDB)
            logger.info("Interruptions table connected")
            self.__realTimeDateTable = db.Table("realTimeData", metadata, autoload_with=networkDataDB)
            logger.info("realTimeData table connected")
            self.__informationArchiveTable = db.Table("informationArchive", metadata, autoload_with=networkDataDB)
            logger.info("informationArchive table connected")
            self.__chargePrevisionDailyTable = db.Table("chargePrevisionDaily", metadata, autoload_with=networkDataDB)
            logger.info("chargePrevisionDaily table connected")
            self.__chargePrevisionHourlyTable = db.Table("chargePrevisionHourly", metadata, autoload_with=networkDataDB)
            logger.info("chargePrevisionHourly table connected")
            self.__chargePrevisionEighteenMonthsTable = db.Table("chargePrevisionEighteenMonths", metadata, autoload_with=networkDataDB)
            logger.info("chargePrevisionWeekly table connected")
            self.__chargePrevisionWeeklyTable = db.Table("chargePrevisionWeekly", metadata, autoload_with=networkDataDB)
            logger.info("chargePrevisionWeekly table connected")
            logger.info("All tables connected")

        except:
            logger.critical("Error while creating the tables connections.\nExiting...")
            sys.exit(84)


    def saveForecast5DaysInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            if (len(file) > 0 and type(file[0]) == np.ndarray):
                for line in file:
                    values.append({
                        "hours": Utils.toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )
            elif (len(file) > 0):
                values.append({
                    "hours": Utils.toDate(file[0]),
                    "prevision": file[1],
                    "filePath": filePath
                    }
                )
            else:
                logger.debug("Empty file: {}".format(filePath))
                return

            ## Create query
            query = db.insert(self.__chargePrevisionDailyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except Exception as error:
            logger.error("Error while adding values of file \"{}\" in the \"chargePrevisionDaily\" table\n".format(filePath))

    def saveForecastHourlyInDatabase(self, file, filePath):
        values = []
        index = 0
        try:
            if (len(file) > 0 and type(file[0]) == np.ndarray):
                for line in file:
                    values.append({
                        "hours": Utils.toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )
            elif (len(file) > 0):
                values.append({
                    "hours": Utils.toDate(file[0]),
                    "prevision": file[1],
                    "filePath": filePath
                    }
                )
            else:
                logger.info("Empty file: {}".format(filePath))
                return

            ## Create query
            query = db.insert(self.__chargePrevisionHourlyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            logger.error("Error while adding values of file \"{}\" in the \"chargePrevisionHourly\" table\n".format(filePath))

    def saveForecastEighteenInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            if (len(file) > 0 and type(file[0]) == np.ndarray):
                for line in file:
                    values.append({
                        "hours": Utils.toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )
            elif (len(file) > 0):
                values.append({
                    "hours": Utils.toDate(file[0]),
                    "prevision": file[1],
                    "filePath": filePath
                    }
                )
            else:
                logger.info("Empty file: {}".format(filePath))
                return

            ## Create query
            query = db.insert(self.__chargePrevisionEighteenMonthsTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            logger.error("Error while adding values of file \"{}\" in the \"chargePrevisionEighteenMonths\" table\n".format(filePath))

    def saveForecastWeeklyInDatabase(self, file, filePath):
        values = []
        index = 0

        try:
            if (len(file) > 0 and type(file[0]) == np.ndarray):
                for line in file:
                    values.append({
                        "hours": Utils.toDate(line[0]),
                        "prevision": line[1],
                        "filePath": filePath
                        }
                    )
            elif (len(file) > 0):
                values.append({
                    "hours": Utils.toDate(file[0]),
                    "prevision": file[1],
                    "filePath": filePath
                    }
                )
            else:
                logger.info("Empty file: {}".format(filePath))
                return

            ## Create query
            query = db.insert(self.__chargePrevisionWeeklyTable).values(values)
            ## Execute query
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
        except:
            logger.error("Error while adding values of file \"{}\" in the \"chargePrevisionWeekly\" table\n".format(filePath))

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
        except Exception as error:
            logger.error("Error while adding values of file \"{}\" in the \"informationArchive\" table\n".format(filePath))

    ## Return a boolean because it will stack up the data if the database is unavialable
    ## Cannot do that for the archives or forecast because they contains too much data
    def saveRealtimeInDatabase(self, data) -> bool:
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
            logger.error("Error while adding values of file in the \"realTimeData\" table\n")
            return (False)

    ## Return a boolean because it will stack up the data if the database is unavialable
    ## Cannot do that for the archives or forecast because they contains too much data
    def saveInterruptionsInDatabase(self, data) -> bool:
        values = []
        try:
            ## Append new values in the values array
            for line in data:
                query = db.select(self.__interruptionTable).where(self.__interruptionTable.c.id == line[0])
                if (self.__networkDataConnection.execute(query).all() == []):
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
            self.__networkDataConnection.execute(query)
            ## Commit changes
            self.__networkDataConnection.commit()
            return (True)
        except Exception as error:
            logger.error("Error while adding values in the \"interruption\" table\n%s", error)
            return (False)

    def getRealTimeDataValueFromYear(self, columName, year):
        query = "SELECT {} FROM realTimeData WHERE YEAR(updateTime) = {}".format(columnName, year)
        try:
            queryResult = self.__networkDataConnection.execute(db.text(query))
            rows = queryResult.fetchall()
            if (len(rows) == 0):
                print(printColors.OKBLUE + "No data found for the year {} for the desired type".format(year) + printColors.ENDC)
                return (None)
        except Exception as error:
            logger.warning("Error while executing the query in getRealTimeDataValueFromYea: %s", error)
            return (None)
        return (rows)

    def getValuesFromYear(self, type, year) -> str:
        query = None
        rows = None

        if (type == "1"):
            ## Real time data
            query = "SELECT * FROM realTimeData WHERE YEAR(updateTime) = {}".format(year)
        elif (type == "2"):
            ## Interruptions
            query = "SELECT * FROM interruption WHERE YEAR(debut) = {}".format(year)
        elif (type == "3"):
            ## Archive
            query = "SELECT * FROM informationArchive WHERE YEAR(hours) = {}".format(year)
        elif (type == "4.1"):
            ## Forecast daily
            query = "SELECT * FROM chargePrevisionDaily WHERE YEAR(hours) = {}".format(year)
        elif (type == "4.2"):
            ## Forecast hourly
            query = "SELECT * FROM chargePrevisionHourly WHERE YEAR(hours) = {}".format(year)
        elif (type == "4.3"):
            ## Forecast Weekly
            query = "SELECT * FROM chargePrevisionWeekly WHERE YEAR(hours) = {}".format(year)
        elif (type == "4.4"):
            ## Forecast 18 months
            query = "SELECT * FROM chargePrevisionEighteenMonths WHERE YEAR(hours) = {}".format(year)

        try:
            queryResult = self.__networkDataConnection.execute(db.text(query))
            rows = queryResult.fetchall()
            if (len(rows) == 0):
                print(printColors.OKBLUE + "No data found for the year {} for the desired type".format(year) + printColors.ENDC)
                return (None)
        except Exception as error:
            logger.warning("Error while executing the query in getValuesFromYear: %s", error)
            return (None)
        return (rows)
