from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, round, when, current_timestamp
import os

def main():
    # 1. Initialize Spark Session aligned with the new data format
    spark = SparkSession.builder \
        .appName("RealRetailDataCleaning") \
        .getOrCreate()
    
    print("🚀 PySpark session started for real data processing...")

    raw_file = "/opt/airflow/data/raw/online-retail.csv"
    processed_path = "/opt/airflow/data/processed"

    # 2. Read Raw Data
    df = spark.read.csv(raw_file, header=True, inferSchema=True)
    
    print("📊 Total raw rows read before cleaning:", df.count())

    # 3. Data Transformation and Cleaning
    # a. Exclude cancelled or returned orders (InvoiceNo starting with 'C')
    # b. Exclude rows with non-positive Quantity or UnitPrice, or missing CustomerID/StockCode
    # c. Convert InvoiceDate to standard date format and calculate sales amount
    df_cleaned = df \
        .filter(~col("InvoiceNo").startswith("C")) \
        .filter((col("Quantity") > 0) & (col("UnitPrice") > 0)) \
        .dropna(subset=["CustomerID", "StockCode"]) \
        .withColumn("OrderDate", to_date(col("InvoiceDate"), "M/d/yyyy H:mm")) \
        .withColumn("SalesAmount", round(col("Quantity") * col("UnitPrice"), 2))

    print("✅ Total clean and processed rows:", df_cleaned.count())

    # 4. Star Schema Preparation (Dimensions and Facts)
    
    # Extract DimCustomer from real data
    dim_customer = df_cleaned.select("CustomerID", "Country").distinct() \
        .withColumn("CustomerName", col("CustomerID").cast("string")) # Fallback since names aren't in raw file

    # Extract DimProduct
    dim_product = df_cleaned.select("StockCode", "Description", "UnitPrice").distinct() \
        .withColumnRenamed("StockCode", "ProductID") \
        .withColumnRenamed("Description", "ProductName")

    # Extract FactSales
    fact_sales = df_cleaned.select(
        col("InvoiceNo").alias("OrderID"),
        col("CustomerID"),
        col("StockCode").alias("ProductID"),
        col("OrderDate"),
        col("Quantity"),
        col("SalesAmount")
    )

    # 5. Save Outputs in Professional Parquet Format
    print("💾 Saving clean data to processed folder...")
    dim_customer.write.mode("overwrite").parquet(f"{processed_path}/dim_customer")
    dim_product.write.mode("overwrite").parquet(f"{processed_path}/dim_product")
    fact_sales.write.mode("overwrite").parquet(f"{processed_path}/fact_sales")

    print("⭐ Real data processing and storage completed successfully!")
    spark.stop()

if __name__ == "__main__":
    main()