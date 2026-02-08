"""
Professional Data Cleaning and Preprocessing Module
Handles missing values, outliers, duplicates, and data validation
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List
import logging
from datetime import datetime
from utils.geo_data import get_coordinates

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Professional-grade data cleaning and preprocessing"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.cleaning_log = []
        self.original_shape = None
        self.cleaned_shape = None
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load CSV data with error handling"""
        try:
            # Use UTF-8 encoding to avoid Windows charmap codec errors
            df = pd.read_csv(filepath, encoding='utf-8', encoding_errors='replace')
            self.original_shape = df.shape
            self._log_step(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert column names to snake_case"""
        original_cols = df.columns.tolist()
        df.columns = (df.columns
                      .str.strip()
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace(r'[^\w\s]', '', regex=True))
        
        self._log_step(f"Normalized {len(original_cols)} column names to snake_case")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Intelligent missing value handling based on data distribution"""
        missing_before = df.isnull().sum().sum()
        
        # Drop columns with >95% missing values
        threshold = 0.95
        null_pct = df.isnull().sum() / len(df)
        cols_to_drop = null_pct[null_pct > threshold].index.tolist()
        
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            self._log_step(f"Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing: {cols_to_drop}")
        
        # For numeric columns, impute with median (robust to outliers)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                null_count = df[col].isnull().sum()
                df[col].fillna(median_val, inplace=True)
                self._log_step(f"Imputed {null_count} missing values in '{col}' with median: {median_val:.2f}")
        
        # For categorical columns, use mode or 'Unknown'
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].isnull().any():
                null_count = df[col].isnull().sum()
                if df[col].mode().empty:
                    df[col].fillna('Unknown', inplace=True)
                else:
                    mode_val = df[col].mode()[0]
                    df[col].fillna(mode_val, inplace=True)
                self._log_step(f"Imputed {null_count} missing values in '{col}' with mode/Unknown")
        
        missing_after = df.isnull().sum().sum()
        self._log_step(f"Missing values: {missing_before} → {missing_after}")
        
        return df
    
    def detect_and_handle_outliers(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """Detect outliers using IQR and Z-score methods"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outlier_summary = {}
        
        for col in columns:
            if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                # IQR method
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                iqr_multiplier = self.config.get('iqr_multiplier', 1.5)
                
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR
                
                iqr_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                
                # Z-score method
                z_threshold = self.config.get('z_score_threshold', 3)
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                z_outliers = (z_scores > z_threshold).sum()
                
                outlier_summary[col] = {
                    'iqr_outliers': iqr_outliers,
                    'z_score_outliers': z_outliers,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
                
                # Flag outliers (don't remove, keep for transparency)
                df[f'{col}_outlier_flag'] = (
                    (df[col] < lower_bound) | 
                    (df[col] > upper_bound)
                ).astype(int)
        
        total_outliers = sum([v['iqr_outliers'] for v in outlier_summary.values()])
        self._log_step(f"Detected {total_outliers} outliers across {len(outlier_summary)} columns (flagged, not removed)")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        duplicates_before = df.duplicated(subset=subset).sum()
        df = df.drop_duplicates(subset=subset, keep='first')
        duplicates_removed = duplicates_before - df.duplicated(subset=subset).sum()
        
        if duplicates_removed > 0:
            self._log_step(f"Removed {duplicates_removed} duplicate rows")
        else:
            self._log_step("No duplicates found")
        
        return df
    
    def parse_datetime(self, df: pd.DataFrame, date_column: str = 'start_date') -> pd.DataFrame:
        """Parse and standardize datetime columns"""
        if date_column in df.columns:
            try:
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                
                # Extract temporal features
                df['year'] = df[date_column].dt.year
                df['month'] = df[date_column].dt.month
                df['quarter'] = df[date_column].dt.quarter
                df['day_of_week'] = df[date_column].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
                
                self._log_step(f"Parsed '{date_column}' and extracted temporal features")
            except Exception as e:
                logger.warning(f"Could not parse {date_column}: {e}")
        
        return df
    
    def validate_pollutant_values(self, df: pd.DataFrame, value_column: str = 'data_value') -> pd.DataFrame:
        """Validate pollutant values for impossible data"""
        if value_column in df.columns:
            # Check for negative values
            negative_count = (df[value_column] < 0).sum()
            if negative_count > 0:
                df = df[df[value_column] >= 0]
                self._log_step(f"Removed {negative_count} rows with negative {value_column}")
            
            # Check for extreme outliers (>1000 for most pollutants is unrealistic)
            extreme_threshold = 1000
            extreme_count = (df[value_column] > extreme_threshold).sum()
            if extreme_count > 0:
                self._log_step(f"Found {extreme_count} extreme values (>{extreme_threshold}) - flagged for review")
        
        return df
    
    def enrich_with_coordinates(self, df: pd.DataFrame, geo_col: str = 'geo_place_name') -> pd.DataFrame:
        """Enrich dataframe with latitude and longitude based on place name"""
        if geo_col in df.columns:
            # Apply get_coordinates function
            # Note: get_coordinates returns a dict {'lat': ..., 'lon': ...}
            coords = df[geo_col].apply(get_coordinates)
            
            # Extract lat/lon into new columns
            df['latitude'] = coords.apply(lambda x: x['lat'])
            df['longitude'] = coords.apply(lambda x: x['lon'])
            
            self._log_step(f"Enriched data with coordinates using '{geo_col}'")
        else:
            logger.warning(f"Could not find '{geo_col}' for coordinate enrichment")
        
        return df

    def clean_pipeline(self, filepath: str) -> Tuple[pd.DataFrame, List[str]]:
        """Complete cleaning pipeline"""
        logger.info("Starting data cleaning pipeline...")
        
        # Load data
        df = self.load_data(filepath)
        
        # Step 1: Normalize columns
        df = self.normalize_column_names(df)
        
        # Step 2: Parse datetime
        df = self.parse_datetime(df)
        
        # Step 3: Remove duplicates
        df = self.remove_duplicates(df)
        
        # Step 4: Handle missing values
        df = self.handle_missing_values(df)
        
        # Step 5: Validate pollutant values
        df = self.validate_pollutant_values(df)
        
        # Step 6: Detect outliers (flag, don't remove)
        numeric_cols = ['data_value']
        df = self.detect_and_handle_outliers(df, columns=numeric_cols)
        
        # Step 7: Enrich with coordinates
        df = self.enrich_with_coordinates(df)
        
        self.cleaned_shape = df.shape
        self._log_step(f"Final cleaned data: {df.shape[0]} rows, {df.shape[1]} columns")
        
        logger.info("Data cleaning pipeline completed")
        return df, self.cleaning_log
    
    def _log_step(self, message: str):
        """Log cleaning step with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Remove special characters that cause Windows encoding issues
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        log_entry = f"[{timestamp}] {safe_message}"
        self.cleaning_log.append(log_entry)
        logger.info(safe_message)
    
    def get_cleaning_report(self) -> Dict:
        """Generate comprehensive cleaning report"""
        return {
            'original_shape': self.original_shape,
            'cleaned_shape': self.cleaned_shape,
            'rows_removed': self.original_shape[0] - self.cleaned_shape[0] if self.original_shape else 0,
            'columns_added': self.cleaned_shape[1] - self.original_shape[1] if self.original_shape else 0,
            'cleaning_steps': len(self.cleaning_log),
            'log': self.cleaning_log
        }


# Convenience function for quick cleaning
def clean_air_quality_data(filepath: str, config: Dict = None) -> Tuple[pd.DataFrame, Dict]:
    """Quick clean air quality data and return report"""
    processor = DataProcessor(config)
    df, log = processor.clean_pipeline(filepath)
    report = processor.get_cleaning_report()
    return df, report


if __name__ == "__main__":
    # Test the module
    from config import OUTLIER_CONFIG
    
    df, report = clean_air_quality_data(
        'Air_Quality.csv',
        config=OUTLIER_CONFIG
    )
    
    print("\n=== Cleaning Report ===")
    print(f"Original shape: {report['original_shape']}")
    print(f"Cleaned shape: {report['cleaned_shape']}")
    print(f"Rows removed: {report['rows_removed']}")
    print(f"Columns added: {report['columns_added']}")
    print(f"\nCleaning steps: {report['cleaning_steps']}")
    for step in report['log'][-5:]:  # Show last 5 steps
        print(step)
