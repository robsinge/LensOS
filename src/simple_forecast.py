import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import joblib
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

class SimpleDemandForecaster:
    def __init__(self):
        self.model = None
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        self.orders = None
        self.products = None
        self.stores = None
        
    def load_data(self):
        """Load all required datasets"""
        print("Loading datasets...")
        self.orders = pd.read_csv(os.path.join(self.data_dir, 'orders.csv'))
        self.products = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
        self.stores = pd.read_csv(os.path.join(self.data_dir, 'stores.csv'))
        print("✓ Data loaded successfully")
        
    def aggregate_demand(self):
        """Aggregate demand by date, store, city, sku, and power cluster"""
        print("Aggregating demand data...")
        
        # Convert date to datetime
        self.orders['date'] = pd.to_datetime(self.orders['date'])
        
        # Group by required dimensions and sum quantities
        demand_data = self.orders.groupby(['date', 'store_id', 'city', 'sku_id', 'power_cluster'])['qty'].sum().reset_index()
        demand_data.rename(columns={'qty': 'daily_qty'}, inplace=True)
        
        print(f"✓ Aggregated demand data shape: {demand_data.shape}")
        return demand_data
    
    def create_simple_features(self, demand_data):
        """Create simple time-based features for forecasting"""
        print("Creating simple features...")
        
        # Merge with product and store information
        df = demand_data.merge(self.products[['sku_id', 'frame_type', 'lens_type', 'price_band']], on='sku_id', how='left')
        df = df.merge(self.stores[['store_id', 'tier', 'avg_footfall']], on='store_id', how='left')
        
        # Time features
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        
        # Simple lag features (using mean of recent values)
        df['lag_7_mean'] = df.groupby(['store_id', 'sku_id', 'power_cluster'])['daily_qty'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean().shift(1)
        )
        
        # Fill missing values
        df['lag_7_mean'] = df['lag_7_mean'].fillna(df['daily_qty'].mean())
        
        print("✓ Simple feature creation complete")
        return df
    
    def prepare_train_data(self, df):
        """Prepare training and validation data"""
        print("Preparing training data...")
        
        # Remove rows with missing target values
        df = df.dropna(subset=['daily_qty'])
        
        # Use last 14 days for validation
        max_date = df['date'].max()
        val_start_date = max_date - timedelta(days=14)
        
        train_df = df[df['date'] < val_start_date].copy()
        val_df = df[df['date'] >= val_start_date].copy()
        
        # Sample data for faster training (10% of data)
        train_df = train_df.sample(frac=0.1, random_state=42)
        val_df = val_df.sample(frac=0.1, random_state=42)
        
        print(f"Training set: {len(train_df)} samples (sampled)")
        print(f"Validation set: {len(val_df)} samples (sampled)")
        
        return train_df, val_df
    
    def train_model(self, train_df, val_df):
        """Train LightGBM model with simple features"""
        print("Training LightGBM model...")
        
        # Select features
        feature_cols = ['day_of_week', 'month', 'avg_footfall', 'lag_7_mean']
        X_train = train_df[feature_cols]
        y_train = train_df['daily_qty']
        X_val = val_df[feature_cols]
        y_val = val_df['daily_qty']
        
        # Initialize and train model
        self.model = LGBMRegressor(
            n_estimators=50,  # Reduced for faster training
            learning_rate=0.1,
            max_depth=4,      # Reduced depth
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        print("✓ Model training complete")
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mae = mean_absolute_error(y_val, y_pred)
        
        print(f"Validation Metrics:")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  MAE: {mae:.2f}")
        
        return rmse, mae
    
    def simple_forecast(self, df, days_ahead=7):
        """Generate simple forecast for next 7 days"""
        print(f"Generating {days_ahead}-day forecast...")
        
        # Get the last date in the dataset
        last_date = df['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        # Get unique combinations for forecasting (sample for speed)
        unique_combinations = df[['store_id', 'city', 'sku_id', 'power_cluster']].drop_duplicates()
        unique_combinations = unique_combinations.sample(n=min(1000, len(unique_combinations)), random_state=42)
        
        forecasts = []
        
        # For each unique combination
        for _, combo in unique_combinations.iterrows():
            store_id = combo['store_id']
            city = combo['city']
            sku_id = combo['sku_id']
            power_cluster = combo['power_cluster']
            
            # Get recent data for this combination
            series_data = df[
                (df['store_id'] == store_id) & 
                (df['sku_id'] == sku_id) & 
                (df['power_cluster'] == power_cluster)
            ].copy()
            
            if len(series_data) == 0:
                continue
                
            # Get latest data point
            latest_data = series_data.iloc[-1]
            
            # Get product and store features
            product_info = self.products[self.products['sku_id'] == sku_id].iloc[0]
            store_info = self.stores[self.stores['store_id'] == store_id].iloc[0]
            
            # Generate forecast for each day
            for i, forecast_date in enumerate(forecast_dates):
                # Create feature vector
                feature_vector = pd.DataFrame([{
                    'day_of_week': forecast_date.weekday(),
                    'month': forecast_date.month,
                    'avg_footfall': store_info['avg_footfall'],
                    'lag_7_mean': latest_data['daily_qty']  # Simple approach
                }])
                
                # Make prediction
                predicted_demand = max(0, self.model.predict(feature_vector)[0])
                
                # Store forecast
                forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'store_id': store_id,
                    'city': city,
                    'sku_id': sku_id,
                    'power_cluster': power_cluster,
                    'predicted_demand': round(predicted_demand, 2)
                })
        
        forecast_df = pd.DataFrame(forecasts)
        print(f"✓ Generated {len(forecast_df)} predictions")
        return forecast_df
    
    def save_model_and_forecast(self, forecast_df, rmse, mae):
        """Save trained model and forecast results"""
        print("Saving model and forecast...")
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        
        # Save model
        model_path = os.path.join(self.model_dir, 'demand_model.pkl')
        joblib.dump(self.model, model_path)
        print(f"✓ Model saved to {model_path}")
        
        # Save forecast
        forecast_path = os.path.join(self.data_dir, 'forecast_next_week.csv')
        forecast_df.to_csv(forecast_path, index=False)
        print(f"✓ Forecast saved to {forecast_path}")
        
        return model_path, forecast_path
    
    def run_forecasting_pipeline(self):
        """Run complete forecasting pipeline"""
        print("=" * 50)
        print("SIMPLE DEMAND FORECASTING PIPELINE")
        print("=" * 50)
        
        # Load data
        self.load_data()
        
        # Aggregate demand
        demand_data = self.aggregate_demand()
        
        # Create features
        df = self.create_simple_features(demand_data)
        
        # Prepare training data
        train_df, val_df = self.prepare_train_data(df)
        
        # Train model
        rmse, mae = self.train_model(train_df, val_df)
        
        # Generate forecast
        forecast_df = self.simple_forecast(df, days_ahead=7)
        
        # Save results
        model_path, forecast_path = self.save_model_and_forecast(forecast_df, rmse, mae)
        
        print("\n" + "=" * 50)
        print("FORECAST GENERATED SUCCESSFULLY")
        print("=" * 50)
        print(f"Number of predictions: {len(forecast_df):,}")
        print(f"Model RMSE: {rmse:.2f}")
        print(f"Model MAE: {mae:.2f}")
        print(f"Forecast period: Next 7 days")
        print(f"Model saved to: {model_path}")
        print(f"Forecast saved to: {forecast_path}")
        
        # Show sample forecast
        print("\nSample Forecast (first 10 predictions):")
        print(forecast_df.head(10))
        
        return forecast_df

def main():
    """Main function to run forecasting"""
    forecaster = SimpleDemandForecaster()
    forecast_df = forecaster.run_forecasting_pipeline()
    return forecast_df

if __name__ == "__main__":
    main()