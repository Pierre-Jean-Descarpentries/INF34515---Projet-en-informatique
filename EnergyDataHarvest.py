#!/bin/python3

import sys
import requests
import numpy as np
from bs4 import BeautifulSoup

def getNRGData() -> int:
    r = requests.get('https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp')
    htmlParser = BeautifulSoup(r.content, 'html.parser')
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
    for x in range(45, 55):
        data = np.append(data, [dataName[x - 45], float(txt[x])])

    print(data)
    return (0)

sys.exit(getNRGData())
