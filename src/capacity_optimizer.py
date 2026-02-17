"""
Capacity-Constrained Production Optimizer
==========================================
Uses Linear Programming (scipy) to maximize revenue captured
under a finite factory capacity constraint.
"""

import os
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
TOTAL_DAILY_CAPACITY = 10_000   # units per day
PRODUCTION_DAYS = 7
TOTAL_CAPACITY = TOTAL_DAILY_CAPACITY * PRODUCTION_DAYS  # 70,000

# Margin multipliers per price band (higher band → higher margin)
MARGIN_MAP = {
    'low': 1.0,
    'mid': 1.3,
    'high': 1.6,
    'premium': 2.0,
}


class CapacityOptimizer:
    """Optimise production plan under capacity constraint."""

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'data'
        )
        self.production: pd.DataFrame | None = None
        self.products: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    def load_data(self) -> None:
        self.production = pd.read_csv(
            os.path.join(self.data_dir, 'production_plan.csv')
        )
        self.products = pd.read_csv(
            os.path.join(self.data_dir, 'products.csv')
        )

    # ------------------------------------------------------------------
    def optimise(self, capacity: int = TOTAL_CAPACITY) -> pd.DataFrame:
        """Run LP optimisation.

        Decision variables:  x_i  = production qty for SKU-power combo i
        Objective:           maximise  sum( margin_i * x_i )
        Constraints:         sum( x_i ) <= capacity
                             0 <= x_i <= recommended_qty_i   (upper bound)
        """
        if self.production is None:
            self.load_data()

        df = self.production.copy()

        # Merge price-band from products to get margin weight
        sku_band = self.products[['sku_id', 'price_band', 'base_cost']].drop_duplicates('sku_id')
        df = df.merge(sku_band, on='sku_id', how='left')
        df['price_band'] = df['price_band'].fillna('mid')
        df['base_cost'] = df['base_cost'].fillna(df['base_cost'].median())
        df['margin'] = df['price_band'].map(MARGIN_MAP).fillna(1.0) * df['base_cost']

        n = len(df)
        recommended = df['recommended_production_qty'].values.astype(float)
        margins = df['margin'].values.astype(float)

        # linprog MINIMISES, so negate margins to maximise
        c = -margins

        # Inequality constraint: sum(x) <= capacity  → A_ub @ x <= b_ub
        A_ub = np.ones((1, n))
        b_ub = np.array([capacity])

        # Bounds: 0 <= x_i <= recommended_i
        bounds = [(0, rec) for rec in recommended]

        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

        if not result.success:
            print(f"⚠  Optimisation warning: {result.message}")
            df['optimized_qty'] = recommended
        else:
            df['optimized_qty'] = np.round(result.x).astype(int)

        total_optimized = df['optimized_qty'].sum()
        df['capacity_utilization_pct'] = round(total_optimized / capacity * 100, 1)

        # Revenue calculations
        df['revenue_captured'] = df['optimized_qty'] * df['base_cost'] * 1.5
        df['revenue_lost'] = (recommended - df['optimized_qty']) * df['base_cost'] * 1.5

        self.result_df = df
        return df

    # ------------------------------------------------------------------
    def save(self, df: pd.DataFrame | None = None) -> str:
        df = df if df is not None else self.result_df
        out_cols = [
            'sku_id', 'power_cluster', 'recommended_production_qty',
            'optimized_qty', 'capacity_utilization_pct',
            'price_band', 'margin', 'revenue_captured', 'revenue_lost',
        ]
        out_path = os.path.join(self.data_dir, 'optimized_production_plan.csv')
        df[out_cols].to_csv(out_path, index=False)
        return out_path

    # ------------------------------------------------------------------
    def summary(self, df: pd.DataFrame | None = None) -> dict:
        df = df if df is not None else self.result_df
        total_optimized = int(df['optimized_qty'].sum())
        total_recommended = int(df['recommended_production_qty'].sum())
        capacity = TOTAL_CAPACITY
        utilization = round(total_optimized / capacity * 100, 1)
        revenue_captured = float(df['revenue_captured'].sum())
        revenue_lost = float(df['revenue_lost'].sum())

        return {
            'total_capacity': capacity,
            'total_optimized': total_optimized,
            'total_recommended': total_recommended,
            'capacity_utilization_pct': utilization,
            'revenue_captured': revenue_captured,
            'revenue_lost': revenue_lost,
            'units_cut': total_recommended - total_optimized,
        }


# ======================================================================
def main():
    print("=" * 60)
    print("  CAPACITY-CONSTRAINED PRODUCTION OPTIMIZER")
    print("=" * 60)

    opt = CapacityOptimizer()
    opt.load_data()
    df = opt.optimise()
    path = opt.save(df)
    s = opt.summary(df)

    print(f"\n✓ Optimised plan saved to: {path}")
    print(f"\n  Total Capacity:      {s['total_capacity']:>10,} units")
    print(f"  Recommended (raw):   {s['total_recommended']:>10,} units")
    print(f"  Optimised (capped):  {s['total_optimized']:>10,} units")
    print(f"  Capacity Used:       {s['capacity_utilization_pct']:>9}%")
    print(f"  Revenue Captured:    ₹{s['revenue_captured']:>12,.0f}")
    print(f"  Revenue Lost:        ₹{s['revenue_lost']:>12,.0f}")
    print(f"  Units Cut:           {s['units_cut']:>10,}")
    print("=" * 60)


if __name__ == '__main__':
    main()
