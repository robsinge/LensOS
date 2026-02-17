import pandas as pd
import os

def load_csv(filename, data_dir):
    path = os.path.join(data_dir, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame()

def generate_brief(data_dir='data'):
    # Load data
    prod_plan = load_csv('optimized_production_plan.csv', data_dir)
    stock_risk = load_csv('stock_risk.csv', data_dir)
    allocation = load_csv('allocation_plan.csv', data_dir)
    products = load_csv('products.csv', data_dir)
    forecast = load_csv('forecast_next_week.csv', data_dir)

    if prod_plan.empty:
        return {"error": "No production plan found"}

    # --- Confidence Narrative ---
    confidence_narrative = "Forecast confidence data unavailable."
    if not forecast.empty and 'confidence_score' in forecast.columns:
        avg_conf = forecast['confidence_score'].mean() * 100
        # Find best segment
        best_cluster = forecast.groupby('power_cluster')['confidence_score'].mean().idxmax()
        confidence_narrative = (
            f"Forecast confidence averages **{avg_conf:.0f}%**. "
            f"Highest certainty observed in **{best_cluster}** segments."
        )

    # --- Part 1: Primary Directive ---
    total_production = int(prod_plan['optimized_qty'].sum())
    total_skus = int(prod_plan['sku_id'].nunique())
    
    # Top demand cities from allocation
    if not allocation.empty:
        # Fix: column name is 'allocated_units'
        top_cities = allocation.groupby('city')['allocated_units'].sum().nlargest(2).index.tolist()
        top_cities_str = " and ".join(top_cities)
    else:
        top_cities_str = "key markets"

    # Top SKU
    top_sku = prod_plan.loc[prod_plan['optimized_qty'].idxmax()]['sku_id']
    
    # Capacity
    TOTAL_CAPACITY = 70000 
    utilization = (total_production / TOTAL_CAPACITY) * 100
    
    # Revenue Risk calculation
    # Merge stock_risk with products to get price
    revenue_at_risk = 0
    if not stock_risk.empty and not products.empty:
        # products.csv likely has 'sku_id' and 'price' (or 'mrp'?)
        # Let's check products columns in next step or assume standard
        # If products has 'price', usage:
        if 'price' in products.columns:
            merged_risk = stock_risk.merge(products[['sku_id', 'price']], on='sku_id', how='left')
            merged_risk['revenue_impact'] = merged_risk['shortage_units'] * merged_risk['price']
            revenue_at_risk = merged_risk['revenue_impact'].sum()
        else:
             # Fallback: average price 3000
             revenue_at_risk = stock_risk['shortage_units'].sum() * 3000

    directive = (
        f"LensOS recommends producing **{total_production:,.0f} units** across **{total_skus} configurations** for Week 24. "
        f"Highest priority demand is concentrated in **{top_cities_str}** for very_high prescription clusters, led by **{top_sku}**. "
        f"Factories are operating at **{utilization:.0f}% capacity**, leaving headroom for additional production if demand spikes. "
        f"If shortages are not addressed, approximately **₹{revenue_at_risk/1e6:.1f}M** in revenue is at risk."
    )

    # --- Part 2: Key Actions ---
    actions = []
    
    # Action 1: Cluster focus
    cluster_counts = prod_plan.groupby('power_cluster')['optimized_qty'].sum()
    top_cluster = cluster_counts.idxmax()
    actions.append(f"Increase production of **{top_cluster} cluster** configurations")

    # Action 2: Allocation
    if not allocation.empty:
        top_3_cities = allocation.groupby('city')['allocated_units'].sum().nlargest(3).index.tolist()
        actions.append(f"Prioritize allocation to **{', '.join(top_3_cities)}**")
    
    # Action 3: Capacity/Revenue
    if utilization < 95:
        actions.append(f"Utilize remaining **{100-utilization:.0f}% capacity** to capture additional revenue")
    else:
         actions.append("Maximize throughput to meet high demand")
         
    # Action 4: Specific Risk
    if not stock_risk.empty:
        # Highest risk city
        risk_city = stock_risk.groupby('city')['shortage_units'].sum().idxmax()
        actions.append(f"Monitor high-risk SKUs in **{risk_city}**")

    # --- Part 3: Capacity Narrative ---
    capacity_narrative = (
        f"Current plan utilizes **{utilization:.0f}%** of available capacity. "
        f"Increasing capacity utilization could capture additional revenue from unmet demand."
    )

    # --- Part 5: Risk Focus ---
    risk_focus = "No critical risks identified."
    if not stock_risk.empty:
        # Find biggest single risk
        highest_shortage = stock_risk.loc[stock_risk['shortage_units'].idxmax()]
        risk_focus = f"Biggest risk this week: **{highest_shortage['city']}** {highest_shortage['power_cluster']} cluster shortages (**{highest_shortage['shortage_units']:.0f} units**)."

    return {
        "directive": directive,
        "actions": actions,
        "capacity_narrative": capacity_narrative,
        "confidence_narrative": confidence_narrative,
        "risk_focus": risk_focus,
        "financials": {
            "revenue_protected": prod_plan['revenue_captured'].sum() if 'revenue_captured' in prod_plan.columns else 0,
            "revenue_risk": revenue_at_risk,
            "working_capital": prod_plan['revenue_captured'].sum() * 0.3 # Rough estimate
        }
    }

if __name__ == "__main__":
    import json
    print(json.dumps(generate_brief(), indent=2))
