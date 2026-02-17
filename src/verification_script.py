import pandas as pd
import numpy as np
import os

def load_data():
    try:
        forecast = pd.read_csv('data/forecast_next_week.csv')
        production = pd.read_csv('data/production_plan.csv')
        allocation = pd.read_csv('data/allocation_plan.csv')
        stock_risk = pd.read_csv('data/stock_risk.csv')
        inventory = pd.read_csv('data/inventory.csv')
        products = pd.read_csv('data/products.csv')
        return forecast, production, allocation, stock_risk, inventory, products
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None

def validate_data(forecast, production, allocation, stock_risk):
    print("--- Data Validation ---")
    
    # 1. Forecast coverage
    print(f"Forecast rows: {len(forecast)}")
    
    # 2. Production vs Allocation
    # production: recommended_production_qty
    # allocation: allocated_units
    prod_total = production['recommended_production_qty'].sum()
    alloc_total = allocation['allocated_units'].sum()
    print(f"Total Production: {prod_total}")
    print(f"Total Allocation Totals (sum of allocated_units): {alloc_total}")
    
    # Note: Allocation might be per city, while production is global per SKU.
    # Allocation sum should ideally match Production total if all produced is allocated.
    # But usually Allocation <= Production.
    
    if abs(prod_total - alloc_total) < 1.0: 
        print("[Pass] Production matches Allocation totals")
    elif alloc_total < prod_total:
         print(f"[Info] Allocation ({alloc_total}) < Production ({prod_total}). Difference: {prod_total - alloc_total}")
    else:
        print(f"[Fail] Allocation ({alloc_total}) > Production ({prod_total})")

    # 3. Stock risk logic
    # shortage_units logic checking
    # Filter where shortfall > 0
    shortages = stock_risk[stock_risk['shortage_units'] > 0]
    print(f"Stock Risk rows with shortages: {len(shortages)}")
    
    # Check logic: shortage = max(0, demand - stock)
    # stock_risk columns: store_predicted_demand, stock_level, shortage_units
    
    # We take a sample
    sample = shortages.head(5)
    valid_risk = True
    for _, row in sample.iterrows():
        expected_shortage = max(0, row['store_predicted_demand'] - row['stock_level'])
        # Allow small floating point difference
        if abs(row['shortage_units'] - expected_shortage) > 0.01:
             print(f"[Fail] Logic Risk: Demand {row['store_predicted_demand']}, Stock {row['stock_level']}, Expected Shortage {expected_shortage}, Got {row['shortage_units']}")
             valid_risk = False
             
    if valid_risk:
        print("[Pass] Stock risk shortage calculation logic seems correct (on sample)")

def validate_business_logic(forecast, production, allocation, products):
    print("\n--- Business Logic Validation ---")
    
    # 1. Production buffer 1.15
    # Forecast column: predicted_demand
    forecast_sku = forecast.groupby(['sku_id', 'power_cluster'])['predicted_demand'].sum().reset_index()
    
    # Merge with production (sku_id, power_cluster)
    merged = pd.merge(forecast_sku, production, on=['sku_id', 'power_cluster'], how='inner')
    
    merged['ratio'] = merged['recommended_production_qty'] / merged['predicted_demand']
    
    avg_ratio = merged['ratio'].mean()
    print(f"Average Production/Demand Ratio: {avg_ratio:.4f}")
    
    if 1.14 <= avg_ratio <= 1.16:
        print("[Pass] Production buffer is approx 1.15x")
    else:
        print(f"[Fail/Check] Production buffer ratio is {avg_ratio:.4f}. Expected ~1.15")
        
    # 2. Revenue Calculation Check
    if 'projected_revenue' in allocation.columns:
        total_rev = allocation['projected_revenue'].sum()
        print(f"Total Projected Revenue: {total_rev:,.2f}")
    else:
        print("[Fail] 'projected_revenue' column missing in allocation_plan.csv")
        
    # Check if price is available in products to calculate it manually?
    if 'price' in products.columns:
        print("Price column found in products.csv")
    elif 'base_cost' in products.columns:
         print("Only 'base_cost' found in products.csv (no selling price)")
    else:
         print("No price or cost found in products.csv")


def main():
    data = load_data()
    with open('verification_report.txt', 'w') as f:
        if data:
            # Redirect stdout to file
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            try:
                validate_data(*data[:4])
                validate_business_logic(data[0], data[1], data[2], data[5])
            finally:
                sys.stdout = original_stdout
        else:
            f.write("Skipping validation due to missing files.\n")

if __name__ == "__main__":
    main()

