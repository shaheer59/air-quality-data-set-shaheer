"""
Advanced Analytics Modules - Innovation Layer
AQSI, Spike Detection, Risk Calculator, Forecasting, Clustering
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class AirQualityStabilityIndex:
    """Calculate Air Quality Stability Index (AQSI)"""
    
    def calculate_aqsi(self, df: pd.DataFrame, by_location: bool = True) -> pd.DataFrame:
        """
        AQSI Formula: (1 - CV) × (1 - anomaly_rate) × trend_score × 100
        Range: 0-100 (higher = more stable)
        """
        
        groupby_cols = ['geo_place_name', 'name'] if by_location else ['name']
        
        aqsi_results = []
        
        for group_keys, group_df in df.groupby(groupby_cols):
            if len(group_df) < 5:
                continue
            
            # Component 1: Coefficient of Variation (CV)
            mean_val = group_df['data_value'].mean()
            std_val = group_df['data_value'].std()
            cv = (std_val / mean_val) if mean_val != 0 else 1
            cv_score = max(0, 1 - min(cv, 1))  # Normalize to 0-1
            
            # Component 2: Anomaly Rate
            anomaly_rate = group_df['is_anomaly'].mean() if 'is_anomaly' in group_df.columns else 0
            anomaly_score = 1 - anomaly_rate
            
            # Component 3: Trend Score (improving trend = higher score)
            if 'year' in group_df.columns and len(group_df) > 3:
                yearly_avg = group_df.groupby('year')['data_value'].mean()
                trend_slope = np.polyfit(range(len(yearly_avg)), yearly_avg.values, 1)[0]
                # Negative slope (decreasing pollution) is good
                trend_score = max(0, min(1, 0.5 - trend_slope * 0.1))
            else:
                trend_score = 0.5  # Neutral if no trend data
            
            # Calculate AQSI
            aqsi = cv_score * anomaly_score * trend_score * 100
            
            if by_location:
                location, pollutant = group_keys
                aqsi_results.append({
                    'location': location,
                    'pollutant': pollutant,
                    'aqsi_score': aqsi,
                    'cv_component': cv_score * 100,
                    'anomaly_component': anomaly_score * 100,
                    'trend_component': trend_score * 100,
                    'interpretation': self._interpret_aqsi(aqsi)
                })
            else:
                aqsi_results.append({
                    'pollutant': group_keys,
                    'aqsi_score': aqsi,
                    'interpretation': self._interpret_aqsi(aqsi)
                })
        
        return pd.DataFrame(aqsi_results).sort_values('aqsi_score', ascending=False)
    
    def _interpret_aqsi(self, score: float) -> str:
        """Interpret AQSI score"""
        if score >= 70:
            return 'Very Stable'
        elif score >= 50:
            return 'Stable'
        elif score >= 30:
            return 'Moderately Stable'
        else:
            return 'Unstable'


class PollutionSpikeDetector:
    """Detect and classify pollution spikes"""
    
    def detect_spikes(self, df: pd.DataFrame, threshold_std: float = 2.0) -> pd.DataFrame:
        """Detect pollution spikes using statistical thresholds"""
        
        spike_results = []
        
        for (location, pollutant), group_df in df.groupby(['geo_place_name', 'name']):
            if len(group_df) < 10:
                continue
            
            mean_val = group_df['data_value'].mean()
            std_val = group_df['data_value'].std()
            
            # Statistical threshold
            threshold = mean_val + threshold_std * std_val
            
            # Rolling mean threshold (for contextual spikes)
            if 'rolling_avg_30d' in group_df.columns:
                group_df['spike_contextual'] = group_df['data_value'] > (group_df['rolling_avg_30d'] * 1.5)
            else:
                group_df['spike_contextual'] = False
            
            # Statistical spike
            group_df['spike_statistical'] = group_df['data_value'] > threshold
            
            # Combined spike detection
            spikes = group_df[group_df['spike_statistical'] | group_df['spike_contextual']]
            
            for idx, spike_row in spikes.iterrows():
                severity = self._classify_spike_severity(
                    spike_row['data_value'],
                    mean_val,
                    std_val
                )
                
                spike_results.append({
                    'location': location,
                    'pollutant': pollutant,
                    'date': spike_row.get('start_date', 'Unknown'),
                    'value': spike_row['data_value'],
                    'mean': mean_val,
                    'threshold': threshold,
                    'severity': severity,
                    'exceedance_pct': ((spike_row['data_value'] - mean_val) / mean_val * 100)
                })
        
        return pd.DataFrame(spike_results).sort_values('exceedance_pct', ascending=False)
    
    def _classify_spike_severity(self, value: float, mean: float, std: float) -> str:
        """Classify spike severity"""
        z_score = (value - mean) / std if std > 0 else 0
        
        if z_score >= 3:
            return 'Severe'
        elif z_score >= 2.5:
            return 'High'
        else:
            return 'Moderate'


class ExposureRiskCalculator:
    """Calculate exposure risk based on AQI and duration"""
    
    def calculate_risk(self, df: pd.DataFrame,
                      exposure_hours: float = 24) -> pd.DataFrame:
        """
        Calculate exposure risk
        Risk = AQI_score × exposure_duration_weight × sensitivity_factor
        """
        
        risk_results = []
        
        for location in df['geo_place_name'].unique():
            location_df = df[df['geo_place_name'] == location]
            
            for pollutant in location_df['name'].unique():
                pollutant_df = location_df[location_df['name'] == pollutant]
                
                avg_value = pollutant_df['data_value'].mean()
                max_value = pollutant_df['data_value'].max()
                
                # Simple risk score (adjust based on pollutant type)
                base_risk = avg_value * (exposure_hours / 24)
                
                # Risk category
                if 'aqi_category' in pollutant_df.columns:
                    category = pollutant_df['aqi_category'].mode()[0] if not pollutant_df['aqi_category'].mode().empty else 'Unknown'
                    risk_level = self._determine_risk_level(category)
                else:
                    risk_level = 'Unknown'
                
                risk_results.append({
                    'location': location,
                    'pollutant': pollutant,
                    'avg_exposure': avg_value,
                    'max_exposure': max_value,
                    'risk_score': base_risk,
                    'risk_level': risk_level,
                    'exposure_hours': exposure_hours
                })
        
        return pd.DataFrame(risk_results).sort_values('risk_score', ascending=False)
    
    def _determine_risk_level(self, aqi_category: str) -> str:
        """Map AQI category to risk level"""
        risk_mapping = {
            'Good': 'Low',
            'Moderate': 'Low-Moderate',
            'Unhealthy for Sensitive Groups': 'Moderate',
            'Unhealthy': 'High',
            'Very Unhealthy': 'Very High',
            'Hazardous': 'Extreme'
        }
        return risk_mapping.get(aqi_category, 'Unknown')


class RegionalRanking:
    """Rank regions by various metrics"""
    
    def rank_regions(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create comprehensive regional rankings"""
        
        rankings = {}
        
        # 1. Best air quality (lowest average pollution)
        best_quality = df.groupby('geo_place_name')['data_value'].mean().sort_values()
        rankings['best_quality'] = pd.DataFrame({
            'location': best_quality.index,
            'avg_pollution': best_quality.values,
            'rank': range(1, len(best_quality) + 1)
        }).head(10)
        
        # 2. Worst air quality
        rankings['worst_quality'] = pd.DataFrame({
            'location': best_quality.index[::-1],
            'avg_pollution': best_quality.values[::-1],
            'rank': range(1, len(best_quality) + 1)
        }).head(10)
        
        # 3. Most stable (lowest volatility)
        if 'volatility_index' in df.columns:
            stability = df.groupby('geo_place_name')['volatility_index'].mean().sort_values()
            rankings['most_stable'] = pd.DataFrame({
                'location': stability.index,
                'volatility_index': stability.values,
                'rank': range(1, len(stability) + 1)
            }).head(10)
        
        # 4. Most improved (best trend)
        if 'year' in df.columns:
            improvement = []
            for location in df['geo_place_name'].unique():
                loc_df = df[df['geo_place_name'] == location]
                yearly = loc_df.groupby('year')['data_value'].mean()
                if len(yearly) > 1:
                    change_pct = ((yearly.iloc[-1] - yearly.iloc[0]) / yearly.iloc[0] * 100)
                    improvement.append({'location': location, 'change_pct': change_pct})
            
            if improvement:
                rankings['most_improved'] = pd.DataFrame(improvement).sort_values('change_pct').head(10)
                rankings['most_improved']['rank'] = range(1, len(rankings['most_improved']) + 1)
        
        return rankings


class PollutionForecaster:
    """Time-series forecasting using ARIMA"""
    
    def forecast_arima(self, df: pd.DataFrame,
                      location: str,
                      pollutant: str,
                      periods: int = 12) -> Dict:
        """Forecast using ARIMA model"""
        
        # Filter data
        forecast_df = df[
            (df['geo_place_name'] == location) &
            (df['name'].str.contains(pollutant, case=False, na=False))
        ].copy()
        
        if len(forecast_df) < 20:
            return None
        
        # Sort by date and create time series
        forecast_df = forecast_df.sort_values('start_date')
        ts_data = forecast_df.set_index('start_date')['data_value']
        ts_data = ts_data.resample('M').mean().fillna(method='ffill')
        
        try:
            # Fit ARIMA model (auto-select parameters)
            model = ARIMA(ts_data, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            forecast = fitted_model.forecast(steps=periods)
            forecast_index = pd.date_range(start=ts_data.index[-1], periods=periods + 1, freq='M')[1:]
            
            # Confidence intervals
            conf_int = fitted_model.get_forecast(steps=periods).conf_int()
            
            return {
                'historical': ts_data,
                'forecast': pd.Series(forecast.values, index=forecast_index),
                'lower_ci': conf_int.iloc[:, 0],
                'upper_ci': conf_int.iloc[:, 1],
                'model_summary': fitted_model.summary()
            }
        except Exception as e:
            print(f"Forecasting error: {e}")
            return None


class PollutionClusterAnalyzer:
    """Cluster regions based on pollution behavior"""
    
    def cluster_regions(self, df: pd.DataFrame, n_clusters: int = 5) -> Tuple[pd.DataFrame, Dict]:
        """Cluster locations based on pollution profiles"""
        
        # Create feature matrix: average pollution by pollutant type for each location
        pivot_df = df.pivot_table(
            values='data_value',
            index='geo_place_name',
            columns='name',
            aggfunc='mean'
        ).fillna(0)
        
        if len(pivot_df) < n_clusters:
            n_clusters = max(2, len(pivot_df) // 2)
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(pivot_df)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_features)
        
        # Add cluster labels
        pivot_df['cluster'] = clusters
        
        # Characterize clusters
        cluster_profiles = {}
        for cluster_id in range(n_clusters):
            cluster_locs = pivot_df[pivot_df['cluster'] == cluster_id]
            profile = {
                'locations': cluster_locs.index.tolist(),
                'size': len(cluster_locs),
                'avg_pollution': cluster_locs.drop('cluster', axis=1).mean().to_dict(),
                'characterization': self._characterize_cluster(cluster_locs.drop('cluster', axis=1))
            }
            cluster_profiles[f'Cluster_{cluster_id}'] = profile
        
        return pivot_df, cluster_profiles
    
    def _characterize_cluster(self, cluster_data: pd.DataFrame) -> str:
        """Characterize cluster based on pollution levels"""
        avg_total = cluster_data.mean().mean()
        
        if avg_total < cluster_data.values.mean() * 0.7:
            return 'Low Pollution Zone'
        elif avg_total > cluster_data.values.mean() * 1.3:
            return 'High Pollution Zone'
        else:
            return 'Moderate Pollution Zone'


# Convenience functions
def calculate_all_advanced_metrics(df: pd.DataFrame) -> Dict:
    """Calculate all advanced analytics"""
    
    results = {}
    
    # AQSI
    aqsi_calc = AirQualityStabilityIndex()
    results['aqsi'] = aqsi_calc.calculate_aqsi(df)
    
    # Spike Detection
    spike_detector = PollutionSpikeDetector()
    results['spikes'] = spike_detector.detect_spikes(df)
    
    # Exposure Risk
    risk_calc = ExposureRiskCalculator()
    results['exposure_risk'] = risk_calc.calculate_risk(df)
    
    # Regional Rankings
    ranker = RegionalRanking()
    results['rankings'] = ranker.rank_regions(df)
    
    # Clustering
    clusterer = PollutionClusterAnalyzer()
    cluster_df, cluster_profiles = clusterer.cluster_regions(df)
    results['clusters'] = {'assignments': cluster_df, 'profiles': cluster_profiles}
    
    return results


if __name__ == "__main__":
    print("Advanced Analytics Module Ready!")
    print("Available modules:")
    print("  - AirQualityStabilityIndex (AQSI)")
    print("  - PollutionSpikeDetector")
    print("  - ExposureRiskCalculator")
    print("  - RegionalRanking")
    print("  - PollutionForecaster (ARIMA)")
    print("  - PollutionClusterAnalyzer")
