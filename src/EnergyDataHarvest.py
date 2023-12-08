import os
import sys
import time
import logging
import requests
import numpy as np
from utils import Utils
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.command import Command

logger = logging.getLogger("appLogger")

## Create and initialize a logger
missingFileLogger = logging.getLogger("appLogger")
basicLogger = logging.FileHandler("app.log", mode='w')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
basicLogger.setFormatter(formatter)
basicLogger.setLevel(logging.INFO)
missingFileLogger.addHandler(basicLogger)


class EnergieNB:
    databaseUtils = None
    currentYear = datetime.now().year
    currentMonth = datetime.now().month
    browser = None

    def __init__(self, database):
        self.databaseUtils = database

    def getNRGData(self, data) -> np.array:
        try:
            r = requests.get("https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp")
            htmlParser = BeautifulSoup(r.content, "html.parser")
            txt = htmlParser.get_text().split('\n')
            dataName = ["Charge au NB",
                        "Demande au NB",
                        "ISO-NE",
                        "EMEC",
                        "MPS",
                        "QUEBEC",
                        "NOVA SCOTIA",
                        "PEI",
                        "Marge de réserve d'exploitation non synchrone de 10 min",
                        "Marge de réserve d'exploitation synchrone de 10 min",
                        "Marge de réserve d'exploitation de 30 min"]
            tmp = []
            for number in txt[45:56]:
                tmp.append(float(number))
            data.append(tmp)
            if (self.databaseUtils.saveRealtimeInDatabase(data) == False):
                return (data)
            else:
                return ([])
        except Exception as error:
            logger.warning("NRGData error: {}".format(error))
            return (data)

    def openBrowser(self):
        option = webdriver.FirefoxOptions()

        # Execute firefox without graphic interface
        option.add_argument("--headless")

        profile = webdriver.FirefoxProfile()
        # Tell selenium to not use the default download folder
        profile.set_preference("browser.download.folderList", 2)
        # Set the download folder
        profile.set_preference("browser.download.dir", "{}/Downloads".format(os.getcwd()))

        option.profile = profile

        try:
            self.browser = webdriver.Firefox(options=option)
            self.browser.implicitly_wait(5)
        except:
            logger.error("Cannot open browser: %s", error)

    def quitBrowser(self):
        if (self.browser != None):
            self.browser.quit()


### DATA VALUES (heure d'Atlentique)
### [Numéro d'intéruption, Status, Heure de début, Heure d'arrêt, but]
class Interrput(EnergieNB):
    def getInterrupt(self, data) -> int:
        try:
            r = requests.get("https://tso.nbpower.com/Public/fr/outages.aspx")
            htmlParser = BeautifulSoup(r.content, "html.parser")
            txt = htmlParser.table.get_text().split('\n')
            while ("" in txt):
                txt.remove("")

            for x in range(5, len(txt), 5):
                while (x + 5 < len(txt) and txt[x + 5].isnumeric() == False):
                    txt[x + 4] += "\n" + txt[x + 5]
                    txt[x + 5] = ""
                    txt.remove("")
                data.insert(0, txt[x:x + 5])
            if (self.databaseUtils.saveInterruptionsInDatabase(data) == True):
                data = []
        except Exception as error:
            logger.warning("Error while getting interruptions: {}".format(error))
        return (data)


class Archives(EnergieNB):
    def getAllArchive(self):
        startMonth = 1
        startYear = 2016
        fileName = None
        fileContent = []

        if (self.browser == None):
            return
        ## Charge la page dans le browser
        self.browser.get("https://tso.nbpower.com/Public/fr/system_information_archive.aspx");


        ## Les éléments récupérés sont le selecteur du mois et de l'année
        for year in range(startYear, self.currentYear + 1):
            for month in range(startMonth, 13):
                ## Récupère le bouton pour télécharger le fichier
                ## Obliger de re-récupérer les éléments car la récupérationdes fichiers téléchargers changent de pages
                obtainData = self.browser.find_element(By.ID, "ctl00_cphMainContent_lbGetData")

                ## Mois
                selectMonthElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlMonth")
                selectMonth = Select(selectMonthElement)
                ## Sélectionne le mois
                selectMonth.select_by_visible_text(str(month))

                ## Année
                selectYearElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlYear")
                selectYear = Select(selectYearElement)
                ## Sélectionne l'année (obligée à chaque fois car besoins de reset l'année vu qu'on change de page et que ça remet les valeurs par défaut)
                selectYear.select_by_visible_text(str(year))

                ## Si on a tout récupéré, on return
                if (year == self.currentYear and month == self.currentMonth):
                    return
                ## Télécharge le fichier
                obtainData.click()
                ## Get the file name
                fileName = Utils.getDownloadedFileName(self.browser, 60)

                ## If file already downloaded
                if (fileName != None and "(" in fileName):
                    os.remove("Downloads/" + fileName)
                    continue

                if (fileName == None or fileName != "FR-{}-{}.csv".format(year, month)):
                    missingFileLogger.warning("File not downloaded for archives with parameters: mois -> {}, année -> {}".format(month, year))
                    continue


                ## Move, read and put file content in database
                try:
                    if (os.path.isfile("Downloads/archive/" + fileName) == True):
                        try:
                            os.remove("Downloads/" + fileName)
                            continue
                        except:
                            pass
                    else:
                        os.rename("Downloads/" + fileName, "Downloads/archive/" + fileName)
                        fileName = "Downloads/archive/" + fileName
                        ## Put in array format to append every changes at once
                        fileContent += [Utils.readFile(fileName)]
                        self.databaseUtils.saveArchiveInDatabase(fileContent, fileName)
                        time.sleep(2)
                except Exception as error:
                    logger.warning(error)
                    try:
                        os.remove("Downloads/" + fileName)
                    except:
                        pass
                    continue
        return (fileName)


    def getArchive(self, month, year):
        fileName = None
        fileContent = []

        try:
            if (self.browser == None):
                return
            self.browser.get("https://tso.nbpower.com/Public/fr/system_information_archive.aspx");
        except Exception as error:
            logger.error("getArchive browser.get error: %s", error)

        selectYearElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlYear")
        selectMonthElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlMonth")
        selectYear = Select(selectYearElement)
        selectMonth = Select(selectMonthElement)
        obtainData = self.browser.find_element(By.ID, "ctl00_cphMainContent_lbGetData")

        selectMonth.select_by_visible_text(str(month))
        selectYear.select_by_visible_text(str(year))

        while True:
            try:
                obtainData.click()
                # self.browser.execute_script("arguments[0].click();", obtainData)
                break
            except Exception as error:
                logger.error("Error while trying to click on button for archives: %s", error)
        fileName = Utils.getDownloadedFileName(self.browser, 60)

        ## Si le fichier à déjà été télécharger
        if (fileName != None and "(" in fileName):
            os.remove("Downloads/" + fileName)
            return(None)

        if (fileName == None or fileName != "FR-{}-{}.csv".format(year, month)):
            missingFileLogger.warning("File not downloaded for archives with parameters: mois -> {}, année -> {}".format(month, year))
            return (None)


        try:
            if (os.path.isfile("Downloads/archive/" + fileName) == True):
                try:
                    os.remove("Downloads/" + fileName)
                except:
                    pass
            else:
                os.rename("Downloads/" + fileName, "Downloads/archive/" + fileName)
                fileName = "Downloads/archive/" + fileName
                ## Put in array format to append every changes at once
                fileContent = [Utils.readFile(fileName)]
                self.databaseUtils.saveArchiveInDatabase(fileContent, fileName)
                return (fileName)
        except Exception as error:
            print(error)
            try:
                os.remove("Downloads/" + fileName)
            except:
                pass
        return (None)


## ATTENTION, TOUTES LES FONCTIONS DE FORECAST FONCTIONNENT EN UTILISANT LES LIENS
    ## SI LE FORMAT DE LIEN CHANGE, IL FAUDRA CHANGER LES FONCTIONS
class Forecast(EnergieNB):

    __browserFiveDays = None
    __browserHourly = None
    __browserWeekly = None
    __browserEighteenMonths = None

    def __linkRecursivity(self, baseLink, browser, predictionType, lvStart = 1):
        fileName = ""
        lastFileName = ""
        fileContent = []

        for lv in range(lvStart, 1000):
            try:
                ## Find the <a> balise containing the link to download the file
                file = browser.find_element(By.ID, "lv_{}".format(lv))
                file.click()
                ## Sleeping because otherwise it won't click on the file before checking for download
                if (browser.current_url != baseLink):
                    logger.debug("New instance:\n  - Current url: {}\n  - Base link: {}".format(browser.current_url, baseLink))
                    self.__linkRecursivity(browser.current_url, browser, predictionType)
                    logger.debug("Out of instance: {}".format(baseLink))
                    continue
                time.sleep(2)
                ## Get the file name
                fileName = Utils.getDownloadedFileName(browser, 60)
            except Exception as error:
                logger.debug("Error while scrapping the files in url: {}, line number: {}. Stopping scrapping for this page . . .\n".format(baseLink, lv))
                missingFileLogger.info("Stopped scrapping files in the url: {}.\n{} files gathered".format(baseLink, lv - 1))

            ## If file already downloaded
            if (fileName != None and "(" in fileName):
                os.remove("Downloads/" + fileName)
                continue

            if (fileName == lastFileName):
                tmp = browser.current_url
                browser.back()
                return
            lastFileName = fileName

            try:
                if (os.path.isfile("Downloads/predictions/{}/{}".format(predictionType, fileName)) == True):
                    try:
                        os.remove("Downloads/" + fileName)
                        continue
                    except:
                        pass
                else:
                    os.rename("Downloads/" + fileName, "Downloads/predictions/{}/{}".format(predictionType, fileName))
                    fileName = "Downloads/predictions/{}/{}".format(predictionType, fileName)
                    time.sleep(1)
                    fileContent = Utils.readFile(fileName)
            except Exception as error:
                try:
                    os.remove("Downloads/" + fileName)
                except:
                    pass
                continue

            ## Put in array format to append every changes at once
            # fileContent = Utils.readFile(fileName)

            if (predictionType == "daily-5days"):
                self.databaseUtils.saveForecast5DaysInDatabase(fileContent, fileName)
            elif (predictionType == "hourly"):
                self.databaseUtils.saveForecastHourlyInDatabase(fileContent, fileName)
            elif (predictionType == "weekly-28Days"):
                self.databaseUtils.saveForecastWeeklyInDatabase(fileContent, fileName)
            elif (predictionType == "18months"):
                self.databaseUtils.saveForecastEighteenInDatabase(fileContent, fileName)
            time.sleep(1.5)

    def getForecast5DayAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\daily%205-day"

        if (self.__browserFiveDays == None):
            return
        self.__browserFiveDays.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserFiveDays, "daily-5days")

    def getForecast5DayLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\daily%205-day"

        if (self.__browserFiveDays == None):
            return
        self.__browserFiveDays.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserFiveDays, "daily-5days", 2)

    def getForecastHourlyAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\hourly"

        if (self.__browserHourly == None):
            return
        self.__browserHourly.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserHourly, "hourly")

    def getForecastHourlyLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\hourly"

        if (self.__browserHourly == None):
            return
        self.__browserHourly.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserHourly, "hourly", 2)

    def getForecastWeeklyAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\weekly%2028-day"

        if (self.__browserWeekly == None):
            return
        self.__browserWeekly.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserWeekly, "weekly-28Days")

    def getForecastWeeklyLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\weekly%2028-day"

        if (self.__browserWeekly == None):
            return
        self.__browserWeekly.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserWeekly, "weekly-28Days", 2)

    def getForecastEighteenMonthsAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\quarterly%2018-month"

        if (self.__browserEighteenMonths == None):
            return
        self.__browserEighteenMonths.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserEighteenMonths, "18months")

    def getForecastEighteenMonthsLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\quarterly%2018-month"

        if (self.__browserEighteenMonths == None):
            return
        self.__browserEighteenMonths.get(baseLink)
        time.sleep(1)
        self.__linkRecursivity(baseLink, self.__browserEighteenMonths, "18months", 2)

## Redefining the methodes openBrowser and quitBrowser form class Forecast because it uses 4 browsers
    def openBrowser(self):
        option = webdriver.FirefoxOptions()

        # Execute firefox without graphic interface
        option.add_argument("--headless")

        profile = webdriver.FirefoxProfile()
        # Tell selenium to not use the default download folder
        profile.set_preference("browser.download.folderList", 2)

        # Set the download folder
        profile.set_preference("browser.download.dir", "{}/Downloads".format(os.getcwd()))

        option.profile = profile

        try:
            self.__browserFiveDays = webdriver.Firefox(options=option)
            ## Tell the driver to wait 5 sec until decreating an element isn't found
            self.__browserFiveDays.implicitly_wait(5)
        except:
            logger.error("Cannot open browser for forecast 5 days")

        try:
            self.__browserHourly = webdriver.Firefox(options=option)
            self.__browserHourly.implicitly_wait(5)
        except:
            logger.error("Cannot open browser for forecast hourly")

        try:
            self.__browserWeekly = webdriver.Firefox(options=option)
            self.__browserWeekly.implicitly_wait(5)
        except:
            logger.error("Cannot open browser for forecast weekly")

        ## Not initializing one since the programm don't scrapp the page
        # self.__browserEighteenMonths = webdriver.Firefox(options=option)


    def quitBrowser(self):
        self.__browserFiveDays.quit()
        self.__browserHourly.quit()
        self.__browserWeekly.quit()
        # self.__browserEighteenMonths.quit()
