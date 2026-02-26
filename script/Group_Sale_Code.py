# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 10:08:43 2026

@author: bills
"""

import pandas as pd

# Load the full dataset (2021–2025) from OPS CSV
# We load the raw OPS export as a pandas DataFrame.

df = pd.read_csv('Origin_all_data.csv',dtype={"Customer ID":"string"})

# STEP 2) Parse the "Date Bought" column into a proper datetime format
# ============================================================
# The raw date values may contain extra spaces (e.g. "2/1/2021  12:00:00 am").
# We standardize the spacing first, then convert to datetime.
# If a date cannot be parsed, it will become NaT (missing date).
s = df["Date Bought"].astype(str).str.strip()
s = s.str.replace(r"\s+", " ", regex=True)

df["Date Bought_parsed"] = pd.to_datetime(
    s,
    dayfirst=True,  # Use day-first format (dd/mm/yyyy). Change to False if needed.
    errors="coerce" # Invalid dates become NaT instead of crashing the code
)

# Quick check: how many dates failed to parse?
print("Date parsing failure rate:", df["Date Bought_parsed"].isna().mean())
print(df[["Date Bought", "Date Bought_parsed"]].head(10))

# Create a "Line_Amount" column for each row (exclude GST basis)
# Each row represents a purchased item / session line.
# We calculate the value of that line as:
# Line_Amount = Session Bought × Session Price
df['Line_Amount'] = df['Session Bought'] * df['Session Price']

#Combine multiple purchases made by the SAME customer on the SAME date
# Business rule: If a customer buys multiple times on the same day,
# we treat it as ONE purchase event (1 visit/day).
# Therefore, we sum all Line_Amount within the same Customer ID + Date.

df_daily = df.groupby(['Customer ID', 'Date Bought_parsed'])['Line_Amount'].sum().reset_index()
print("The Original number of rows", len(df))
print("The number of rows after Groupby", len(df_daily))


# Find each customer's first purchase date
# For each Customer ID, we take the earliest purchase date as the First Purchase Date.
first_purchases = df_daily.groupby('Customer ID')['Date Bought_parsed'].min().reset_index()
first_purchases.columns = ['Customer ID', 'First_Purchase_Date']

# Define the target customer cohort (First Purchase on/before 30 Sep 2024)
# Here We only include customers whose FIRST purchase date is on or before 2024-09-30.
# Reason: This ensures each customer has enough follow-up time (up to 15 months)
# to observe repeat purchases using the available data range.
target_customers = first_purchases[first_purchases['First_Purchase_Date'] <= '2024-09-30']

# Keep ALL purchase records for the target customers (including future years)
# After selecting the eligible customers, we bring back all their purchase records.
# This allows us to analyze repeat purchases after the first purchase date.
final_analysis_data = pd.merge(target_customers, df_daily, on='Customer ID', how='inner')

# Summary Check(how many customers are included)
print(f"Total customers in raw data (unique Customer ID):  {first_purchases['Customer ID'].nunique()}")
print(f"Customers in target cohort (First Purchase <= 2024-09-30):{target_customers['Customer ID'].nunique()}")

import numpy as np
import pandas as pd

# Attach each customer's first purchase date to daily purchase records
# daily = each customer's daily purchase amount + their first purchase date
daily = pd.merge(df_daily, target_customers, on="Customer ID", how="inner")

# Get the purchase amount on the first purchase date
# ============================================================
# First_Amount = total spending on the customer's first purchase day
first_amount = daily[daily["Date Bought_parsed"] == daily["First_Purchase_Date"]] \
    .groupby("Customer ID")["Line_Amount"].sum().reset_index()
first_amount.columns = ["Customer ID", "First_Amount"]


# Find the first repeat purchase AFTER the first purchase date
# ============================================================
# Repeat 1 = the earliest purchase day after the first purchase day
after_first = daily[daily["Date Bought_parsed"] > daily["First_Purchase_Date"]].copy()

repeat1 = after_first.sort_values(["Customer ID", "Date Bought_parsed"]) \
    .groupby("Customer ID").first().reset_index()

repeat1 = repeat1[["Customer ID", "Date Bought_parsed", "Line_Amount"]]
repeat1.columns = ["Customer ID", "Repeat1_Date", "Repeat1_Amount"]

# ============================================================
# Build a customer-level table (1 row per customer)
customer_level = pd.merge(target_customers, first_amount, on="Customer ID", how="left")
customer_level = pd.merge(customer_level, repeat1, on="Customer ID", how="left")

# Check if Repeat #1 happened within each time window
# ============================================================
# If Repeat1_Date is missing (NaT), it means no repeat purchase.
customer_level["Repeat_6m"]  = customer_level["Repeat1_Date"] <= (customer_level["First_Purchase_Date"] + pd.DateOffset(months=6))
customer_level["Repeat_12m"] = customer_level["Repeat1_Date"] <= (customer_level["First_Purchase_Date"] + pd.DateOffset(months=12))
customer_level["Repeat_15m"] = customer_level["Repeat1_Date"] <= (customer_level["First_Purchase_Date"] + pd.DateOffset(months=15))

# If repeat1_Date is Null then turn to False，which aligns with the definition of "no repurchase"

# 6) Calculate the direction of amount change（only valid if Repeat1 is not NULL）
customer_level["Amount_Change"] = customer_level["Repeat1_Amount"] - customer_level["First_Amount"]
customer_level["Increased"] = customer_level["Amount_Change"] > 0
customer_level["Decreased"] = customer_level["Amount_Change"] < 0
customer_level["No_Change"] = customer_level["Amount_Change"] == 0

total_customers = customer_level["Customer ID"].nunique()

def window_metrics(window_col):
    repeat_customers = customer_level[customer_level[window_col] == True].copy()
    repeat_count = repeat_customers["Customer ID"].nunique()

    if repeat_count == 0:
        return {
            "Total_Customers": total_customers,
            "Repeat_Customers": 0,
            "Repeat_Rate": 0,
            "Increased_%": np.nan,
            "Decreased_%": np.nan,
            "NoChange_%": np.nan
        }

    increased_pct = (repeat_customers["Increased"].sum() / repeat_count) * 100
    decreased_pct = (repeat_customers["Decreased"].sum() / repeat_count) * 100
    nochange_pct  = (repeat_customers["No_Change"].sum() / repeat_count) * 100


    return {
        "Total_Customers": total_customers,
        "Repeat_Customers": repeat_count,
        "Repeat_Rate": repeat_count / total_customers * 100,
        "Increased_%": increased_pct,
        "Decreased_%": decreased_pct,
        "NoChange_%": nochange_pct
    }

results = pd.DataFrame([
    {"Window": "6 months",  **window_metrics("Repeat_6m")},
    {"Window": "12 months", **window_metrics("Repeat_12m")},
    {"Window": "15 months", **window_metrics("Repeat_15m")},
])
print(results)

# 1) Output KPI Summary
results.to_excel("Repeat_Purchase_KPI_Summary.xlsx", index=False)
results.to_csv("Repeat_Purchase_KPI_Summary.csv", index=False, encoding="utf-8-sig")

print("✅ output：Repeat_Purchase_KPI_Summary.xlsx / .csv")

#%%
# 2)  customer-level repeat details，to check the data accuracy
customer_level.to_excel("Customer_Level_Repeat_Detail.xlsx", index=False)
print("✅ output：Customer_Level_Repeat_Detail.xlsx")
#%%
