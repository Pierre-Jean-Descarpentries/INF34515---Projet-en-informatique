import os
import sys
import time
import utils
import requests
import numpy as np
from utils import Utils, printColors
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

__printColors = printColors()

class EnergieNB:
    utils = None
    currentYear = datetime.now().year
    currentMonth = datetime.now().month
    browser = None

    def __init__(self, utils):
        self.utils = utils

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
            if (self.utils.saveRealtimeInDatabase(data) == False):
                return (data)
            else:
                return ([])
        except Exception as error:
            print("NRGData error: ", error, file=sys.stderr)
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
        self.browser = webdriver.Firefox(options=option)

    def quitBrowser(self):
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
            if (self.utils.saveInterruptionsInDatabase(data) == True):
                data = []
        except Exception as error:
            print("Error while getting interruptions: ", error, file=sys.stderr)
        return (data)


class Archives(EnergieNB):
    def getAllArchive(self):
        startMonth = 1
        startYear = 2016
        fileName = None
        fileContent = []

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

                if (fileName == None || filename != "FR-{}-{}.csv".format(year, month)):
                    print(printColors.FAIL + "File not downloaded for archives with parameters: mois -> {}, année -> {}".format(month, year) + printColors.ENDC)
                    return

                ## If file already downloaded
                if ("(1).csv" in fileName):
                    print("toRm", file=sys.stdout)
                    sys.stdout.flush()
                    os.remove("Downloads/" + fileName)
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
                        self.utils.saveArchiveInDatabase(fileContent, fileName)
                        time.sleep(1)
                except Exception as error:
                    print(error)
                    try:
                        os.remove("Downloads/" + fileName)
                    except:
                        pass
                    continue
        return (fileName)


    def getArchive(self, month, year):
        self.browser.get("https://tso.nbpower.com/Public/fr/system_information_archive.aspx");

        selectYearElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlYear")
        selectMonthElement = self.browser.find_element(By.ID, "ctl00_cphMainContent_ddlMonth")
        selectYear = Select(selectYearElement)
        selectMonth = Select(selectMonthElement)
        obtainData = self.browser.find_element(By.ID, "ctl00_cphMainContent_lbGetData")
        fileName = None
        fileContent = []

        selectMonth.select_by_visible_text(str(year))
        selectYear.select_by_visible_text(str(year))

        while True:
            try:
                obtainData.click()
                # self.browser.execute_script("arguments[0].click();", obtainData)
                break
            except Exception as error:
                print("Error while trying to click on button for archives: ", error, file=sys.stderr)
        fileName = Utils.getDownloadedFileName(self.browser, 60)

        if (fileName == None || filename != "FR-{}-{}.csv".format(year, month)):
            print(printColors.FAIL + "File not downloaded for archives with parameters: mois -> {}, année -> {}".format(month, year) + printColors.ENDC)
            return (None)

        ## Si le fichier à déjà été télécharger
        if ("(1).csv" in fileName):
            os.remove("Downloads/" + fileName)
            return(fileName)

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
                fileContent = [[Utils.readFile(fileName)]]
                self.utils.saveArchiveInDatabase(fileContent, fileName)
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

    __browser5Days = None
    __browserHourly = None
    __browserWeekly = None
    __browser18Months = None

    def __linkRecursivity(self, baseLink, predictionType, browser, lvStart = 1):
        fileName = ""
        lastFileName = ""
        filecontent = []

        for lv in range(lvStart, 1000):
            try:
                ## Find the <a> balise containing the link to download the file
                file = browser.find_element(By.ID, "lv_{}".format(lv))
                obtainData.click()
                # browser.execute_script("arguments[0].click()", obtainData)
                if (browser.current_url != baseLink):
                    self.__linkRecursivity(browser.current_url)
                    continue
                ## Get the file name
                fileName = Utils.getDownloadedFileName(browser, 60)
            except:
                print(__printColors.FAIL + "Error while scrapping the files in url: {}, line number: {}. Stopping scrapping for this page . . .".format(baseLink, lv) + __printColors.ENDC)
                break

            if (fileName == lastFileName):
                browser.navigate().back()
                return
            lastFileName = fileName
            ## If file already downloaded
            if ("(1).csv" in fileName):
                os.remove("Downloads/" + fileName)
                continue

            try:
                if (os.path.isfile("Downloads/archive/" + fileName) == True):
                    try:
                        os.remove("Downloads/" + fileName)
                        continue
                    except:
                        pass
                else:
                    os.rename("Downloads/" + fileName, "Downloads/predictions/{}/{}".format(predictionType, fileName))
                    fileName = "Downloads/archive/" + fileName
            except Exception as error:
                print(error)
                try:
                    os.remove("Downloads/" + fileName)
                except:
                    pass
                continue

            ## Put in array format to append every changes at once
            fileName = "Downloads/predictions/{}/{}".format(predictionType, fileName)
            fileContent += [Utils.readFile(fileName)]

            if (predictionType == "daily-5days"):
                self.utils.saveForecast5DaysInDatabase(fileContent, fileName)
            elif (predictionType == "hourly"):
                self.utils.saveForecastHourlyInDatabase(fileContent, fileName)
            elif (predictionType == "weekly-28days"):
                self.utils.saveForecastWeeklyInDatabase(fileContent, fileName)
            elif (predictionType == "18months"):
                self.utils.saveForecastEighteenInDatabase(fileContent, fileName)
            time.sleep(1)

    def getForecast5DayAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\daily%205-day"

        self.__linkRecursivity(baseLink, self.__browser5Days, "daily-5days")

    def getForecast5DayLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\daily%205-day"

        self.__linkRecursivity(baseLink, self.__browser5Days, "daily-5days", 2)

    def getForecastHourlyAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\hourly"

        self.__linkRecursivity(baseLink, self.__browser5Days, "hourly")

    def getForecastHourlyLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\hourly"

        self.__linkRecursivity(baseLink, self.__browser5Days, "hourly", 2)

    def getForecastWeeklyAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\weekly%2028-day"

        self.__linkRecursivity(baseLink, self.__browser5Days, "weekly-28days")

    def getForecastWeeklyLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\weekly%2028-day"

        self.__linkRecursivity(baseLink, self.__browser5Days, "weekly-28days", 2)

    def getForecastWeeklyAll(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\quarterly%2018-month"

        self.__linkRecursivity(baseLink, self.__browser5Days, "18months")

    def getForecastWeeklyLast(self):
        baseLink = "https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=\load%20forecast\quarterly%2018-month"

        self.__linkRecursivity(baseLink, self.__browser5Days, "18months", 2)

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
        # Show download progress
        profile.set_preference("browser.download.manager.showWhenStarting", True)

        option.profile = profile
        self.__browser5Days = webdriver.Firefox(options=option)
        self.__browserHourly = webdriver.Firefox(options=option)
        self.__browserWeekly = webdriver.Firefox(options=option)
        self.__browser18Months = webdriver.Firefox(options=option)


    def quitBrowser(self):
        self.__browser5Days.quit()
        self.__browserHourly.quit()
        self.__browserWeekly.quit()
        self.__browser18Months.quit()
