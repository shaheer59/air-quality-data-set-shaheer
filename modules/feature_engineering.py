"""
Advanced Feature Engineering Module
Creates derived features: rolling averages, AQI categories, volatility indices, aggregations
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Advanced feature engineering for air quality data"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
    def create_rolling_features(self, df: pd.DataFrame, value_col: str = 'data_value',
                                 windows: List[int] = None) -> pd.DataFrame:
        """Create rolling average features"""
        if windows is None:
            windows = self.config.get('rolling_windows', [7, 30])
        
        # Sort by date for proper rolling calculation
        if 'start_date' in df.columns:
            df = df.sort_values('start_date')
        
        for window in windows:
            df[f'rolling_avg_{window}d'] = df.groupby(['name', 'geo_place_name'])[value_col].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'rolling_std_{window}d'] = df.groupby(['name', 'geo_place_name'])[value_col].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
        
        return df
    
    def classify_aqi_category(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Classify pollutant levels into AQI categories based on EPA standards"""
        
        def get_aqi_category(value, pollutant_type):
            """Determine AQI category based on pollutant and value"""
            # Simplified AQI categorization (adjust based on specific pollutant)
            if pollutant_type == 'NO2':  # ppb
                if value <= 53:
                    return 'Good'
                elif value <= 100:
                    return 'Moderate'
                elif value <= 360:
                    return 'Unhealthy for Sensitive Groups'
                elif value <= 649:
                    return 'Unhealthy'
                elif value <= 1249:
                    return 'Very Unhealthy'
                else:
                    return 'Hazardous'
            
            elif pollutant_type == 'PM2.5':  # mcg/m3
                if value <= 12:
                    return 'Good'
                elif value <= 35.4:
                    return 'Moderate'
                elif value <= 55.4:
                    return 'Unhealthy for Sensitive Groups'
                elif value <= 150.4:
                    return 'Unhealthy'
                elif value <= 250.4:
                    return 'Very Unhealthy'
                else:
                    return 'Hazardous'
            
            elif pollutant_type == 'O3':  # ppb
                if value <= 54:
                    return 'Good'
                elif value <= 70:
                    return 'Moderate'
                elif value <= 85:
                    return 'Unhealthy for Sensitive Groups'
                elif value <= 105:
                    return 'Unhealthy'
                elif value <= 200:
                    return 'Very Unhealthy'
                else:
                    return 'Hazardous'
            
            else:
                # Generic categorization based on percentiles
                return 'Unknown'
        
        # Extract pollutant name from the 'name' column
        if 'name' in df.columns:
            df['pollutant_type'] = df['name'].apply(lambda x: 
                'NO2' if 'NO2' in str(x) or 'Nitrogen' in str(x) 
                else 'PM2.5' if 'PM' in str(x) or 'Fine particles' in str(x)
                else 'O3' if 'O3' in str(x) or 'Ozone' in str(x)
                else 'Other'
            )
            
            df['aqi_category'] = df.apply(
                lambda row: get_aqi_category(row[value_col], row['pollutant_type']),
                axis=1
            )
        
        return df
    
    def calculate_volatility_index(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Calculate pollution volatility index (coefficient of variation)"""
        
        # Group by location and pollutant, calculate CV
        df['volatility_index'] = df.groupby(['name', 'geo_place_name'])[value_col].transform(
            lambda x: (x.std() / x.mean() * 100) if x.mean() != 0 else 0
        )
        
        # Classify volatility level
        df['volatility_level'] = pd.cut(
            df['volatility_index'],
            bins=[-np.inf, 10, 25, 50, np.inf],
            labels=['Low', 'Moderate', 'High', 'Very High']
        )
        
        return df
    
    def create_temporal_aggregations(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Create temporal aggregations"""
        
        if 'start_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['start_date']):
            # Daily aggregation
            df['daily_avg'] = df.groupby(['geo_place_name', 'name', df['start_date'].dt.date])[value_col].transform('mean')
            
            # Weekly aggregation
            df['week'] = df['start_date'].dt.isocalendar().week
            df['weekly_avg'] = df.groupby(['geo_place_name', 'name', 'year', 'week'])[value_col].transform('mean')
            
            # Monthly aggregation
            df['monthly_avg'] = df.groupby(['geo_place_name', 'name', 'year', 'month'])[value_col].transform('mean')
            
            # Quarterly aggregation
            df['quarterly_avg'] = df.groupby(['geo_place_name', 'name', 'year', 'quarter'])[value_col].transform('mean')
        
        return df
    
    def calculate_change_rates(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Calculate rate of change and year-over-year changes"""
        
        # Sort by location, pollutant, and date
        if 'start_date' in df.columns:
            df = df.sort_values(['geo_place_name', 'name', 'start_date'])
            
            # Calculate percentage change
            df['pct_change'] = df.groupby(['geo_place_name', 'name'])[value_col].pct_change() * 100
            
            # Calculate absolute change
            df['abs_change'] = df.groupby(['geo_place_name', 'name'])[value_col].diff()
            
            # Year-over-year change (if year column exists)
            if 'year' in df.columns:
                df['yoy_change'] = df.groupby(['geo_place_name', 'name', 'month'])[value_col].diff()
        
        return df
    
    def create_seasonal_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create seasonal indicator features"""
        
        if 'month' in df.columns:
            # Season classification
            def get_season(month):
                if month in [12, 1, 2]:
                    return 'Winter'
                elif month in [3, 4, 5]:
                    return 'Spring'
                elif month in [6, 7, 8]:
                    return 'Summer'
                else:
                    return 'Fall'
            
            df['season'] = df['month'].apply(get_season)
            
            # Seasonal average
            df['seasonal_avg'] = df.groupby(['geo_place_name', 'name', 'season'])['data_value'].transform('mean')
        
        # Extract from time_period if available
        if 'time_period' in df.columns:
            df['is_summer'] = df['time_period'].str.contains('Summer', case=False, na=False).astype(int)
            df['is_winter'] = df['time_period'].str.contains('Winter', case=False, na=False).astype(int)
            df['is_annual'] = df['time_period'].str.contains('Annual', case=False, na=False).astype(int)
        
        return df
    
    def create_pollution_velocity(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Calculate pollution change velocity (first and second derivatives)"""
        
        if 'start_date' in df.columns:
            df = df.sort_values(['geo_place_name', 'name', 'start_date'])
            
            # First derivative (velocity)
            df['pollution_velocity'] = df.groupby(['geo_place_name', 'name'])[value_col].diff()
            
            # Second derivative (acceleration)
            df['pollution_acceleration'] = df.groupby(['geo_place_name', 'name'])['pollution_velocity'].diff()
            
            # Classify trend direction
            df['trend_direction'] = df['pollution_velocity'].apply(
                lambda x: 'Improving' if x < -0.5 else 'Worsening' if x > 0.5 else 'Stable'
            )
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering steps"""
        
        print("Starting feature engineering...")
        
        # 1. Rolling features
        df = self.create_rolling_features(df)
        print("[OK] Created rolling average features")
        
        # 2. AQI categorization
        df = self.classify_aqi_category(df)
        print("[OK] Classified AQI categories")
        
        # 3. Volatility index
        df = self.calculate_volatility_index(df)
        print("[OK] Calculated volatility indices")
        
        # 4. Temporal aggregations
        df = self.create_temporal_aggregations(df)
        print("[OK] Created temporal aggregations")
        
        # 5. Change rates
        df = self.calculate_change_rates(df)
        print("[OK] Calculated change rates")
        
        # 6. Seasonal indicators
        df = self.create_seasonal_indicators(df)
        print("[OK] Created seasonal indicators")
        
        # 7. Pollution velocity
        df = self.create_pollution_velocity(df)
        print("[OK] Calculated pollution velocity")
        
        print(f"Feature engineering complete! Added {df.shape[1] - 12} new features")
        
        return df


# Convenience function
def engineer_features(df: pd.DataFrame, config: Dict = None) -> pd.DataFrame:
    """Quick feature engineering"""
    engineer = FeatureEngineer(config)
    return engineer.engineer_all_features(df)


if __name__ == "__main__":
    # Test the module
    from data_processor import clean_air_quality_data
    from config import FEATURE_CONFIG
    
    # Clean data first
    df, _ = clean_air_quality_data('Air_Quality.csv')
    
    # Engineer features
    df_engineered = engineer_features(df, FEATURE_CONFIG)
    
    print("\n=== Engineered Features ===")
    print(f"Original columns: 12")
    print(f"Total columns after engineering: {df_engineered.shape[1]}")
    print(f"\nNew feature columns:")
    new_cols = [col for col in df_engineered.columns if col not in 
                ['unique_id', 'indicator_id', 'name', 'measure', 'measure_info',
                 'geo_type_name', 'geo_join_id', 'geo_place_name', 'time_period',
                 'start_date', 'data_value', 'message']]
    for col in new_cols[:10]:  # Show first 10
        print(f"  - {col}")
