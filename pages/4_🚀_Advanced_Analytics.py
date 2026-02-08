"""
Page 4: Advanced Analytics
AQSI, Spike Detection, Risk Calculator, Rankings, Clustering
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from modules.feature_engineering import engineer_features
from modules.analytics import AdvancedAnalytics
from modules.advanced_analytics import (
    AirQualityStabilityIndex,
    PollutionSpikeDetector,
    ExposureRiskCalculator,
    RegionalRanking,
    PollutionClusterAnalyzer,
    calculate_all_advanced_metrics
)
from utils.utils import sidebar_filters, apply_filters_to_data
from config import OUTLIER_CONFIG, FEATURE_CONFIG

st.set_page_config(page_title="Advanced Analytics", page_icon="🚀", layout="wide")

st.title("🚀 Advanced Analytics & Innovation Modules")
st.markdown("### Cutting-Edge Air Quality Intelligence")

@st.cache_data
def load_and_compute_advanced():
    df, _ = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    df = engineer_features(df, config=FEATURE_CONFIG)
    
    # Add anomaly detection
    analytics = AdvancedAnalytics()
    df = analytics.anomaly_detection(df)
    
    # Compute advanced metrics
    advanced_results = calculate_all_advanced_metrics(df)
    
    return df, advanced_results

try:
    with st.spinner("Computing advanced analytics..."):
        df, advanced_results = load_and_compute_advanced()
    
    # Tabs for different modules
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 AQSI",
        "⚡ Spike Detection",
        "🛡️ Risk Calculator",
        "🏆 Rankings",
        "🔮 Clustering"
    ])
    
    with tab1:
        st.subheader("Air Quality Stability Index (AQSI)")
        st.info("**AQSI Formula**: (1 - CV) × (1 - anomaly_rate) × trend_score × 100")
        
        if not advanced_results['aqsi'].empty:
            # Top 10 most stable
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 10 Most Stable (Highest AQSI)**")
                top_stable = advanced_results['aqsi'].head(10)
                st.dataframe(top_stable, use_container_width=True)
            
            with col2:
                st.write("**Top 10 Least Stable (Lowest AQSI)**")
                least_stable = advanced_results['aqsi'].tail(10)
                st.dataframe(least_stable, use_container_width=True)
            
            # Download full results
            st.download_button(
                "Download Full AQSI Results",
                advanced_results['aqsi'].to_csv(index=False).encode('utf-8'),
                "aqsi_scores.csv",
                "text/csv"
            )
        else:
            st.warning("AQSI data not available")
    
    with tab2:
        st.subheader("Pollution Spike Detection")
        st.info("Detects anomalous pollution spikes using statistical and contextual thresholds")
        
        if not advanced_results['spikes'].empty:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Spikes", len(advanced_results['spikes']))
            with col2:
                severe_spikes = len(advanced_results['spikes'][advanced_results['spikes']['severity'] == 'Severe'])
                st.metric("Severe Spikes", severe_spikes)
            with col3:
                avg_exceedance = advanced_results['spikes']['exceedance_pct'].mean()
                st.metric("Avg Exceedance", f"{avg_exceedance:.1f}%")
            
            # Top spikes
            st.write("**Top 20 Pollution Spikes**")
            st.dataframe(advanced_results['spikes'].head(20), use_container_width=True)
            
            # Filter by severity
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=['Severe', 'High', 'Moderate'],
                default=['Severe', 'High']
            )
            
            filtered_spikes = advanced_results['spikes'][
                advanced_results['spikes']['severity'].isin(severity_filter)
            ]
            
            st.write(f"**Filtered Spikes ({len(filtered_spikes)} records)**")
            st.dataframe(filtered_spikes, use_container_width=True)
        else:
            st.warning("No spikes detected")
    
    with tab3:
        st.subheader("Exposure Risk Calculator")
        
        # Interactive calculator
        st.write("**Interactive Risk Assessment**")
        
        exposure_hours = st.slider("Exposure Duration (hours)", 1, 168, 24)
        
        if st.button("Calculate Exposure Risk"):
            risk_calc = ExposureRiskCalculator()
            risk_results = risk_calc.calculate_risk(df, exposure_hours=exposure_hours)
            
            if not risk_results.empty:
                # Top risks
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Highest Risk Locations**")
                    high_risk = risk_results.nlargest(10, 'risk_score')
                    st.dataframe(high_risk, use_container_width=True)
                
                with col2:
                    st.write("**Lowest Risk Locations**")
                    low_risk = risk_results.nsmallest(10, 'risk_score')
                    st.dataframe(low_risk, use_container_width=True)
            else:
                st.warning("Risk calculation unavailable")
        
        if not advanced_results['exposure_risk'].empty:
            st.write("**Baseline Exposure Risk (24h)**")
            st.dataframe(advanced_results['exposure_risk'].head(20), use_container_width=True)
    
    with tab4:
        st.subheader("Regional Rankings")
        
        rankings = advanced_results['rankings']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Best Air Quality**")
            if 'best_quality' in rankings:
                st.dataframe(rankings['best_quality'], use_container_width=True)
            else:
                st.info("Data not available")
            
            if 'most_stable' in rankings:
                st.write("**⚖️ Most Stable Regions**")
                st.dataframe(rankings['most_stable'], use_container_width=True)
        
        with col2:
            st.write("**⚠️ Worst Air Quality**")
            if 'worst_quality' in rankings:
                st.dataframe(rankings['worst_quality'], use_container_width=True)
            else:
                st.info("Data not available")
            
            if 'most_improved' in rankings:
                st.write("**📈 Most Improved**")
                st.dataframe(rankings['most_improved'], use_container_width=True)
    
    with tab5:
        st.subheader("Geographic Clustering Analysis")
        st.info("K-means clustering based on multi-pollutant profiles")
        
        cluster_assignments = advanced_results['clusters']['assignments']
        cluster_profiles = advanced_results['clusters']['profiles']
        
        # Show cluster summary
        st.write("**Cluster Summary**")
        for cluster_name, profile in cluster_profiles.items():
            with st.expander(f"{cluster_name}: {profile['characterization']} ({profile['size']} locations)"):
                st.write("**Locations:**")
                st.write(", ".join(profile['locations'][:10]))  # Show first 10
                
                st.write("**Average Pollution Profile:**")
                profile_df = pd.DataFrame([profile['avg_pollution']]).T
                profile_df.columns = ['Average Level']
                st.dataframe(profile_df)
        
        # Download cluster assignments
        st.download_button(
            "Download Cluster Assignments",
            cluster_assignments.to_csv().encode('utf-8'),
            "cluster_assignments.csv",
            "text/csv"
        )

except FileNotFoundError:
    st.error("❌ Air_Quality.csv not found!")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.exception(e)
