-- 1. إنشاء قاعدة بيانات مستودع البيانات
CREATE DATABASE RetailDataWarehouse;
GO

USE RetailDataWarehouse;
GO

-- 2. إنشاء جدول أبعاد العملاء (DimCustomer)
CREATE TABLE DimCustomer (
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY, -- المفتاح البديل (Surrogate Key)
    CustomerID INT NOT NULL,                  -- المعرف الأصلي من ملف الـ CSV
    CustomerName VARCHAR(100),
    Gender VARCHAR(20),
    Age INT,
    City VARCHAR(50),
    Country VARCHAR(50),
    RowInsertDate DATETIME DEFAULT GETDATE()  -- وقت إدخال السجل للمتابعة
);
GO

-- 3. إنشاء جدول أبعاد المنتجات (DimProduct)
CREATE TABLE DimProduct (
    ProductKey INT IDENTITY(1,1) PRIMARY KEY,  -- المفتاح البديل (Surrogate Key)
    ProductID INT NOT NULL,                    -- المعرف الأصلي
    ProductName VARCHAR(100),
    Category VARCHAR(50),
    Brand VARCHAR(50),
    UnitPrice DECIMAL(10,2),
    RowInsertDate DATETIME DEFAULT GETDATE()
);
GO

-- 4. إنشاء جدول أبعاد الوقت (DimDate) لخدمة الـ BI والتحليل الزمني
CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,                  -- صيغة تاريخية رقمية مثل (20260624)
    FullDate DATE,
    Year INT,
    Quarter INT,
    Month INT,
    MonthName VARCHAR(20),
    Day INT,
    DayOfWeek VARCHAR(20)
);
GO

-- 5. إنشاء جدول الحقائق المالي (FactSales)
CREATE TABLE FactSales (
    SalesKey INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NOT NULL,
    CustomerKey INT FOREIGN KEY REFERENCES DimCustomer(CustomerKey),
    ProductKey INT FOREIGN KEY REFERENCES DimProduct(ProductKey),
    DateKey INT FOREIGN KEY REFERENCES DimDate(DateKey),
    Quantity INT,
    SalesAmount DECIMAL(12,2),
    RowInsertDate DATETIME DEFAULT GETDATE()
);
GO