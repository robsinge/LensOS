import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import joblib
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

class DemandForecaster:
    def __init__(self):
        self.model = None
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        self.orders = None
        self.products = None
        self.stores = None
        self.residual_std_map = {}   # series_id → residual std
        self.global_residual_std = 1.0
        
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
    
    def create_features(self, demand_data):
        """Create time-based and lag features for forecasting"""
        print("Creating features...")
        
        # Merge with product and store information
        df = demand_data.merge(self.products[['sku_id', 'frame_type', 'lens_type', 'price_band']], on='sku_id', how='left')
        df = df.merge(self.stores[['store_id', 'tier', 'avg_footfall']], on='store_id', how='left')
        
        # Time features
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        
        # Create unique identifier for each time series
        df['series_id'] = df['store_id'] + '_' + df['sku_id'] + '_' + df['power_cluster']
        
        # Sort by series and date
        df = df.sort_values(['series_id', 'date']).reset_index(drop=True)
        
        # Create lag features
        print("Creating lag features...")
        lag_features = []
        
        for lag in [1, 7, 14]:
            lag_col = f'lag_{lag}'
            df[lag_col] = df.groupby('series_id')['daily_qty'].shift(lag)
            lag_features.append(lag_col)
        
        # Create rolling mean features
        print("Creating rolling features...")
        df['rolling_mean_7'] = df.groupby('series_id')['daily_qty'].shift(1).rolling(window=7, min_periods=1).mean()
        df['rolling_mean_14'] = df.groupby('series_id')['daily_qty'].shift(1).rolling(window=14, min_periods=1).mean()
        
        # Handle missing values
        feature_cols = ['day_of_week', 'week_of_year', 'month', 'avg_footfall'] + lag_features + ['rolling_mean_7', 'rolling_mean_14']
        
        # Fill missing lag values with 0 (no sales)
        for col in lag_features + ['rolling_mean_7', 'rolling_mean_14']:
            df[col] = df[col].fillna(0)
        
        print(f"✓ Feature creation complete. Total features: {len(feature_cols)}")
        return df, feature_cols
    
    def prepare_train_data(self, df, feature_cols):
        """Prepare training and validation data"""
        print("Preparing training data...")
        
        # Remove rows with missing target values
        df = df.dropna(subset=['daily_qty'])
        
        # Use last 14 days for validation
        max_date = df['date'].max()
        val_start_date = max_date - timedelta(days=14)
        
        train_df = df[df['date'] < val_start_date].copy()
        val_df = df[df['date'] >= val_start_date].copy()
        
        print(f"Training set: {len(train_df)} samples")
        print(f"Validation set: {len(val_df)} samples")
        
        return train_df, val_df
    
    def train_model(self, train_df, val_df, feature_cols):
        """Train LightGBM model"""
        print("Training LightGBM model...")
        
        X_train = train_df[feature_cols]
        y_train = train_df['daily_qty']
        X_val = val_df[feature_cols]
        y_val = val_df['daily_qty']
        
        # Simple approach - use all features as numerical for now
        X_train_copy = X_train.copy()
        X_val_copy = X_val.copy()
        
        # Initialize and train model
        self.model = LGBMRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.model.fit(
            X_train_copy, y_train,
            eval_set=[(X_val_copy, y_val)]
        )
        
        print("✓ Model training complete")
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mae = mean_absolute_error(y_val, y_pred)
        
        # --- Compute per-series residual std for confidence scoring ---
        val_df_copy = val_df.copy()
        val_df_copy['residual'] = (y_val.values - y_pred)
        series_std = val_df_copy.groupby('series_id')['residual'].std().fillna(rmse)
        self.residual_std_map = series_std.to_dict()
        self.global_residual_std = float(np.std(y_val.values - y_pred))
        print(f"  Computed residual std for {len(self.residual_std_map)} series")
        
        print(f"Validation Metrics:")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  MAE: {mae:.2f}")
        
        return rmse, mae
    
    def recursive_forecast(self, df, feature_cols, days_ahead=7):
        """Generate recursive forecast for next 7 days"""
        print(f"Generating {days_ahead}-day forecast...")
        
        # Get the last date in the dataset
        last_date = df['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        # Get unique combinations for forecasting
        unique_combinations = df[['store_id', 'city', 'sku_id', 'power_cluster']].drop_duplicates()
        
        forecasts = []
        
        # For each unique combination
        for _, combo in unique_combinations.iterrows():
            store_id = combo['store_id']
            city = combo['city']
            sku_id = combo['sku_id']
            power_cluster = combo['power_cluster']
            
            # Get the latest data for this combination
            series_data = df[
                (df['store_id'] == store_id) & 
                (df['sku_id'] == sku_id) & 
                (df['power_cluster'] == power_cluster)
            ].copy()
            
            if len(series_data) == 0:
                continue
                
            # Sort by date and get latest data
            series_data = series_data.sort_values('date').reset_index(drop=True)
            latest_row = series_data.iloc[-1].copy()
            
            # Get product and store features
            product_info = self.products[self.products['sku_id'] == sku_id].iloc[0]
            store_info = self.stores[self.stores['store_id'] == store_id].iloc[0]
            
            # Generate forecast for each day
            current_row = latest_row.copy()
            
            for i, forecast_date in enumerate(forecast_dates):
                # Update time features
                current_row['date'] = forecast_date
                current_row['day_of_week'] = forecast_date.weekday()
                current_row['week_of_year'] = forecast_date.isocalendar().week
                current_row['month'] = forecast_date.month
                
                # Update product/store features
                current_row['frame_type'] = product_info['frame_type']
                current_row['lens_type'] = product_info['lens_type']
                current_row['price_band'] = product_info['price_band']
                current_row['tier'] = store_info['tier']
                current_row['avg_footfall'] = store_info['avg_footfall']
                
                # Create feature vector
                feature_vector = pd.DataFrame([current_row[feature_cols]])
                
                # Make prediction
                predicted_demand = max(0, self.model.predict(feature_vector)[0])  # Ensure non-negative
                current_row['daily_qty'] = predicted_demand
                
                # Update lag features for next iteration
                if i == 0:  # First prediction
                    current_row['lag_1'] = latest_row['daily_qty'] if not pd.isna(latest_row['daily_qty']) else 0
                    current_row['lag_7'] = series_data.iloc[-7]['daily_qty'] if len(series_data) >= 7 else 0
                    current_row['lag_14'] = series_data.iloc[-14]['daily_qty'] if len(series_data) >= 14 else 0
                elif i >= 1:
                    current_row['lag_1'] = predicted_demand
                    current_row['lag_7'] = series_data.iloc[-6]['daily_qty'] if len(series_data) >= 6 else 0
                    current_row['lag_14'] = series_data.iloc[-13]['daily_qty'] if len(series_data) >= 13 else 0
                
                # Update rolling means (simplified)
                current_row['rolling_mean_7'] = predicted_demand  # Simplified approach
                current_row['rolling_mean_14'] = predicted_demand  # Simplified approach
                
                # --- Confidence scoring (Raw calculation) ---
                series_key = f"{store_id}_{sku_id}_{power_cluster}"
                res_std = self.residual_std_map.get(series_key, self.global_residual_std)
                
                # Expand bounds for visual uncertainty
                lower = max(0, predicted_demand - 1.96 * res_std)
                upper = predicted_demand + 1.96 * res_std
                
                # Raw uncertainty ratio (relative to demand)
                # Add small epsilon to demand to avoid division by zero
                uncertainty_ratio = (upper - lower) / (predicted_demand + 1.0)
                
                # Store forecast with raw uncertainty for now
                forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'store_id': store_id,
                    'city': city,
                    'sku_id': sku_id,
                    'power_cluster': power_cluster,
                    'predicted_demand': round(predicted_demand, 2),
                    'lower_bound': round(lower, 2),
                    'upper_bound': round(upper, 2),
                    'uncertainty_raw': uncertainty_ratio, # Temporary column
                })
                
                # Add prediction to series data for next iteration
                new_row = current_row.copy()
                new_row['date'] = forecast_date
                series_data = pd.concat([series_data, pd.DataFrame([new_row])], ignore_index=True)
        
        forecast_df = pd.DataFrame(forecasts)
        
        # --- Normalize Confidence Scores ---
        if not forecast_df.empty:
            # 1. Min-Max normalization of uncertainty
            u_min = forecast_df['uncertainty_raw'].min()
            u_max = forecast_df['uncertainty_raw'].max()
            
            if u_max > u_min:
                forecast_df['uncertainty_norm'] = (forecast_df['uncertainty_raw'] - u_min) / (u_max - u_min)
            else:
                forecast_df['uncertainty_norm'] = 0.5
            
            # 2. Map normalized uncertainty to Confidence (0.3 to 0.95)
            # Low uncertainty (0.0) -> High confidence (0.95)
            # High uncertainty (1.0) -> Low confidence (0.30)
            forecast_df['confidence_score'] = 0.95 - (forecast_df['uncertainty_norm'] * (0.95 - 0.30))
            
            # Round off
            forecast_df['confidence_score'] = forecast_df['confidence_score'].round(2)
            
            # Drop temporary columns
            forecast_df.drop(columns=['uncertainty_raw', 'uncertainty_norm'], inplace=True)
            
        print(f"✓ Generated {len(forecast_df)} predictions with normalized confidence")
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
        print("DEMAND FORECASTING PIPELINE")
        print("=" * 50)
        
        # Load data
        self.load_data()
        
        # Aggregate demand
        demand_data = self.aggregate_demand()
        
        # Create features
        df, feature_cols = self.create_features(demand_data)
        
        # Prepare training data
        train_df, val_df = self.prepare_train_data(df, feature_cols)
        
        # Train model
        rmse, mae = self.train_model(train_df, val_df, feature_cols)
        
        # Generate forecast
        forecast_df = self.recursive_forecast(df, feature_cols, days_ahead=7)
        
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
    forecaster = DemandForecaster()
    forecast_df = forecaster.run_forecasting_pipeline()
    return forecast_df

if __name__ == "__main__":
    main()