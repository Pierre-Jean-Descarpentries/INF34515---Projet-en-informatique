CREATE DATABASE IF NOT EXISTS networkData;

USE networkData;

CREATE TABLE IF NOT EXISTS interruption (
    id              BIGINT UNSIGNED NOT NULL,
    status          VARCHAR(255) NOT NULL,
    debut           DATETIME NOT NULL,
    fin             DATETIME,
    description     TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS realTimeData (
  updateTime                DATETIME DEFAULT CURRENT_TIMESTAMP,
  chargeNB                  INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  demandeNB                 INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  isoNe                     INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  emec                      INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  mps                       INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  quebec                    INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  novaScotia                INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  pei                       INT NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  reserveMarginAsync10Min   INT NOT NULL COMMENT "Marge de réserve d'exploitation non synchrone de 10 min",
  reserveMarginSync10Min    INT NOT NULL COMMENT "Marge de réserve d'exploitation synchrone de 10 min",
  reserveMargin30Min        INT NOT NULL COMMENT "Marge de réserve d'exploitation de 30 min",
  PRIMARY KEY (updateTime)
);

CREATE TABLE IF NOT EXISTS informationArchive (
  id                        VARCHAR(36) DEFAULT (UUID()),
  hours                     DATETIME NOT NULL,
  chargeNB                  VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  demandeNB                 VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  isoNe                     VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  nmisa                     VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  quebec                    VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  novaScotia                VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  pei                       VARCHAR(50) NOT NULL COMMENT "Une valeur positive représente une exportation, une valeur négative une importation.",
  filePath                  VARCHAR(255) NOT NULL COMMENT "Le chemin vers le fichier source",
  lastModified              DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT "La dernière modification de la ligne",
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS chargePrevisionDaily (
  id                        VARCHAR(36) DEFAULT (UUID()),
  hours                     DATETIME NOT NULL,
  prevision                 VARCHAR(50) NOT NULL COMMENT "Valeur prévisionnelle de la consomation.",
  filePath                  VARCHAR(255) NOT NULL COMMENT "Le chemin vers le fichier source",
  lastModified              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "La dernière modification de la ligne",
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS chargePrevisionHourly (
  id                        VARCHAR(36) DEFAULT (UUID()),
  hours                     DATETIME NOT NULL,
  prevision                 VARCHAR(50) NOT NULL COMMENT "Valeur prévisionnelle de la consomation.",
  filePath                  VARCHAR(255) NOT NULL COMMENT "Le chemin vers le fichier source",
  lastModified              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "La dernière modification de la ligne",
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS chargePrevisionEighteenMonths (
  id                        VARCHAR(36) DEFAULT (UUID()),
  hours                     DATETIME NOT NULL,
  prevision                 VARCHAR(50) NOT NULL COMMENT "Valeur prévisionnelle de la consomation.",
  filePath                  VARCHAR(255) NOT NULL COMMENT "Le chemin vers le fichier source",
  lastModified              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "La dernière modification de la ligne",
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS chargePrevisionWeekly (
  id                        VARCHAR(36) DEFAULT (UUID()),
  hours                     DATETIME NOT NULL,
  prevision                 VARCHAR(50) NOT NULL COMMENT "Valeur prévisionnelle de la consomation.",
  filePath                  VARCHAR(255) NOT NULL COMMENT "Le chemin vers le fichier source",
  lastModified              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "La dernière modification de la ligne",
  PRIMARY KEY (id)
);
