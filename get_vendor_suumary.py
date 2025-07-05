import pandas as pd
import sqlite3
import logging
from ingestion_db import ingest_db


logging.basicConfig(
    filename="logs/get_vendor_summary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",  # FIXED typo here
    filemode="a"
)

def create_vendor_summary(conn):
    #this function will merge different tables tpo get overall summary and adding new columns in the resultant data
    vendor_sales_summary =pd.read_sql_query(""" WITH Freightsummary AS(
    select
        VendorNumber,
        sum(Freight) as FreightCost
    From vendor_invoice
    Group by VendorNumber
),

PurchaseSummary AS (
    select 
        p.VendorNumber,
        p.VendorName,
        p.Brand,
        p.Description,
        p.PurchasePrice,
        pp.Volume,
        pp.Price as Actual_Price,
        sum(p.Quantity) as TotalPurchaseQuantity,
        sum(p.Dollars) as TotalPurchaseDollars
    FROM purchases p
    JOIN purchase_prices pp
        ON p.Brand =pp.Brand
    where p.PurchasePrice>0
    GROUP BY p.VendorNumber, p.VendorName,p.Brand ,p.Description ,p.PurchasePrice, pp.Price, pp.Volume
),

SalesSummary AS(select
    VendorNo,
    Brand,
    Sum(SalesDollars) as TotalSalesDollars,
    Sum(SalesPrice) as TotalSalesPrice,
    Sum(SalesQuantity) as TotalSalesQuantity,
    Sum(ExciseTax) as TotalExciseTax
    FROM sales
    GROUP BY VendorNo,Brand
)

SELECT
    ps.VendorNumber,
    ps.VendorName,
    ps.Brand,
    ps.Description,
    ps.PurchasePrice,
    ps.Actual_Price,
    ps.Volume,
    ps.TotalPurchaseQuantity,
    ps.TotalPurchaseDollars,
    ss.TotalSalesQuantity,
    ss.TotalSalesDollars,
    ss.TotalSalesPrice,
    ss.TotalExciseTax,
    fs.FreightCost
FROM PurchaseSummary ps
LEFT JOIN SalesSummary  ss
    ON ps.VendorNumber=ss.VendorNo
    AND ps.Brand=ss.Brand
LEFT JOIN  Freightsummary fs
    ON ps.VendorNumber=fs.VendorNumber
ORDER BY ps.TotalPurchaseDollars DESC""",conn)
    return vendor_sales_summary

def clean_data(df):
    #changing the datatype to float
    df['Volume']=df['Volume'].astype('float64')

    #filling missing value with 0
    df.fillna(0, inplace=True)

    #removing space from categorial columns
    df['VendorName']= df['VendorName'].str.strip()
    df['Description']= df['Description'].str.strip()

    #Creating new Columns
    df['GrossProfit']=df['TotalSalesDollars']-df['TotalPurchaseDollars']
    df['ProfitMargin'] =df['GrossProfit']/df['TotalSalesDollars']*100
    df['StockTurnover']=df['TotalSalesQuantity']/df['TotalPurchaseQuantity']
    df['SalestoPurchaseRatio']=df['TotalSalesDollars']/df['TotalPurchaseDollars']

    return df

if __name__ == '__main__':
    #creating database Conncetion
    conn = sqlite3.connect('inventory.db')

    logging.info("creating vendor summary table")
    summary_df = create_vendor_summary(conn)
    logging.info(summary_df.head())

    logging.info('cleaning Data-------')
    clean_df =clean_data(summary_df)
    logging.info(clean_df.head())

    logging.info("Ingesting data------")
    ingest_db (clean_df,'vendor_sales_summary',conn)
    logging.info('completed')


    
