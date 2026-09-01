"""
Streamlit app: Interactive SQL Query Explorer
International Debt Analysis Project
"""

import streamlit as st
import pandas as pd
import mysql.connector

# Page config
st.set_page_config(page_title="International Debt - SQL QUERIES", layout="wide")

# Database connection with fallback handling
def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True
        )
    except KeyError:
        st.error("Missing `.streamlit/secrets.toml` file or `[mysql]` configuration block!")
        return None
    except Exception as e:
        st.error(f"Failed to connect to MySQL database: {e}")
        return None

def run_query(query):
    conn = get_connection()
    if conn:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return None

# All 30 queries organized by level
QUERIES = {
    "Basic Queries": {
        "1. Retrieve all distinct country names": "SELECT DISTINCT country_name FROM Countries;",
        "2. Count total number of countries available": "SELECT COUNT(*) AS total_countries FROM Countries;",
        "3. Find total number of indicators": "SELECT COUNT(*) AS total_indicators FROM Indicators;",
        "4. Display first 10 records of the dataset": "SELECT * FROM DebtData LIMIT 10;",
        "5. Calculate total global debt": "SELECT SUM(value) AS total_global_debt FROM DebtData;",
        "6. List all unique indicator names": "SELECT DISTINCT series_name FROM Indicators;",
        "7. Number of records for each country": """
            SELECT c.country_name, COUNT(*) AS record_count
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY record_count DESC;
        """,
        "8. Display records where debt > 1 billion USD": "SELECT * FROM DebtData WHERE value > 1000000000 LIMIT 500;",
        "9. Min, max and average debt values": "SELECT MIN(value) AS min_debt, MAX(value) AS max_debt, AVG(value) AS avg_debt FROM DebtData;",
        "10. Count total number of records in the dataset": "SELECT COUNT(*) AS total_records FROM DebtData;",
    },
    "Intermediate Level": {
        "1. Total debt for each country": """
            SELECT c.country_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY total_debt DESC;
        """,
        "2. Top 10 countries with highest total debt": """
            SELECT c.country_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY total_debt DESC LIMIT 10;
        """,
        "3. Average debt per country": """
            SELECT c.country_name, AVG(d.value) AS avg_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY avg_debt DESC;
        """,
        "4. Total debt for each indicator": """
            SELECT i.series_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Indicators i ON d.series_code = i.series_code
            GROUP BY i.series_name
            ORDER BY total_debt DESC;
        """,
        "5. Indicator contributing highest total debt": """
            SELECT i.series_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Indicators i ON d.series_code = i.series_code
            GROUP BY i.series_name
            ORDER BY total_debt DESC LIMIT 1;
        """,
        "6. Country with the lowest total debt": """
            SELECT c.country_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY total_debt ASC LIMIT 1;
        """,
        "7. Total debt per country and indicator combination": """
            SELECT c.country_name, i.series_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            JOIN Indicators i ON d.series_code = i.series_code
            GROUP BY c.country_name, i.series_name
            ORDER BY total_debt DESC LIMIT 500;
        """,
        "8. Count how many indicators each country has": """
            SELECT c.country_name, COUNT(DISTINCT d.series_code) AS indicator_count
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY indicator_count DESC;
        """,
        "9. Countries whose total debt is above global average": """
            SELECT country_name, total_debt
            FROM (
                SELECT c.country_name, SUM(d.value) AS total_debt
                FROM DebtData d
                JOIN Countries c ON d.country_code = c.country_code
                GROUP BY c.country_name
            ) AS country_totals
            WHERE total_debt > (
                SELECT AVG(total_debt) FROM (
                    SELECT SUM(value) AS total_debt FROM DebtData GROUP BY country_code
                ) AS avg_calc
            )
            ORDER BY total_debt DESC;
        """,
        "10. Rank countries based on total debt": """
            SELECT c.country_name,
                   SUM(d.value) AS total_debt,
                   RANK() OVER (ORDER BY SUM(d.value) DESC) AS debt_rank
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name;
        """,
    },
    "Advanced Level": {
        "1. Top 5 indicators contributing most to global debt": """
            SELECT i.series_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Indicators i ON d.series_code = i.series_code
            GROUP BY i.series_name
            ORDER BY total_debt DESC LIMIT 5;
        """,
        "2. Percentage contribution of each country": """
            SELECT c.country_name,
                   SUM(d.value) AS total_debt,
                   ROUND(SUM(d.value) * 100.0 / (SELECT SUM(value) FROM DebtData), 4) AS pct_of_global_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY pct_of_global_debt DESC;
        """,
        "3. Top 3 countries for each indicator based on debt": """
            SELECT series_name, country_name, total_debt, rnk
            FROM (
                SELECT i.series_name, c.country_name,
                       SUM(d.value) AS total_debt,
                       RANK() OVER (PARTITION BY i.series_name ORDER BY SUM(d.value) DESC) AS rnk
                FROM DebtData d
                JOIN Countries c ON d.country_code = c.country_code
                JOIN Indicators i ON d.series_code = i.series_code
                GROUP BY i.series_name, c.country_name
            ) ranked
            WHERE rnk <= 3
            ORDER BY series_name, rnk LIMIT 500;
        """,
        "4. Difference between max and min debt for each country": """
            SELECT c.country_name, MAX(d.value) - MIN(d.value) AS debt_range
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY debt_range DESC;
        """,
        "5. Top 10 countries with highest debt": """
            SELECT c.country_name, SUM(d.value) AS total_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            GROUP BY c.country_name
            ORDER BY total_debt DESC LIMIT 10;
        """,
        "6. Categorize countries: High / Medium / Low debt": """
            SELECT country_name, total_debt,
                CASE
                    WHEN total_debt >= 100000000000 THEN 'High Debt'
                    WHEN total_debt >= 10000000000  THEN 'Medium Debt'
                    ELSE 'Low Debt'
                END AS debt_category
            FROM (
                SELECT c.country_name, SUM(d.value) AS total_debt
                FROM DebtData d
                JOIN Countries c ON d.country_code = c.country_code
                GROUP BY c.country_name
            ) t
            ORDER BY total_debt DESC;
        """,
        "7. Cumulative debt per country": """
            SELECT c.country_name, d.year, d.value,
                   SUM(d.value) OVER (PARTITION BY c.country_name ORDER BY d.year) AS cumulative_debt
            FROM DebtData d
            JOIN Countries c ON d.country_code = c.country_code
            WHERE d.series_code = 'DT.DOD.DECT.CD'
            ORDER BY c.country_name, d.year LIMIT 500;
        """,
        "8. Indicators where average debt is higher than overall average": """
            SELECT i.series_name, AVG(d.value) AS avg_indicator_debt
            FROM DebtData d
            JOIN Indicators i ON d.series_code = i.series_code
            GROUP BY i.series_name
            HAVING AVG(d.value) > (SELECT AVG(value) FROM DebtData)
            ORDER BY avg_indicator_debt DESC;
        """,
        "9. Countries contributing morethan 5% of global debt": """
            SELECT country_name, total_debt, pct_of_global_debt FROM (
                SELECT c.country_name,
                       SUM(d.value) AS total_debt,
                       ROUND(SUM(d.value) * 100.0 / (SELECT SUM(value) FROM DebtData), 4) AS pct_of_global_debt
                FROM DebtData d
                JOIN Countries c ON d.country_code = c.country_code
                GROUP BY c.country_name
            ) t
            WHERE pct_of_global_debt > 5
            ORDER BY pct_of_global_debt DESC;
        """,
        "10. Most dominant indicator for each country": """
            SELECT country_name, series_name, total_debt
            FROM (
                SELECT c.country_name, i.series_name,
                       SUM(d.value) AS total_debt,
                       RANK() OVER (PARTITION BY c.country_name ORDER BY SUM(d.value) DESC) AS rnk
                FROM DebtData d
                JOIN Countries c ON d.country_code = c.country_code
                JOIN Indicators i ON d.series_code = i.series_code
                GROUP BY c.country_name, i.series_name
            ) ranked
            WHERE rnk = 1
            ORDER BY total_debt DESC LIMIT 500;
        """,
    },
}

# Sidebar Navigation (Complexity Level in Sidebar)
st.sidebar.header("Query Navigator")
level = st.sidebar.radio("Select Complexity Level:", list(QUERIES.keys()))

st.sidebar.markdown("---")
st.sidebar.caption("Database: `international_debtid`")
st.sidebar.info("Power BI Dashboard handles visual analytics.")

# Main Dashboard
st.title("International Debt Analysis - SQL Query Explorer")
st.caption("Execute analytical SQL queries interactively against MySQL")

# Query Dropdown in Main Dashboard
query_name = st.selectbox(
    f"Select a query from {level}:", 
    list(QUERIES[level].keys())
)

st.markdown("---")

# Query Details & Execution
st.subheader(f"Selected: {query_name}")
sql_text = QUERIES[level][query_name]

with st.expander("View SQL Statement"):
 st.code(sql_text.strip(), language="sql")

if st.button("Run Query", type="primary"):
    with st.spinner("Executing SQL query..."):
        result = run_query(sql_text)
    
    if result is not None:
        st.success(f"Returned {len(result)} rows")
        st.dataframe(result, use_container_width=True)

        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", csv, "query_result.csv", "text/csv")