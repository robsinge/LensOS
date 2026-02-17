import pandas as pd
import os

def verify_backend_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    print("\n" + "="*50)
    print("BACKEND DATA VERIFICATION")
    print("="*50)
    
    try:
        production = pd.read_csv(os.path.join(data_dir, 'production_plan.csv'))
        stock_risk = pd.read_csv(os.path.join(data_dir, 'stock_risk.csv'))
        products = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        
        # 1. Total Production
        total_production = int(production['recommended_production_qty'].sum())
        print(f"Total Production: {total_production:,}")
        
        # 2. Total Shortage
        total_shortage = int(stock_risk['shortage_units'].sum())
        print(f"Total Shortage: {total_shortage:,}")
        
        # 3. Revenue Risk
        risk_with_price = stock_risk.merge(products[['sku_id', 'base_cost']], on='sku_id', how='left')
        risk_with_price['revenue_risk'] = risk_with_price['shortage_units'] * (risk_with_price['base_cost'] * 1.5)
        total_revenue_risk = risk_with_price['revenue_risk'].sum()
        print(f"Revenue Risk: ₹{total_revenue_risk:,.2f}")
        
        # 4. Working Capital Freed (Logic from api.py)
        # avg_cost = products['base_cost'].mean()
        # total_inventory_units = total_production + total_shortage
        # working_capital_freed = (total_inventory_units * 0.20) * avg_cost
        
        print("\nFiles verified:")
        print(f"- production_plan.csv: {len(production)} rows")
        print(f"- stock_risk.csv: {len(stock_risk)} rows")
        
    except Exception as e:
        print(f"Error verifying data: {e}")

if __name__ == "__main__":
    verify_backend_data()
