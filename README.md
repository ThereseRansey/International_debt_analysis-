# International Debt Analysis

An end-to-end data analytics project analyzing World Bank International Debt Statistics (IDS) data — covering data cleaning, exploratory data analysis, SQL database design, an interactive SQL query explorer, and a Power BI dashboard.

##  Project Overview

This project builds a complete data analytics pipeline to understand global external debt patterns:

- **120 countries** and **576 debt-related indicators** from the World Bank IDS dataset
- Data spanning **2000–2024**
- Insights on country-wise debt distribution, top/bottom debtor nations, indicator-wise breakdowns, and long-term debt trends


> **Note:** `DebtData_table.csv` (~1.37M rows) is not included in this repository due to file size. Run `notebooks/data_cleaning_and_EDA.ipynb` to regenerate it from the raw source files.

##  Tech Stack

| Layer | Tool |
|---|---|
| Data Cleaning & EDA | Python (Pandas, Matplotlib, Seaborn, Plotly) in Google Colab |
| Database | MySQL |
| SQL Query Interface | Streamlit + `mysql-connector-python` |
| Dashboard | Power BI |

##  Data Pipeline

1. **Data Collection** — Raw CSVs from the World Bank International Debt Statistics dataset (main data + country/series/footnote metadata)
2. **Data Cleaning & Preprocessing**
   - Removed duplicate and broken rows
   - Dropped irrelevant columns
   - Reshaped from wide (year-per-column) to long/tidy format
   - Forward-filled and backward-filled missing values within each country + indicator series
   - Filtered out World Bank regional/income aggregate rows (e.g. "Sub-Saharan Africa" totals) from country-level analysis
3. **Exploratory Data Analysis** — Country-wise debt distribution, top/bottom debtor countries, indicator impact (debt-to-GNI ratio), correlation analysis, and regional/income-group comparisons
4. **Database Design** — Three normalized MySQL tables (`Countries`, `Indicators`, `DebtData`) with primary and foreign key relationships
5. **SQL Analysis** — 30 analytical queries (10 basic, 10 intermediate, 10 advanced) covering aggregations, rankings, window functions, and views
6. **Visualization & Reporting** — Power BI dashboard with KPI cards, country/indicator/region breakdowns, and trend analysis over time

##  How to Run

### 1. Data Cleaning & EDA
Open `notebooks/data_cleaning_and_EDA.ipynb` in Google Colab or Jupyter, upload the raw World Bank CSVs, and run all cells. This produces the cleaned `Countries_table.csv`, `Indicators_table.csv`, and `DebtData_table.csv`.

### 2. Set Up the Database
```bash
mysql -u root -p < sql/create_schema.sql
python sql/load_data_to_mysql.py
```
Update the MySQL password in `load_data_to_mysql.py` before running.

### 3. Run the Streamlit SQL Explorer
```bash
pip install streamlit mysql-connector-python pandas
streamlit run streamlit_app/app.py
```
Update the MySQL password in `app.py` before running. Opens at `http://localhost:8501`.

### 4. Open the Power BI Dashboard
Open `powerbi/international_debt.pbix` in Power BI Desktop. Requires the MySQL Connector/NET driver installed, and a live connection to your local MySQL database (`international_debt`).

## Key Insights

- **China** holds the highest total external debt in absolute terms (~$2.45T in 2023), nearly 4x the next-highest country (India).
- Global external debt has grown roughly **4x** since 2000, from ~$1.9T to ~$8.8T, with a temporary dip around 2015.
- **East Asia & Pacific** carries the largest regional debt burden overall.
- Debt is highly concentrated — a small number of countries account for a disproportionate share of global debt (right-skewed distribution).

##  Database Schema

| Table | Key Columns |
|---|---|
| `Countries` | `country_code` (PK), `country_name`, `region`, `income_group` |
| `Indicators` | `series_code` (PK), `series_name`, `topic` |
| `DebtData` | `debt_id` (PK), `country_code` (FK), `series_code` (FK), `year`, `value` |

## Data Source

[World Bank International Debt Statistics (IDS)](https://databank.worldbank.org/source/international-debt-statistics)

