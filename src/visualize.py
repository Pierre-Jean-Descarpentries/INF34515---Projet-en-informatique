import logging
import numpy as np
import pandas as pd
from utils import printColors
import matplotlib.pyplot as plt

logger = logging.getLogger("appLogger")

class Interraction:
    @staticmethod
    def getPredictionType():
        option = input("""Select option (1, 2, 3, 4):
        1) Daily 5-days
        2) Hourly
        3) Weekly 28-days
        4) 18 months""")

        if (option == "1" or option == "2" or option == "3" or option == "4"):
            return (option)
        else:
            print(printColors.FAIL + "Invalid option \"{}\"".format(option) + printColors.ENDC)
        return (None)

    @staticmethod
    def getType():
        option = input("""Select option (1, 2, 3, 4):
        1) Real time data
        2) Interruptions
        3) Archives
        4) Forecast""")

        if (option == "1" or option == "2" or option == "3"):
            return (option)
        elif (option == "4"):
            type = getPredictionTypeprediction()
            if (type == None):
                return (None)
            option += ".{}".format(type)
        else:
            print(printColors.FAIL + "Invalid option \"{}\"".format(option) + printColors.ENDC)
            return (None)

    @staticmethod
    def commands():
        command = None

        try:
            while True:
                command = input("> ").lower()
                if (command == "help"):
                    print(printColors.HEADER + "Availiable commands are:\n- Export\n- Graphic\n" + printColors.ENDC)
                elif (command == "export"):
                    Export.export()
                elif (command == "graphic"):
                    Graph.graph()
                elif (not command and command != ""):
                    print(printColors.FAIL + "Invalid command \"{}\". Use help to get the list of the available commands".format(command) + printColors.ENDC)
        except:
            pass

class Export(Interraction):
    __databaseInstance = None

    def __init__(self, databaseInstance):
        this.__databaseInstance = databaseInstance

    ## Private method to generate the file
    def __generateFile(self, type, year):
        filePath = None
        rows = None

        if (type == "1"):
            ## Real time data
            filePath = "realTimeData-{}.csv".format(year)
        elif (type == "2"):
            ## Interruptions
            filePath = "interruptions-{}.csv".format(year)
        elif (type == "3"):
            ## Archive
            filePath = "informationArchive-{}.csv".format(year)
        elif (type == "4.1"):
            ## Forecast daily
            filePath = "chargePrevisionDaily-{}.csv".format(year)
        elif (type == "4.2"):
            ## Forecast hourly
            filePath = "chargePrevisionHourly-{}.csv".format(year)
        elif (type == "4.3"):
            ## Forecast Weekly
            filePath = "chargePrevisionWeekly-{}.csv".format(year)
        elif (type == "4.4"):
            ## Forecast 18 months
            filePath = "chargePrevisionEighteenMonths-{}.csv".format(year)

        rows = self.__databaseInstance.getValuesFromYear(type, year)
        if (rows != None):
            data = pd.DataFrame(rows)
            data.columns = rows[0].keys()
            data.to_csv(filePath, index=False)

    ## Method to gather the necessary informations to export
    @staticmethod
    def export():
        year = None
        type = getType()

        if (type == None):
            return
        year = input("Desired year: ")
        self.__generateFile(type, year)
        return

class Graph(Interraction):
    __databaseInstance = None

    def __init__(self, databaseInstance):
        this.__databaseInstance = databaseInstance

    ## Helper function used for visualization in the following examples
    def __identify_axes(ax_dict, fontsize=30):
        kw = dict(ha="center", va="center", fontsize=fontsize, color="darkgrey")
        for i, ax in ax_dict.items():
            ax.text(0.5, 0.5, i, transform=ax.transAxes, **kw)

    def __createStackplots(self, graph, values, labels, xLabel="Weeks", yLabel="Charge"):
        graph.xlabel(xLabel)
        graph.ylabel(yLabel)
        fig, ax = graph.subplots()
        ax.stackplot(np.arange(1, 52), values, labels=labels)

    def __createPlots(self, graph, values, xRange=np.arange(1, 52), xLabel="Weeks", yLabel="Charge"):
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        fig, ax = plt.subplots()
        ax.plot(xRange, values)

    def __generateComparison(self, type, years):
        ## Variables declaration
        values = np.array([])
        chargeNBVal = np.array([])
        demandeNBVal = np.array([])
        isoNeVal = np.array([])
        emecVal = np.array([])
        mpsVal = np.array([])
        quebecVal = np.array([])
        novaScotiaVal = np.array([])
        peiVal = np.array([])
        reserveMarginAsyncVal = np.array([])
        reserveMarginSyncVal = np.array([])
        reserveMarginVal = np.array([])

        ## Get the ressources from the database
        for year in years:
            if (type == "1"):
                chargeNBVal = np.vstack(chargeNBVal, this.__databaseInstance.getRealTimeDataValueFromYear("chargeNB", year))
                demandeNBVal = np.vstack(demandeNBVal, this.__databaseInstance.getRealTimeDataValueFromYear("demandeNB", year))
                isoNeVal = np.vstack(isoNeVal, this.__databaseInstance.getRealTimeDataValueFromYear("isoNe", year))
                emecVal = np.vstack(emecVal, this.__databaseInstance.getRealTimeDataValueFromYear("emec", year))
                mpsVal = np.vstack(mpsVal, this.__databaseInstance.getRealTimeDataValueFromYear("mps", year))
                quebecVal = np.vstack(quebecVal, this.__databaseInstance.getRealTimeDataValueFromYear("quebec", year))
                novaScotiaVal = np.vstack(novaScotiaVal, this.__databaseInstance.getRealTimeDataValueFromYear("novaScotia", year))
                peiVal = np.vstack(peiVal, this.__databaseInstance.getRealTimeDataValueFromYear("pei", year))
                reserveMarginAsyncVal = np.vstack(reserveMarginAsyncVal, this.__databaseInstance.getRealTimeDataValueFromYear("reserveMarginAsync10Min", year))
                reserveMarginSyncVal = np.vstack(reserveMarginSyncVal, this.__databaseInstance.getRealTimeDataValueFromYear("reserveMarginSync10Min", year))
                reserveMarginVal = np.vstack(reserveMarginVal, this.__databaseInstance.getRealTimeDataValueFromYear("reserveMargin30Min", year))
            elif (type == "2"):
                ## For the interruptions, we compare the number of interruptions
                values = np.vstack(values, len(this.__databaseInstance.getValuesFromYear(year)))
            else:
                values = np.vstack(values, this.__databaseInstance.getValuesFromYear(year))

        ##Creating the graphs:
        if (type == "1"):
            fig = plt.figure(layout="constrained")
            graphs = fig.subplot_mosaic([
                ["chargeNB", "demandeNB", "isoNe"],
                ["emec", "mps", "quebec"],
                ["reserveMarginAsync10Min", "reserveMarginSync10Min", "reserveMargin30Min"],
                ["novaScotia", "pei"]
            ])
            ## Parametting the graphs
            self.__createStackplots(graphs["chargeNB"], chargeNBVal, years)
            self.__createStackplots(graphs["demandeNB"], demandeNBVal, years)
            self.__createStackplots(graphs["isoNe"], isoNeVal, years)
            self.__createStackplots(graphs["emec"], emecVal, years)
            self.__createStackplots(graphs["mps"], mpsVal, years)
            self.__createStackplots(graphs["quebec"], quebecVal, years)
            self.__createStackplots(graphs["reserveMarginAsync10Min"], reserveMarginAsyncVal, years)
            self.__createStackplots(graphs["reserveMarginSync10Min"], reserveMarginSyncVal, years)
            self.__createStackplots(graphs["reserveMargin30Min"], reserveMarginVal, years)
            self.__createStackplots(graphs["novaScotia"], novaScotiaVal, years)
            self.__createStackplots(graphs["pei"], peiVal, years)
            self.__identify_axes(graphs)
            plt.show()
        elif (type == "2"):
            self.__createPlots(plt, values, xRange=len(values), yLabel="Interruption number")
            plt.show()
        else:
            self.__createStackplots(plt, values, years)
            plt.show()

    def __generateEvolution(self, type, year):
        ## Variables declaration
        values = None
        chargeNBVal = None
        demandeNBVal = None
        isoNeVal = None
        emecVal = None
        mpsVal = None
        quebecVal = None
        novaScotiaVal = None
        peiVal = None
        reserveMarginAsyncVal = None
        reserveMarginSyncVal = None
        reserveMarginVal = None

        ## Get the ressources from the database
        if (type == "1"):
            chargeNBVal = this.__databaseInstance.getRealTimeDataValueFromYear("chargeNB", year)
            demandeNBVal = this.__databaseInstance.getRealTimeDataValueFromYear("demandeNB", year)
            isoNeVal = this.__databaseInstance.getRealTimeDataValueFromYear("isoNe", year)
            emecVal = this.__databaseInstance.getRealTimeDataValueFromYear("emec", year)
            mpsVal = this.__databaseInstance.getRealTimeDataValueFromYear("mps", year)
            quebecVal = this.__databaseInstance.getRealTimeDataValueFromYear("quebec", year)
            novaScotiaVal = this.__databaseInstance.getRealTimeDataValueFromYear("novaScotia", year)
            peiVal = this.__databaseInstance.getRealTimeDataValueFromYear("pei", year)
            reserveMarginAsyncVal = this.__databaseInstance.getRealTimeDataValueFromYear("reserveMarginAsync10Min", year)
            reserveMarginSyncVal = this.__databaseInstance.getRealTimeDataValueFromYear("reserveMarginSync10Min", year)
            reserveMarginVal = this.__databaseInstance.getRealTimeDataValueFromYear("reserveMargin30Min", year)
        elif (type == "2"):
            ## For the interruptions, we compare the number of interruptions
            values = len(this.__databaseInstance.getValuesFromYear(year))
        else:
            values = this.__databaseInstance.getValuesFromYear(year)

        ##Creating the graphs:
        if (type == "1"):
            fig = plt.figure(layout="constrained")
            graphs = fig.subplot_mosaic([
                ["chargeNB", "demandeNB", "isoNe"],
                ["emec", "mps", "quebec"],
                ["reserveMarginAsync10Min", "reserveMarginSync10Min", "reserveMargin30Min"],
                ["novaScotia", "pei"]
            ])
            ## Parametting the graphs
            self.__createPlots(graphs["chargeNB"], chargeNBVal)
            self.__createPlots(graphs["demandeNB"], demandeNBVal)
            self.__createPlots(graphs["isoNe"], isoNeVal)
            self.__createPlots(graphs["emec"], emecVal)
            self.__createPlots(graphs["mps"], mpsVal)
            self.__createPlots(graphs["quebec"], quebecVal)
            self.__createPlots(graphs["reserveMarginAsync10Min"], reserveMarginAsyncVal)
            self.__createPlots(graphs["reserveMarginSync10Min"], reserveMarginSyncVal)
            self.__createPlots(graphs["reserveMargin30Min"], reserveMarginVal)
            self.__createPlots(graphs["novaScotia"], novaScotiaVal)
            self.__createPlots(graphs["pei"], peiVal)
            self.__identify_axes(graphs)
            plt.show()
        elif (type == "2"):
            self.__createPlots(plt, values, xRange=len(values), yLabel="Interruption number")
            plt.show()
        else:
            self.__createPlots(plt, values)
            plt.show()


    @staticmethod
    def graph():
        year = None
        type = None
        mode = input("""Select graph style (1, 2)
        1) Evolution
        2) Comparison""")

        if (option == "1"):
            print("Which data do you want to see the evolution?")
            type = getType()
            if (type == None):
                return
            year = input("Desired year: ")
            self.__generateEvolution(type, year)
        elif (option == "2"):
            print("Which data do you want to compare?")
            type = getType()
            if (type == None):
                return
            years = input("Please enter the differents years separated with spaces you want the comparison to be done: ")
            self.__generateComparison(type, years)
        return
