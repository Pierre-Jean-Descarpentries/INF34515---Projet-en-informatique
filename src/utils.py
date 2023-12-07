import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("appLogger")

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
            print(printColors.HEADER + "Reading file: {}".format(filePath) + printColors.ENDC)
            arr = np.loadtxt(filePath, delimiter=",", dtype=str)
            if (("predictions" in filePath) == False):
                arr = arr[1:]
            return (arr)
        except Exception as error:
            logger.error("Error while opening file: {}\n".format(filePath))
            return (None)

    @staticmethod
    def toDate(baseDate) -> str:
        date = "{}-{}-{} {}:{}:{}".format(baseDate[0:4], baseDate[4:6], baseDate[6:8], baseDate[8:10], baseDate[10:12], baseDate[12:14])
        return (date)
