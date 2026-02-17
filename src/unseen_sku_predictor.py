"""
Unseen SKU Demand Predictor
===========================
Predicts demand for new SKUs with no historical sales data
by finding similar existing products and averaging their forecasts.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import NearestNeighbors


# Price-band adjustment multipliers (relative to mid baseline)
PRICE_BAND_MULTIPLIERS = {
    'low': 0.90,
    'mid': 1.00,
    'high': 1.05,
    'premium': 1.15,
}

# Ordered price bands for numeric encoding used in adjustment
PRICE_BAND_ORDER = {'low': 0, 'mid': 1, 'high': 2, 'premium': 3}

# Feature columns used for similarity matching
FEATURE_COLS = ['frame_type', 'lens_type', 'price_band']


class UnseenSKUPredictor:
    """Predicts demand for unseen / newly-launched SKUs."""

    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.products: pd.DataFrame | None = None
        self.forecast: pd.DataFrame | None = None
        self.encoder: OneHotEncoder | None = None
        self.nn_model: NearestNeighbors | None = None
        self.encoded_features: np.ndarray | None = None
        self._is_fitted = False

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_data(self) -> None:
        """Load products and forecast CSVs."""
        self.products = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
        self.forecast = pd.read_csv(os.path.join(self.data_dir, 'forecast_next_week.csv'))

    # ------------------------------------------------------------------
    # Feature encoding & neighbour fitting
    # ------------------------------------------------------------------
    def fit(self) -> None:
        """Encode product features and fit NearestNeighbors."""
        if self.products is None:
            self.load_data()

        feature_df = self.products[FEATURE_COLS].copy()

        # One-hot encode categorical features
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.encoded_features = self.encoder.fit_transform(feature_df)

        # Fit nearest-neighbour model (cosine similarity)
        k = min(5, len(self.products))
        self.nn_model = NearestNeighbors(n_neighbors=k, metric='cosine')
        self.nn_model.fit(self.encoded_features)
        self._is_fitted = True

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict_new_sku_demand(self, new_sku_dict: dict) -> pd.DataFrame:
        """
        Predict demand for a new SKU described by *new_sku_dict*.

        Parameters
        ----------
        new_sku_dict : dict
            Must contain keys: frame_type, lens_type, price_band.
            Optional: color (currently unused for similarity).

        Returns
        -------
        pd.DataFrame
            Columns: city, power_cluster, predicted_demand
        """
        if not self._is_fitted:
            self.load_data()
            self.fit()

        # --- Step 0: encode the new SKU ---
        new_df = pd.DataFrame([{col: new_sku_dict.get(col, '') for col in FEATURE_COLS}])
        new_encoded = self.encoder.transform(new_df)

        # --- Step 1: find similar SKUs ---
        distances, indices = self.nn_model.kneighbors(new_encoded)
        similar_skus = self.products.iloc[indices[0]]['sku_id'].tolist()

        # --- Step 2: average their predicted demand ---
        similar_forecast = self.forecast[self.forecast['sku_id'].isin(similar_skus)]

        if similar_forecast.empty:
            # Fallback: return global average by city × power_cluster
            demand_df = (
                self.forecast
                .groupby(['city', 'power_cluster'])['predicted_demand']
                .mean()
                .reset_index()
            )
        else:
            demand_df = (
                similar_forecast
                .groupby(['city', 'power_cluster'])['predicted_demand']
                .mean()
                .reset_index()
            )

        # --- Step 3: price-band adjustment ---
        # Compute average price band of the neighbours
        neighbor_bands = self.products.iloc[indices[0]]['price_band']
        avg_neighbor_band_val = neighbor_bands.map(PRICE_BAND_ORDER).mean()

        new_band_val = PRICE_BAND_ORDER.get(new_sku_dict.get('price_band', 'mid'), 1)
        band_diff = new_band_val - avg_neighbor_band_val

        # Map the difference to a multiplier (each step ≈ 5 %)
        adjustment = 1.0 + band_diff * 0.05
        demand_df['predicted_demand'] = (demand_df['predicted_demand'] * adjustment).round(2)

        return demand_df

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get_similar_skus(self, new_sku_dict: dict, n: int = 5) -> pd.DataFrame:
        """Return the top-n most similar existing SKUs (with distances)."""
        if not self._is_fitted:
            self.load_data()
            self.fit()

        new_df = pd.DataFrame([{col: new_sku_dict.get(col, '') for col in FEATURE_COLS}])
        new_encoded = self.encoder.transform(new_df)
        distances, indices = self.nn_model.kneighbors(new_encoded, n_neighbors=n)

        result = self.products.iloc[indices[0]].copy()
        result['similarity_distance'] = distances[0]
        return result.reset_index(drop=True)

    @staticmethod
    def get_option_values() -> dict:
        """Return the valid option values for UI dropdowns."""
        return {
            'frame_type': ['full-rim', 'half-rim', 'rimless'],
            'lens_type': ['single vision', 'blue cut', 'progressive'],
            'price_band': ['low', 'mid', 'high', 'premium'],
        }


# ======================================================================
# CLI entry-point
# ======================================================================
def main():
    """Run a sample prediction and save to CSV."""
    predictor = UnseenSKUPredictor()
    predictor.load_data()
    predictor.fit()

    sample_sku = {
        'frame_type': 'full-rim',
        'lens_type': 'progressive',
        'price_band': 'premium',
        'color': 'black',
    }

    print("="*60)
    print("  Unseen SKU Demand Predictor")
    print("="*60)
    print(f"\nNew SKU: {sample_sku}\n")

    # Show similar SKUs
    similar = predictor.get_similar_skus(sample_sku)
    print("Top-5 Similar Existing SKUs:")
    print(similar[['sku_id', 'frame_type', 'lens_type', 'price_band', 'base_cost', 'similarity_distance']].to_string(index=False))

    # Predict demand
    demand = predictor.predict_new_sku_demand(sample_sku)
    print(f"\nPredicted demand across {demand['city'].nunique()} cities, {demand['power_cluster'].nunique()} power clusters:")
    print(f"  Total estimated demand: {demand['predicted_demand'].sum():,.1f} units")

    # Save
    out_path = os.path.join('data', 'new_sku_forecast.csv')
    demand.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
