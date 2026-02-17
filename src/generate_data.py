import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

class LensDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.fake.seed_instance(42)  # For reproducible results
        np.random.seed(42)
        random.seed(42)
        
        # Configuration
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2023, 6, 30)
        self.n_cities = 10
        self.n_stores = 50
        self.n_skus = 200
        self.n_days = (self.end_date - self.start_date).days + 1
        
        # Product configurations
        self.frame_types = ['full-rim', 'half-rim', 'rimless']
        self.lens_types = ['single vision', 'progressive', 'blue cut']
        self.power_clusters = ['low', 'medium', 'high', 'very_high']
        self.price_bands = ['low', 'mid', 'high', 'premium']
        self.city_tiers = ['tier1', 'tier2', 'tier3']
        
    def generate_cities(self):
        """Generate list of cities with realistic Indian city names"""
        cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 
            'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
        ]
        return cities[:self.n_cities]
    
    def generate_stores(self):
        """Generate store data with city assignments and tiers"""
        cities = self.generate_cities()
        stores = []
        
        # Distribute stores across cities (weighted towards larger cities)
        city_store_counts = [8, 7, 6, 5, 4, 4, 3, 3, 5, 5]  # Total = 50
        
        store_id = 1
        for i, city in enumerate(cities):
            tier = random.choices(self.city_tiers, weights=[0.3, 0.4, 0.3])[0]
            avg_footfall = {
                'tier1': random.randint(300, 800),
                'tier2': random.randint(150, 400),
                'tier3': random.randint(80, 200)
            }[tier]
            
            for _ in range(city_store_counts[i]):
                stores.append({
                    'store_id': f'STORE_{store_id:03d}',
                    'city': city,
                    'tier': tier,
                    'avg_footfall': avg_footfall
                })
                store_id += 1
                
        return pd.DataFrame(stores)
    
    def generate_products(self):
        """Generate product catalog with SKUs"""
        products = []
        
        # Create product combinations
        for sku_id in range(1, self.n_skus + 1):
            frame_type = random.choices(self.frame_types, weights=[0.45, 0.35, 0.20])[0]
            lens_type = random.choices(self.lens_types, weights=[0.60, 0.25, 0.15])[0]
            color = self.fake.color_name()
            
            # Price band assignment with realistic distribution
            # Mid-price products are most common
            price_band = random.choices(self.price_bands, weights=[0.2, 0.5, 0.25, 0.05])[0]
            
            # Base cost based on price band
            base_cost = {
                'low': random.uniform(800, 1500),
                'mid': random.uniform(1500, 3000),
                'high': random.uniform(3000, 5000),
                'premium': random.uniform(5000, 8000)
            }[price_band]
            
            products.append({
                'sku_id': f'SKU_{sku_id:03d}',
                'frame_type': frame_type,
                'color': color,
                'lens_type': lens_type,
                'price_band': price_band,
                'base_cost': round(base_cost, 2)
            })
            
        return pd.DataFrame(products)
    
    def generate_inventory(self, stores_df, products_df):
        """Generate initial inventory levels for each store-SKU combination"""
        inventory = []
        
        for _, store in stores_df.iterrows():
            for _, product in products_df.iterrows():
                # Stock level based on store tier and product price
                base_stock = {
                    'tier1': random.randint(15, 30),
                    'tier2': random.randint(10, 20),
                    'tier3': random.randint(5, 15)
                }[store['tier']]
                
                # Adjust for price band (premium items have less stock)
                stock_multiplier = {
                    'low': 1.2,
                    'mid': 1.0,
                    'high': 0.8,
                    'premium': 0.5
                }[product['price_band']]
                
                stock_level = max(0, int(base_stock * stock_multiplier + random.randint(-5, 10)))
                lead_time = random.randint(2, 10)  # Days
                
                inventory.append({
                    'store_id': store['store_id'],
                    'sku_id': product['sku_id'],
                    'stock_level': stock_level,
                    'lead_time_days': lead_time
                })
                
        return pd.DataFrame(inventory)
    
    def generate_daily_orders(self, date, stores_df, products_df):
        """Generate orders for a specific date"""
        orders = []
        order_id_counter = 1
        
        # Daily base demand (affected by day of week)
        day_of_week = date.weekday()
        # Weekend effect (higher demand)
        weekend_multiplier = 1.3 if day_of_week >= 5 else 1.0
        
        # Monthly trend (gradual growth)
        days_since_start = (date - self.start_date).days
        trend_factor = 1 + (days_since_start * 0.002)  # 0.2% daily growth
        
        for _, store in stores_df.iterrows():
            # Store-level base demand based on tier and footfall
            base_demand = store['avg_footfall'] * 0.05  # 5% conversion rate
            
            for _, product in products_df.iterrows():
                # Product demand factors
                price_factor = {
                    'low': 1.2,
                    'mid': 1.5,
                    'high': 0.8,
                    'premium': 0.4
                }[product['price_band']]
                
                lens_factor = {
                    'single vision': 1.0,
                    'progressive': 0.3,  # Less frequent but higher value
                    'blue cut': 0.7
                }[product['lens_type']]
                
                # City demand variation
                city_factor = {
                    'Mumbai': 1.2,
                    'Delhi': 1.1,
                    'Bangalore': 1.15,
                    'Hyderabad': 1.0,
                    'Chennai': 1.0,
                    'Kolkata': 0.9,
                    'Pune': 1.05,
                    'Ahmedabad': 0.95,
                    'Jaipur': 0.85,
                    'Lucknow': 0.8
                }.get(store['city'], 1.0)
                
                # Calculate expected demand
                expected_demand = (base_demand * price_factor * lens_factor * 
                                 city_factor * weekend_multiplier * trend_factor)
                
                # Add randomness
                if expected_demand > 0:
                    # Poisson-like distribution for count data
                    actual_demand = np.random.poisson(expected_demand * 0.3)
                    
                    if actual_demand > 0:
                        # Power cluster assignment
                        power_cluster = random.choices(
                            self.power_clusters, 
                            weights=[0.4, 0.35, 0.2, 0.05]
                        )[0]
                        
                        # Price calculation
                        price = product['base_cost'] * random.uniform(1.2, 1.8)
                        
                        orders.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'order_id': f'ORDER_{date.strftime("%Y%m%d")}_{order_id_counter:04d}',
                            'store_id': store['store_id'],
                            'city': store['city'],
                            'sku_id': product['sku_id'],
                            'frame_type': product['frame_type'],
                            'lens_type': product['lens_type'],
                            'power_cluster': power_cluster,
                            'qty': actual_demand,
                            'price': round(price, 2)
                        })
                        order_id_counter += 1
                        
        return orders
    
    def generate_orders(self, stores_df, products_df):
        """Generate complete orders dataset for the time period"""
        all_orders = []
        
        current_date = self.start_date
        while current_date <= self.end_date:
            daily_orders = self.generate_daily_orders(current_date, stores_df, products_df)
            all_orders.extend(daily_orders)
            current_date += timedelta(days=1)
            
        return pd.DataFrame(all_orders)
    
    def generate_all_datasets(self):
        """Generate all required datasets"""
        print("Generating stores data...")
        stores_df = self.generate_stores()
        
        print("Generating products data...")
        products_df = self.generate_products()
        
        print("Generating inventory data...")
        inventory_df = self.generate_inventory(stores_df, products_df)
        
        print("Generating orders data (this may take a moment)...")
        orders_df = self.generate_orders(stores_df, products_df)
        
        return orders_df, products_df, stores_df, inventory_df
    
    def save_datasets(self, orders_df, products_df, stores_df, inventory_df):
        """Save all datasets to CSV files"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_paths = {
            'orders': os.path.join(data_dir, 'orders.csv'),
            'products': os.path.join(data_dir, 'products.csv'),
            'stores': os.path.join(data_dir, 'stores.csv'),
            'inventory': os.path.join(data_dir, 'inventory.csv')
        }
        
        orders_df.to_csv(file_paths['orders'], index=False)
        products_df.to_csv(file_paths['products'], index=False)
        stores_df.to_csv(file_paths['stores'], index=False)
        inventory_df.to_csv(file_paths['inventory'], index=False)
        
        print(f"Datasets saved to {os.path.abspath(data_dir)}")
        return file_paths

def main():
    """Main function to generate all datasets"""
    print("Starting data generation for Lens Manufacturing Demo...")
    print("=" * 50)
    
    generator = LensDataGenerator()
    orders_df, products_df, stores_df, inventory_df = generator.generate_all_datasets()
    
    file_paths = generator.save_datasets(orders_df, products_df, stores_df, inventory_df)
    
    print("\nDataset Generation Complete!")
    print("=" * 50)
    print("Dataset Shapes:")
    print(f"Orders: {orders_df.shape}")
    print(f"Products: {products_df.shape}")
    print(f"Stores: {stores_df.shape}")
    print(f"Inventory: {inventory_df.shape}")
    
    print("\nSample of Orders dataset:")
    print(orders_df.head())
    
    print("\nSample of Products dataset:")
    print(products_df.head())
    
    return orders_df, products_df, stores_df, inventory_df

if __name__ == "__main__":
    main()