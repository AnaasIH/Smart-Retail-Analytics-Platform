# Smart Retail Analytics Platform 🚀

An end-to-end Data Engineering pipeline that extracts raw retail transaction data, cleanses and processes it, and loads it into a structured SQL Server Data Warehouse ($Star\ Schema$) for business intelligence and reporting via Power BI.

## 🏗️ Architecture Overview
The project implements a modern data warehousing architecture:
* **Data Cleansing:** Automated Python scripts using Pandas to handle anomalies, incorrect custom Excel delimiters, and missing dates ($NaT$).
* **Data Warehouse:** Built on SQL Server containing a Fact table (`FactSales`) and Dimension tables (`DimDate`, `DimCustomer`, `DimProduct`).
* **Automation:** A combined script (`clean_and_run.py`) that handles automatic table truncation and complete reload seamlessly.
* **BI Layer:** Live reporting and dashboards built using Power BI.

## 🛠️ Tech Stack
* **Language:** Python 3.10
* **Data Processing:** Pandas, PySpark (under development)
* **Database:** Microsoft SQL Server
* **Containerization:** Docker & Docker-Compose
* **Orchestration:** Apache Airflow
* **Visualization:** Power BI

## 🏃‍♂️ How to Run the Pipeline
1. Clone the repository.
2. Spin up the infrastructure:
   ```bash
   docker-compose up -d
   Run the automated ETL script to clear the old warehouse and load updated data: python clean_and_run.py
   Open your Power BI dashboard and hit Refresh!
   
