import pyodbc
import subprocess

# Database Connection Setup
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=RetailDataWarehouse;"
    "UID=sa;"
    "PWD=YourStrong@Password123;"
)

try:
    print("🧹 Connecting to server to truncate old data...")
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    # Truncate Warehouse tables in correct order to respect Foreign Key constraints
    cursor.execute("TRUNCATE TABLE FactSales;")
    cursor.execute("DELETE FROM DimCustomer;")
    cursor.execute("DELETE FROM DimProduct;")
    cursor.execute("DELETE FROM DimDate;")
    
    cursor.close()
    conn.close()
    print("✅ Warehouse tables successfully truncated!")
    
    print("🚀 Running the pipeline (load_warehouse.py) to load your new data...")
    subprocess.run(["python", "sql/load_warehouse.py"], check=True)
    print("🎉 Success! Your pipeline ran flawlessly.")
    
except Exception as e:
    print(f"❌ Error during execution: {e}")