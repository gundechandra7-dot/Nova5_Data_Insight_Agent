"""
Script to generate rich multi-format test datasets:
- sales_data.csv
- customer_churn.xlsx (multi-sheet)
- app_metrics.json (nested json)
- sensor_readings.parquet (columnar parquet)
- company_analytics.db (sqlite relational database)
"""

import os
import json
import sqlite3
import numpy as np
import pandas as pd

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Set seed for reproducibility
np.random.seed(42)

# 1. sales_data.csv
n_sales = 500
dates = pd.date_range("2023-01-01", periods=n_sales, freq="D")
categories = np.random.choice(["Electronics", "Home & Kitchen", "Apparel", "Office Supplies", "Books"], n_sales)
regions = np.random.choice(["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"], n_sales)
channels = np.random.choice(["Online", "Retail Store", "Direct Sales", "Distributor"], n_sales)
units = np.random.randint(1, 50, n_sales)
unit_prices = np.random.choice([19.99, 49.99, 120.00, 299.99, 850.00], n_sales)
discounts = np.random.choice([0.0, 0.05, 0.1, 0.15, 0.25], n_sales)
revenue = np.round(units * unit_prices * (1 - discounts), 2)
cost_per_unit = unit_prices * np.random.uniform(0.4, 0.7, n_sales)
profit = np.round(revenue - (units * cost_per_unit), 2)

df_sales = pd.DataFrame({
    "Order_Date": dates,
    "Region": regions,
    "Category": categories,
    "Sales_Channel": channels,
    "Units_Sold": units,
    "Unit_Price": unit_prices,
    "Discount_Rate": discounts,
    "Total_Revenue": revenue,
    "Total_Profit": profit,
})
# Inject some nulls and outliers
df_sales.loc[np.random.choice(n_sales, 10, replace=False), "Discount_Rate"] = np.nan
df_sales.loc[3, "Total_Revenue"] = 45000.0  # outlier

csv_path = os.path.join(SAMPLE_DIR, "sales_data.csv")
df_sales.to_csv(csv_path, index=False)
print(f"Generated: {csv_path}")

# 2. customer_churn.xlsx (multi-sheet)
n_cust = 300
cust_ids = [f"CUST-{1000+i}" for i in range(n_cust)]
genders = np.random.choice(["Female", "Male"], n_cust)
tenures = np.random.randint(1, 72, n_cust)
monthly_charges = np.round(np.random.uniform(20.0, 115.0, n_cust), 2)
contracts = np.random.choice(["Month-to-month", "One year", "Two year"], n_cust)
payment_methods = np.random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], n_cust)
churn_prob = np.where(contracts == "Month-to-month", 0.45, 0.15)
churn = np.where(np.random.rand(n_cust) < churn_prob, "Yes", "No")

df_cust = pd.DataFrame({
    "CustomerID": cust_ids,
    "Gender": genders,
    "Tenure_Months": tenures,
    "Contract_Type": contracts,
    "Payment_Method": payment_methods,
    "Monthly_Charges": monthly_charges,
    "Churn": churn,
})

df_plans = pd.DataFrame({
    "Plan_Name": ["Basic", "Standard", "Premium", "Enterprise"],
    "Monthly_Base_Fee": [25.00, 55.00, 95.00, 150.00],
    "Storage_GB": [50, 200, 1000, 5000],
    "Support_Level": ["Standard", "Standard", "Priority", "24/7 Dedicated"],
})

xlsx_path = os.path.join(SAMPLE_DIR, "customer_churn.xlsx")
with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    df_cust.to_excel(writer, sheet_name="Customers", index=False)
    df_plans.to_excel(writer, sheet_name="Subscription_Plans", index=False)
print(f"Generated: {xlsx_path}")

# 3. app_metrics.json (nested json)
app_data = []
for i in range(60):
    date_str = (pd.Timestamp("2024-01-01") + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
    dau = int(np.random.normal(12000, 1500))
    app_data.append({
        "timestamp": date_str,
        "active_users": dau,
        "performance": {
            "p95_latency_ms": round(float(np.random.normal(140, 20)), 1),
            "crash_rate_pct": round(float(np.random.uniform(0.01, 0.15)), 3),
            "cpu_usage_pct": round(float(np.random.uniform(30.0, 75.0)), 1),
        },
        "engagement": {
            "avg_session_min": round(float(np.random.uniform(8.5, 16.0)), 2),
            "screens_per_session": round(float(np.random.uniform(4.0, 9.5)), 1),
        }
    })

json_path = os.path.join(SAMPLE_DIR, "app_metrics.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"product": "InsightEngineApp", "metrics": app_data}, f, indent=2)
print(f"Generated: {json_path}")

# 4. sensor_readings.parquet (columnar parquet)
n_sensor = 1000
timestamps = pd.date_range("2024-06-01", periods=n_sensor, freq="15min")
sensor_ids = np.random.choice(["SENSOR-A1", "SENSOR-B2", "SENSOR-C3", "SENSOR-D4"], n_sensor)
temps = np.round(np.random.normal(72.5, 4.2, n_sensor), 2)
pressure_psi = np.round(np.random.normal(101.3, 2.5, n_sensor), 2)
vibration_hz = np.round(np.random.uniform(10.0, 55.0, n_sensor), 2)
status = np.where(temps > 82.0, "WARNING", "NORMAL")

df_sensor = pd.DataFrame({
    "Timestamp": timestamps,
    "Sensor_ID": sensor_ids,
    "Temperature_C": temps,
    "Pressure_PSI": pressure_psi,
    "Vibration_Hz": vibration_hz,
    "Machine_Status": status,
})
parquet_path = os.path.join(SAMPLE_DIR, "sensor_readings.parquet")
df_sensor.to_parquet(parquet_path, index=False)
print(f"Generated: {parquet_path}")

# 5. company_analytics.db (sqlite database)
db_path = os.path.join(SAMPLE_DIR, "company_analytics.db")
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_dept = pd.DataFrame({
    "dept_id": [1, 2, 3, 4],
    "dept_name": ["Engineering", "Product", "Sales", "Marketing"],
    "headcount_budget": [40, 15, 30, 20],
})
df_dept.to_sql("departments", conn, index=False)

df_emp = pd.DataFrame({
    "emp_id": [101, 102, 103, 104, 105, 106, 107, 108],
    "name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Ethan Hunt", "Fiona Gallagher", "George Clark", "Hannah Abbott"],
    "dept_id": [1, 1, 2, 3, 3, 4, 1, 4],
    "salary": [135000, 142000, 125000, 110000, 155000, 95000, 160000, 98000],
    "performance_score": [4.5, 4.8, 3.9, 4.2, 4.9, 3.8, 4.7, 4.1],
})
df_emp.to_sql("employees", conn, index=False)

df_pipeline = pd.DataFrame({
    "deal_id": [201, 202, 203, 204, 205, 206],
    "account_name": ["Acme Corp", "Globex", "Initech", "Umbrella LLC", "Wayne Ent", "Stark Ind"],
    "deal_value": [45000, 120000, 30000, 250000, 80000, 500000],
    "stage": ["Won", "Proposal", "Qualified", "Won", "Negotiation", "Won"],
})
df_pipeline.to_sql("sales_pipeline", conn, index=False)
conn.close()
print(f"Generated: {db_path}")
print("All sample datasets generated successfully!")
