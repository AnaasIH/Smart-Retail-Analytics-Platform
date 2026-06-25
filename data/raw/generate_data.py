import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

os.makedirs('data/raw', exist_ok=True)

np.random.seed(42)
num_customers = 100
num_products = 20
num_orders = 500

# 1. Customers Data
customers = {
    'CustomerID': range(1, num_customers + 1),
    'Name': [f'Customer_{i}' for i in range(1, num_customers + 1)],
    'Gender': np.random.choice(['Male', 'Female'], num_customers),
    'Age': np.random.randint(18, 70, num_customers),
    'City': np.random.choice(['Cairo', 'Riyadh', 'Dubai', 'Casablanca', 'Amman'], num_customers),
    'Country': np.random.choice(['Egypt', 'KSA', 'UAE', 'Morocco', 'Jordan'], num_customers)
}
df_customers = pd.DataFrame(customers)
# إضافة قيم فارغة (Nulls) عمداً لاختبار PySpark لاحقاً
df_customers.loc[df_customers['CustomerID'].sample(2).index, 'CustomerID'] = np.nan
df_customers.to_csv('data/raw/customers.csv', index=False)

# 2. Products Data
products = {
    'ProductID': range(1, num_products + 1),
    'ProductName': [f'Product_{i}' for i in range(1, num_products + 1)],
    'Category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Books'], num_products),
    'Brand': np.random.choice(['Brand_A', 'Brand_B', 'Brand_C'], num_products),
    'UnitPrice': np.round(np.random.uniform(10, 500, num_products), 2)
}
df_products = pd.DataFrame(products)
df_products.to_csv('data/raw/products.csv', index=False)

# 3. Orders Data
start_date = datetime(2026, 1, 1)
order_dates = [start_date + timedelta(days=int(np.random.randint(0, 150))) for _ in range(num_orders)]

orders = {
    'OrderID': range(1001, 1001 + num_orders),
    'CustomerID': np.random.choice(range(1, num_customers + 1), num_orders),
    'ProductID': np.random.choice(range(1, num_products + 1), num_orders),
    'Quantity': np.random.randint(-2, 10, num_orders), # قيم سالبة عمداً لاختبار التنظيف
    'OrderDate': [d.strftime('%Y-%m-%d') for d in order_dates],
    'SalesAmount': np.random.uniform(-50, 2000, num_orders) # قيم سالبة عمداً
}
df_orders = pd.DataFrame(orders)
df_orders.to_csv('data/raw/orders.csv', index=False)

# 4. Inventory Data
inventory = {
    'ProductID': range(1, num_products + 1),
    'StockQuantity': np.random.randint(5, 150, num_products),
    'LastUpdateDate': datetime.now().strftime('%Y-%m-%d')
}
df_inventory = pd.DataFrame(inventory)
df_inventory.to_csv('data/raw/inventory.csv', index=False)

print("✅ تم إنشاء الملفات الأربعة بنجاح داخل مجلد data/raw/")