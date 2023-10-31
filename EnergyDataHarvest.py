#!/bin/python3

import sys
import requests
import numpy as np
from bs4 import BeautifulSoup

def getNRGData() -> int:
    try:
        r = requests.get("https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp")
        htmlParser = BeautifulSoup(r.content, "html.parser")
        txt = htmlParser.get_text().split('\n')
        data = []
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
        for x in range(45, 56):
            data = np.append(data, [dataName[x - 45], float(txt[x])])

        print(data)
        return (0)
    except Exception:
        print(Exception, file=sys.stderr)
        return (84)

### DATA VALUES (heure d'Atlentique)
### [Numéro d'intéruption, Status, Heure de début, Heure d'arrêt, but]
def getInterrupt() -> int:
    try:
        r = requests.get("https://tso.nbpower.com/Public/fr/outages.aspx")
        htmlParser = BeautifulSoup(r.content, "html.parser")
        txt = htmlParser.table.get_text().split('\n')
        while ("" in txt):
            txt.remove("")
        data = []

        for x in range(5, len(txt), 5):
            while (x + 5 < len(txt) and txt[x + 5].isnumeric() == False):
                txt[x + 4] += "\n" + txt[x + 5]
                txt[x + 5] = ""
                txt.remove("")
            data.insert(0, txt[x:x + 5])
        data.remove([])
        return (0)
    except Exception:
        print(Exception, file=sys.stderr)
        return (84)
