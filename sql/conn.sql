
-- International Debt Analysis - MySQL Schema & Data Import
-- Database: international_debtid


CREATE DATABASE IF NOT EXISTS international_debtid;
USE international_debtid;


-- 1. Create Relational Tables with Keys & Dependencies

DROP TABLE IF EXISTS DebtData;   -- Drop child table first
DROP TABLE IF EXISTS Countries;
DROP TABLE IF EXISTS Indicators;

-- Table: Countries
CREATE TABLE Countries (
    country_code VARCHAR(30) PRIMARY KEY,
    country_name VARCHAR(150) NOT NULL,
    region       VARCHAR(100),
    income_group VARCHAR(100)
);

-- Table: Indicators
CREATE TABLE Indicators (
    series_code VARCHAR(50) PRIMARY KEY,
    series_name VARCHAR(255) NOT NULL,
    topic       VARCHAR(250)
);

-- Table: DebtData (Fact Table)
CREATE TABLE DebtData (
    debt_id      INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(30) NOT NULL,
    series_code  VARCHAR(50) NOT NULL,
    year         INT NOT NULL,
    value        DOUBLE NOT NULL,
    CONSTRAINT fk_country FOREIGN KEY (country_code) REFERENCES Countries(country_code),
    CONSTRAINT fk_series FOREIGN KEY (series_code) REFERENCES Indicators(series_code)
);


-- 2. Data Import (Populate Master Tables First)


-- Enable local file loading session settings
SET GLOBAL local_infile = 1;
SET FOREIGN_KEY_CHECKS = 0; -- Prevents Error 1452 during bulk import

-- Load Countries
LOAD DATA LOCAL INFILE 'C:/Users/there/Downloads/Countries_table.csv'
INTO TABLE Countries
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(country_code, country_name, region, income_group);

-- Load Indicators
LOAD DATA LOCAL INFILE 'C:/Users/there/Downloads/Indicators_table.csv'
INTO TABLE Indicators
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(series_code, series_name, topic);

-- Load Main Fact Table (DebtData)
TRUNCATE TABLE DebtData;

LOAD DATA LOCAL INFILE 'C:/Users/there/Downloads/DebtData_table.csv'
INTO TABLE DebtData
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(debt_id, country_code, series_code, year, value);

SET FOREIGN_KEY_CHECKS = 1; -- Re-enable FK checks after import

-- Verify Row Counts
SELECT COUNT(*) AS total_countries FROM Countries;  -- Expected: 120
SELECT COUNT(*) AS total_indicators FROM Indicators; -- Expected: 574
SELECT COUNT(*) AS total_debt_records FROM DebtData;  -- Expected: 1,376,225

