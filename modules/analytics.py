"""
Advanced Analytics and Statistical Analysis Module
Includes EDA, correlation analysis, decomposition, anomaly detection
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import skew, kurtosis
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedAnalytics:
    """Deep statistical analysis and EDA"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def comprehensive_statistics(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Calculate comprehensive statistics by pollutant and region"""
        
        stats_df = df.groupby(['name', 'geo_place_name'])[value_col].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('variance', 'var'),
            ('min', 'min'),
            ('max', 'max'),
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75)),
            ('skewness', lambda x: skew(x.dropna())),
            ('kurtosis', lambda x: kurtosis(x.dropna())),
            ('cv', lambda x: (x.std() / x.mean() * 100) if x.mean() != 0 else 0)
        ]).reset_index()
        
        return stats_df
    
    def correlation_analysis(self, df: pd.DataFrame, numeric_cols: List[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Calculate correlation matrix with significance testing"""
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove ID columns
            numeric_cols = [col for col in numeric_cols if 'id' not in col.lower() and 'flag' not in col.lower()]
        
        # Remove duplicate columns to prevent broadcasting errors in pearsonr
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Ensure numeric_cols are unique and exist
        numeric_cols = list(set([col for col in numeric_cols if col in df.columns]))
        
        # Correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # P-values for correlations
        n = len(df)
        pval_matrix = pd.DataFrame(np.zeros((len(numeric_cols), len(numeric_cols))),
                                    columns=numeric_cols, index=numeric_cols)
        
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i != j:
                    # Pairwise complete observations
                    valid_data = df[[col1, col2]].dropna()
                    if len(valid_data) > 1:
                        _, pval = stats.pearsonr(valid_data[col1], valid_data[col2])
                        pval_matrix.iloc[i, j] = pval
                    else:
                        pval_matrix.iloc[i, j] = np.nan
        
        return corr_matrix, pval_matrix
    
    def multicollinearity_detection(self, df: pd.DataFrame, numeric_cols: List[str] = None) -> pd.DataFrame:
        """Calculate Variance Inflation Factor (VIF) for multicollinearity"""
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [col for col in numeric_cols if 'id' not in col.lower()][:10]  # Limit to 10 features
        
        # Remove any columns with NaN or infinite values
        df_clean = df[numeric_cols].replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(df_clean) == 0 or len(numeric_cols) < 2:
            return pd.DataFrame({'Feature': [], 'VIF': []})
        
        try:
            vif_data = pd.DataFrame()
            vif_data['Feature'] = numeric_cols
            vif_data['VIF'] = [variance_inflation_factor(df_clean.values, i) 
                              for i in range(len(numeric_cols))]
            vif_data['Multicollinearity'] = vif_data['VIF'].apply(
                lambda x: 'High' if x > 10 else 'Moderate' if x > 5 else 'Low'
            )
            return vif_data.sort_values('VIF', ascending=False)
        except:
            return pd.DataFrame({'Feature': numeric_cols, 'VIF': [np.nan] * len(numeric_cols)})
    
    def time_series_decomposition(self, df: pd.DataFrame, value_col: str = 'data_value',
                                  pollutant: str = None, location: str = None) -> Dict:
        """Decompose time series into trend, seasonal, and residual components"""
        
        # Filter for specific pollutant and location
        if pollutant:
            df = df[df['name'].str.contains(pollutant, case=False, na=False)]
        if location:
            df = df[df['geo_place_name'] == location]
        
        # Must have datetime index
        if 'start_date' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['start_date']):
            return None
        
        # Sort and set index
        df = df.sort_values('start_date').set_index('start_date')
        
        # Resample to regular frequency (monthly) and handle missing values
        ts_data = df[value_col].resample('M').mean().fillna(method='ffill')
        
        if len(ts_data) < 24:  # Need at least 2 years for decomposition
            return None
        
        try:
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(ts_data, model='additive', period=12)
            
            return {
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'observed': decomposition.observed
            }
        except:
            return None
    
    def distribution_analysis(self, df: pd.DataFrame, value_col: str = 'data_value') -> Dict:
        """Analyze distribution characteristics for each pollutant"""
        
        results = {}
        
        for pollutant in df['name'].unique():
            pollutant_data = df[df['name'] == pollutant][value_col].dropna()
            
            if len(pollutant_data) < 3:
                continue
            
            # Normality test (Shapiro-Wilk)
            if len(pollutant_data) <= 5000:  # Shapiro-Wilk has sample size limit
                shapiro_stat, shapiro_p = stats.shapiro(pollutant_data)
            else:
                shapiro_stat, shapiro_p = np.nan, np.nan
            
            # Anderson-Darling test
            anderson_result = stats.anderson(pollutant_data)
            
            results[pollutant] = {
                'count': len(pollutant_data),
                'mean': pollutant_data.mean(),
                'median': pollutant_data.median(),
                'std': pollutant_data.std(),
                'skewness': skew(pollutant_data),
                'kurtosis': kurtosis(pollutant_data),
                'shapiro_stat': shapiro_stat,
                'shapiro_pvalue': shapiro_p,
                'is_normal': shapiro_p > 0.05 if not np.isnan(shapiro_p) else False,
                'anderson_stat': anderson_result.statistic,
                'distribution_type': 'Normal' if (not np.isnan(shapiro_p) and shapiro_p > 0.05) else 'Non-Normal'
            }
        
        return pd.DataFrame(results).T
    
    def anomaly_detection(self, df: pd.DataFrame, value_col: str = 'data_value',
                         contamination: float = 0.05) -> pd.DataFrame:
        """Detect anomalies using Isolation Forest"""
        
        # Prepare features for anomaly detection
        feature_cols = [value_col]
        
        # Add temporal features if available
        if 'month' in df.columns:
            feature_cols.append('month')
        if 'year' in df.columns:
            feature_cols.append('year')
        
        # Add rolling features if available
        rolling_cols = [col for col in df.columns if 'rolling' in col.lower()]
        if rolling_cols:
            feature_cols.extend(rolling_cols[:2])  # Add first 2 rolling features
        
        # Clean data
        df_clean = df[feature_cols].replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(df_clean) < 10:
            df['anomaly_score'] = 0
            df['is_anomaly'] = 0
            return df
        
        # Fit Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        df_clean['anomaly_score'] = iso_forest.fit_predict(df_clean[feature_cols])
        df_clean['is_anomaly'] = (df_clean['anomaly_score'] == -1).astype(int)
        
        # Merge back to original dataframe
        df = df.merge(df_clean[['anomaly_score', 'is_anomaly']], 
                     left_index=True, right_index=True, how='left')
        
        # Fill missing anomaly flags
        df['anomaly_score'].fillna(1, inplace=True)
        df['is_anomaly'].fillna(0, inplace=True)
        
        return df
    
    def stability_analysis(self, df: pd.DataFrame, value_col: str = 'data_value') -> pd.DataFrame:
        """Analyze time-series stability across regions"""
        
        stability_metrics = []
        
        for location in df['geo_place_name'].unique():
            for pollutant in df['name'].unique():
                subset = df[(df['geo_place_name'] == location) & (df['name'] == pollutant)]
                
                if len(subset) < 5:
                    continue
                
                # Calculate stability metrics
                cv = (subset[value_col].std() / subset[value_col].mean() * 100) if subset[value_col].mean() != 0 else 0
                range_val = subset[value_col].max() - subset[value_col].min()
                
                # Trend stability (if we have enough temporal data)
                if 'start_date' in subset.columns and len(subset) > 3:
                    subset_sorted = subset.sort_values('start_date')
                    trend_direction = 'Decreasing' if subset_sorted[value_col].iloc[-1] < subset_sorted[value_col].iloc[0] else 'Increasing'
                else:
                    trend_direction = 'Unknown'
                
                stability_metrics.append({
                    'location': location,
                    'pollutant': pollutant,
                    'coefficient_of_variation': cv,
                    'range': range_val,
                    'mean': subset[value_col].mean(),
                    'std': subset[value_col].std(),
                    'trend': trend_direction,
                    'stability_score': max(0, 100 - cv)  # Higher score = more stable
                })
        
        return pd.DataFrame(stability_metrics)


# Convenience functions
def perform_eda(df: pd.DataFrame) -> Dict:
    """Perform complete EDA and return all results"""
    analytics = AdvancedAnalytics()
    
    results = {
        'statistics': analytics.comprehensive_statistics(df),
        'distribution': analytics.distribution_analysis(df),
        'stability': analytics.stability_analysis(df)
    }
    
    # Correlation analysis
    corr, pval = analytics.correlation_analysis(df)
    results['correlation'] = corr
    results['correlation_pvalues'] = pval
    
    # VIF analysis
    results['vif'] = analytics.multicollinearity_detection(df)
    
    return results


if __name__ == "__main__":
    from data_processor import clean_air_quality_data
    from feature_engineering import engineer_features
    
    # Load and prepare data
    df, _ = clean_air_quality_data('Air_Quality.csv')
    df = engineer_features(df)
    
    # Perform EDA
    eda_results = perform_eda(df)
    
    print("\n=== EDA Results ===")
    print(f"\nStatistics shape: {eda_results['statistics'].shape}")
    print(f"Distribution analysis: {len(eda_results['distribution'])} pollutants")
    print(f"Stability metrics: {eda_results['stability'].shape[0]} location-pollutant pairs")
    print(f"\nTop 5 most stable regions:")
    print(eda_results['stability'].nlargest(5, 'stability_score')[['location', 'pollutant', 'stability_score']])
