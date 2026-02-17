import pandas as pd
import numpy as np
import os

class ManufacturingRecommendationEngine:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.forecast = None
        self.inventory = None
        self.products = None
        self.stores = None
        self.production_plan = None
        self.allocation_plan = None
        self.stock_risk = None
        self.revenue_opportunity = None
    
    def load_data(self):
        """Load all required datasets"""
        print("Loading datasets...")
        self.forecast = pd.read_csv(os.path.join(self.data_dir, 'forecast_next_week.csv'))
        self.inventory = pd.read_csv(os.path.join(self.data_dir, 'inventory.csv'))
        self.products = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
        self.stores = pd.read_csv(os.path.join(self.data_dir, 'stores.csv'))
        print("✓ Data loaded successfully")
        
        # Display data shapes
        print(f"Forecast: {self.forecast.shape}")
        print(f"Inventory: {self.inventory.shape}")
        print(f"Products: {self.products.shape}")
        print(f"Stores: {self.stores.shape}")
    
    def aggregate_forecast(self):
        """Aggregate forecast to different levels"""
        print("Aggregating forecast data...")
        
        # Total demand per SKU + power cluster (across all cities)
        sku_power_demand = self.forecast.groupby(['sku_id', 'power_cluster'])['predicted_demand'].sum().reset_index()
        sku_power_demand.rename(columns={'predicted_demand': 'total_predicted_demand'}, inplace=True)
        
        # Demand per city + SKU + power cluster
        city_sku_demand = self.forecast.groupby(['city', 'sku_id', 'power_cluster'])['predicted_demand'].sum().reset_index()
        city_sku_demand.rename(columns={'predicted_demand': 'city_predicted_demand'}, inplace=True)
        
        # Store-level demand (needed for stock-out detection)
        store_demand = self.forecast.groupby(['store_id', 'sku_id', 'power_cluster'])['predicted_demand'].sum().reset_index()
        store_demand.rename(columns={'predicted_demand': 'store_predicted_demand'}, inplace=True)
        
        print("✓ Forecast aggregation complete")
        return sku_power_demand, city_sku_demand, store_demand
    
    def generate_production_recommendations(self, sku_power_demand):
        """Generate production plan with safety buffer"""
        print("Generating production recommendations...")
        
        # Apply 15% safety buffer
        sku_power_demand['recommended_production_qty'] = (
            sku_power_demand['total_predicted_demand'] * 1.15
        ).round().astype(int)
        
        # Create production plan
        self.production_plan = sku_power_demand[['sku_id', 'power_cluster', 'recommended_production_qty']].copy()
        
        print(f"✓ Production plan generated: {len(self.production_plan)} recommendations")
        return self.production_plan
    
    def allocate_inventory(self, city_sku_demand, sku_power_demand):
        """Allocate production across cities proportional to forecast demand"""
        print("Allocating inventory to cities...")
        
        # Merge to get total demand per SKU+power cluster
        allocation_data = city_sku_demand.merge(
            sku_power_demand[['sku_id', 'power_cluster', 'total_predicted_demand']],
            on=['sku_id', 'power_cluster'],
            how='left'
        )
        
        # Calculate allocation proportion
        allocation_data['allocation_proportion'] = (
            allocation_data['city_predicted_demand'] / allocation_data['total_predicted_demand']
        )
        
        # Merge with production plan to get total production
        allocation_data = allocation_data.merge(
            self.production_plan,
            on=['sku_id', 'power_cluster'],
            how='left'
        )
        
        # Calculate allocated units
        allocation_data['allocated_units'] = (
            allocation_data['allocation_proportion'] * allocation_data['recommended_production_qty']
        ).round().astype(int)
        
        # Create allocation plan
        self.allocation_plan = allocation_data[[
            'city', 'sku_id', 'power_cluster', 'allocated_units'
        ]].copy()
        
        print(f"✓ Inventory allocation complete: {len(self.allocation_plan)} city allocations")
        return self.allocation_plan
    
    def detect_stockout_risks(self, store_demand):
        """Detect stock-out risks by comparing demand vs current inventory"""
        print("Detecting stock-out risks...")
        
        # Merge store demand with current inventory
        risk_data = store_demand.merge(
            self.inventory[['store_id', 'sku_id', 'stock_level']],
            on=['store_id', 'sku_id'],
            how='left'
        )
        
        # Handle missing inventory (assume 0)
        risk_data['stock_level'] = risk_data['stock_level'].fillna(0)
        
        # Calculate shortage
        risk_data['shortage_units'] = (
            risk_data['store_predicted_demand'] - risk_data['stock_level']
        ).clip(lower=0).round(2)  # Only positive shortages
        
        # Calculate risk probability (shortage / demand), clamped to 1.0
        # Avoid division by zero
        risk_data['risk_probability'] = (
            risk_data['shortage_units'] / (risk_data['store_predicted_demand'] + 0.001)
        ).clip(upper=1.0).round(2)
        
        # Add power cluster information
        risk_data = risk_data.merge(
            self.stores[['store_id', 'city']],
            on='store_id',
            how='left'
        )
        
        # Create stock risk dataframe
        self.stock_risk = risk_data[[
            'store_id', 'city', 'sku_id', 'power_cluster',
            'store_predicted_demand', 'stock_level', 'shortage_units', 'risk_probability'
        ]].copy()
        
        # Filter to only include actual risks (shortage > 0)
        self.stock_risk = self.stock_risk[self.stock_risk['shortage_units'] > 0].reset_index(drop=True)
        
        print(f"✓ Stock-out risk detection complete: {len(self.stock_risk)} risk cases identified")
        return self.stock_risk
    
    def calculate_revenue_opportunity(self):
        """Calculate revenue opportunity from stock-outs"""
        print("Calculating revenue opportunity...")
        
        # Get price information for each SKU
        stock_risk_with_price = self.stock_risk.merge(
            self.products[['sku_id', 'base_cost']],
            on='sku_id',
            how='left'
        )
        
        # Estimate selling price (add 50% markup to base cost)
        stock_risk_with_price['estimated_price'] = stock_risk_with_price['base_cost'] * 1.5
        
        # Calculate revenue opportunity
        stock_risk_with_price['revenue_opportunity'] = (
            stock_risk_with_price['shortage_units'] * stock_risk_with_price['estimated_price']
        )
        
        # Store revenue opportunity
        self.revenue_opportunity = stock_risk_with_price[['store_id', 'city', 'sku_id', 'power_cluster', 
                                                          'shortage_units', 'estimated_price', 'revenue_opportunity']].copy()
        
        print(f"✓ Revenue opportunity calculation complete: {len(self.revenue_opportunity)} opportunities")
        return self.revenue_opportunity
    
    def save_recommendations(self):
        """Save all recommendation outputs to CSV files"""
        print("Saving recommendations...")
        
        # Create output file paths
        production_file = os.path.join(self.data_dir, 'production_plan.csv')
        allocation_file = os.path.join(self.data_dir, 'allocation_plan.csv')
        risk_file = os.path.join(self.data_dir, 'stock_risk.csv')
        
        # Save dataframes
        self.production_plan.to_csv(production_file, index=False)
        self.allocation_plan.to_csv(allocation_file, index=False)
        self.stock_risk.to_csv(risk_file, index=False)
        
        print(f"✓ Production plan saved to: {production_file}")
        print(f"✓ Allocation plan saved to: {allocation_file}")
        print(f"✓ Stock risk saved to: {risk_file}")
    
    def generate_summary_report(self):
        """Generate business summary report"""
        print("\n" + "=" * 60)
        print("MANUFACTURING & INVENTORY RECOMMENDATION SUMMARY")
        print("=" * 60)
        
        # Total production
        total_production = self.production_plan['recommended_production_qty'].sum()
        print(f"Total recommended production: {total_production:,} units")
        
        # Total shortage risk
        total_shortage = self.stock_risk['shortage_units'].sum()
        print(f"Total shortage risk: {total_shortage:,.2f} units")
        
        # Revenue at risk
        total_revenue_risk = self.revenue_opportunity['revenue_opportunity'].sum()
        print(f"Revenue at risk: ₹{total_revenue_risk:,.2f}")
        
        # Key insights
        print("\nKey Business Insights:")
        print(f"• {len(self.production_plan)} unique SKU-power combinations to produce")
        print(f"• {len(self.allocation_plan)} city-level inventory allocations")
        print(f"• {len(self.stock_risk)} store-level stock-out risks identified")
        print(f"• {len(self.revenue_opportunity)} revenue opportunities")
        
        # Top production recommendations
        print("\nTop 5 Production Recommendations:")
        top_production = self.production_plan.nlargest(5, 'recommended_production_qty')
        for _, row in top_production.iterrows():
            print(f"  {row['sku_id']} ({row['power_cluster']}): {row['recommended_production_qty']:,} units")
        
        # High-risk stores
        if len(self.stock_risk) > 0:
            print("\nTop 5 High-Risk Stores:")
            top_risk = self.stock_risk.nlargest(5, 'shortage_units')
            for _, row in top_risk.iterrows():
                print(f"  {row['store_id']} ({row['city']}): {row['shortage_units']:.1f} units shortage")
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION ENGINE COMPLETE")
        print("=" * 60)
    
    def run_recommendation_pipeline(self):
        """Run complete recommendation pipeline"""
        print("=" * 60)
        print("MANUFACTURING RECOMMENDATION ENGINE")
        print("=" * 60)
        
        # Load data
        self.load_data()
        
        # Aggregate forecast
        sku_power_demand, city_sku_demand, store_demand = self.aggregate_forecast()
        
        # Generate production recommendations
        self.generate_production_recommendations(sku_power_demand)
        
        # Allocate inventory
        self.allocate_inventory(city_sku_demand, sku_power_demand)
        
        # Detect stock-out risks
        self.detect_stockout_risks(store_demand)
        
        # Calculate revenue opportunity
        self.calculate_revenue_opportunity()
        
        # Save recommendations
        self.save_recommendations()
        
        # Generate summary report
        self.generate_summary_report()
        
        return {
            'production_plan': self.production_plan,
            'allocation_plan': self.allocation_plan,
            'stock_risk': self.stock_risk,
            'revenue_opportunity': self.revenue_opportunity
        }

def main():
    """Main function to run recommendation engine"""
    engine = ManufacturingRecommendationEngine()
    results = engine.run_recommendation_pipeline()
    return results

if __name__ == "__main__":
    main()