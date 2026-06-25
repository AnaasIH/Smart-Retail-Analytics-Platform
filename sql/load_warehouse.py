import os
import pandas as pd
import pyodbc

def main():
    # 1. Database Connection Setup
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=RetailDataWarehouse;"
        "UID=sa;"
        "PWD=YourStrong@Password123"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("🔌 Successfully connected to the Data Warehouse...")

        # 2. Read and Preprocess Raw Data
        print("📖 Reading and preparing the raw data file...")
        
        # Smart read: auto-detects delimiter, skips bad lines, and handles encoding
        raw_df = pd.read_csv("data/raw/online-retail.csv", sep=None, engine='python', on_bad_lines='skip', encoding='utf-8-sig')
        
        # Clean missing or empty InvoiceDates
        raw_df = raw_df.dropna(subset=['InvoiceDate'])
        if raw_df['InvoiceDate'].dtype == 'object':
            raw_df['InvoiceDate'] = raw_df['InvoiceDate'].astype(str).str.strip()
            raw_df = raw_df[raw_df['InvoiceDate'] != '']
            
        # Apply strict data cleaning filters (aligned with Spark pipeline)
        raw_df = raw_df[~raw_df['InvoiceNo'].astype(str).str.startswith('C')]
        raw_df = raw_df[(raw_df['Quantity'] > 0) & (raw_df['UnitPrice'] > 0)]
        raw_df = raw_df.dropna(subset=['CustomerID', 'StockCode'])
        
        raw_df['CustomerID'] = raw_df['CustomerID'].astype(int)
        raw_df['OrderDate'] = pd.to_datetime(raw_df['InvoiceDate']).dt.date
        raw_df['SalesAmount'] = round(raw_df['Quantity'] * raw_df['UnitPrice'], 2)
        
        # 3. Process and Populate DimDate
        print("📅 Checking date range and populating DimDate...")
        min_date = pd.to_datetime(raw_df['OrderDate']).min()
        max_date = pd.to_datetime(raw_df['OrderDate']).max()
        print(f"   ➔ Detected Date Range: From {min_date.date()} to {max_date.date()}")
        
        date_list = pd.date_range(start=min_date, end=max_date)
        batch_dates = []
        for dt in date_list:
            date_key = int(dt.strftime("%Y%m%d"))
            cursor.execute("SELECT 1 FROM DimDate WHERE DateKey = ?", date_key)
            if not cursor.fetchone():
                batch_dates.append((
                    date_key, dt.date(), dt.year, (dt.month - 1) // 3 + 1, 
                    dt.month, dt.strftime("%B"), dt.day, dt.strftime("%A")
                ))
                
        if batch_dates:
            cursor.executemany("""
                INSERT INTO DimDate (DateKey, FullDate, Year, Quarter, Month, MonthName, Day, DayOfWeek)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_dates)
            conn.commit()
            print(f"✅ Inserted {len(batch_dates)} new days into DimDate.")

        # 4. Populate DimCustomer
        print("👥 Loading customers into DimCustomer...")
        df_cust = raw_df[['CustomerID', 'Country']].drop_duplicates()
        for _, row in df_cust.iterrows():
            cursor.execute("SELECT 1 FROM DimCustomer WHERE CustomerID = ?", int(row['CustomerID']))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO DimCustomer (CustomerID, CustomerName, Country)
                    VALUES (?, ?, ?)
                """, int(row['CustomerID']), f"Customer_{int(row['CustomerID'])}", row['Country'])
        conn.commit()

        # 5. Populate DimProduct
        print("📦 Loading products into DimProduct...")
        df_prod = raw_df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates(subset=['StockCode'])
        for _, row in df_prod.iterrows():
            product_id = str(row['StockCode'])
            product_name = str(row['Description'])[:255] if pd.notnull(row['Description']) else "Unknown Product"
            
            cursor.execute("SELECT 1 FROM DimProduct WHERE ProductID = ?", product_id)
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO DimProduct (ProductID, ProductName, UnitPrice)
                    VALUES (?, ?, ?)
                """, product_id, product_name, float(row['UnitPrice']))
        conn.commit()

        # 6. Populate FactSales (Using Batch Inserts for Performance)
        print("💰 Mapping surrogate keys and preparing FactSales...")
        
        # Cache dimensions lookup maps in memory for blazing fast mapping
        cursor.execute("SELECT CustomerID, CustomerKey FROM DimCustomer")
        cust_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT ProductID, ProductKey FROM DimProduct")
        prod_map = {row[0]: row[1] for row in cursor.fetchall()}

        batch_records = []
        for _, row in raw_df.iterrows():
            cust_key = cust_map.get(int(row['CustomerID']))
            prod_key = prod_map.get(str(row['StockCode']))
            
            try:
                date_key = int(pd.to_datetime(row['OrderDate']).strftime("%Y%m%d"))
            except:
                continue # Skip row if there is an unexpected parsing error
                
            order_id = str(row['InvoiceNo'])

            if cust_key and prod_key:
                batch_records.append((order_id, cust_key, prod_key, date_key, int(row['Quantity']), float(row['SalesAmount'])))

        print(f"🚀 Shipping {len(batch_records)} records to FactSales...")
        if batch_records:
            cursor.executemany("""
                INSERT INTO FactSales (OrderID, CustomerKey, ProductKey, DateKey, Quantity, SalesAmount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, batch_records)
            conn.commit()

        print("🎉 Data Warehouse successfully populated with high performance!")

    except Exception as e:
        print(f"❌ Error during ETL execution: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()