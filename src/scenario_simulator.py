"""
Scenario Simulation Engine ("What-If" Analysis)
================================================
Allows executives to explore demand / price / capacity changes
and see the impact on revenue and production before committing.
"""

import os
import pandas as pd
import numpy as np

# Re-use capacity optimizer logic
from capacity_optimizer import CapacityOptimizer, TOTAL_DAILY_CAPACITY, PRODUCTION_DAYS


class ScenarioSimulator:
    """Run what-if analysis on demand, price, and capacity."""

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'data'
        )

    # ------------------------------------------------------------------
    def run_scenario(
        self,
        demand_multiplier: float = 1.0,   # 0.8 – 1.2
        price_multiplier: float = 1.0,    # 0.9 – 1.1
        capacity_change_pct: float = 0.0,  # -20 to +20
    ) -> dict:
        """
        Recompute production plan under modified assumptions.

        Returns a dict with baseline vs scenario comparison.
        """
        # --- Load baseline data ---
        forecast  = pd.read_csv(os.path.join(self.data_dir, 'forecast_next_week.csv'))
        products  = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
        production = pd.read_csv(os.path.join(self.data_dir, 'production_plan.csv'))

        # --- Baseline metrics ---
        baseline_demand = float(forecast['predicted_demand'].sum())
        sku_band = products[['sku_id', 'base_cost', 'price_band']].drop_duplicates('sku_id')
        prod_with_price = production.merge(sku_band, on='sku_id', how='left')
        prod_with_price['base_cost'] = prod_with_price['base_cost'].fillna(prod_with_price['base_cost'].median())
        baseline_revenue = float(
            (prod_with_price['recommended_production_qty'] * prod_with_price['base_cost'] * 1.5).sum()
        )
        baseline_capacity = TOTAL_DAILY_CAPACITY * PRODUCTION_DAYS

        # --- Scenario adjustments ---
        # 1. Adjust demand
        scenario_forecast = forecast.copy()
        scenario_forecast['predicted_demand'] *= demand_multiplier

        # 2. Adjusted capacity
        scenario_capacity = int(baseline_capacity * (1 + capacity_change_pct / 100))

        # 3. Recalculate production plan from adjusted forecast
        sku_power_demand = (
            scenario_forecast
            .groupby(['sku_id', 'power_cluster'])['predicted_demand']
            .sum()
            .reset_index()
        )
        sku_power_demand['recommended_production_qty'] = (
            sku_power_demand['predicted_demand'] * 1.15
        ).round().astype(int)

        # 4. Run capacity optimizer on scenario plan
        opt = CapacityOptimizer(data_dir=self.data_dir)
        opt.load_data()
        # Replace production with scenario production
        opt.production = sku_power_demand[['sku_id', 'power_cluster', 'recommended_production_qty']]
        scenario_df = opt.optimise(capacity=scenario_capacity)

        # 5. Adjust revenue by price multiplier
        scenario_df['revenue_captured'] *= price_multiplier
        scenario_df['revenue_lost'] *= price_multiplier

        scenario_revenue = float(scenario_df['revenue_captured'].sum())
        scenario_demand = float(scenario_forecast['predicted_demand'].sum())
        scenario_production = int(scenario_df['optimized_qty'].sum())
        scenario_utilization = round(scenario_production / max(scenario_capacity, 1) * 100, 1)

        result = {
            'baseline': {
                'total_demand': round(baseline_demand, 0),
                'total_production': int(production['recommended_production_qty'].sum()),
                'total_revenue': round(baseline_revenue, 0),
                'capacity': baseline_capacity,
                'utilization_pct': round(
                    int(production['recommended_production_qty'].sum()) / baseline_capacity * 100, 1
                ),
            },
            'scenario': {
                'demand_multiplier': demand_multiplier,
                'price_multiplier': price_multiplier,
                'capacity_change_pct': capacity_change_pct,
                'total_demand': round(scenario_demand, 0),
                'total_production': scenario_production,
                'total_revenue': round(scenario_revenue, 0),
                'capacity': scenario_capacity,
                'utilization_pct': scenario_utilization,
            },
            'delta': {
                'demand_change': round(scenario_demand - baseline_demand, 0),
                'production_change': scenario_production - int(production['recommended_production_qty'].sum()),
                'revenue_change': round(scenario_revenue - baseline_revenue, 0),
                'revenue_change_pct': round(
                    (scenario_revenue - baseline_revenue) / max(baseline_revenue, 1) * 100, 1
                ),
            },
        }

        # Save scenario results
        out_path = os.path.join(self.data_dir, 'scenario_results.csv')
        scenario_df.to_csv(out_path, index=False)

        return result


# ======================================================================
def main():
    print("=" * 60)
    print("  SCENARIO SIMULATION ENGINE")
    print("=" * 60)

    sim = ScenarioSimulator()

    # Example: demand up 10%, price up 5%, capacity up 15%
    result = sim.run_scenario(
        demand_multiplier=1.10,
        price_multiplier=1.05,
        capacity_change_pct=15,
    )

    b = result['baseline']
    s = result['scenario']
    d = result['delta']

    print(f"\n{'Metric':<25} {'Baseline':>15} {'Scenario':>15} {'Delta':>15}")
    print("-" * 72)
    print(f"{'Total Demand':<25} {b['total_demand']:>15,.0f} {s['total_demand']:>15,.0f} {d['demand_change']:>+15,.0f}")
    print(f"{'Total Production':<25} {b['total_production']:>15,} {s['total_production']:>15,} {d['production_change']:>+15,}")
    print(f"{'Total Revenue':<25} {'₹'+str(int(b['total_revenue'])):>15} {'₹'+str(int(s['total_revenue'])):>15} {d['revenue_change_pct']:>+14.1f}%")
    print(f"{'Capacity':<25} {b['capacity']:>15,} {s['capacity']:>15,}")
    print(f"{'Utilization':<25} {b['utilization_pct']:>14.1f}% {s['utilization_pct']:>14.1f}%")
    print("=" * 60)


if __name__ == '__main__':
    main()
