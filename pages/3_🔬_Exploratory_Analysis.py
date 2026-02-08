"""
Page 3: Exploratory Data Analysis
Statistical analysis, correlations, distributions, and decomposition
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from modules.feature_engineering import engineer_features
from modules.analytics import AdvancedAnalytics, perform_eda
from modules.visualizations import VisualizationFactory
from utils.utils import sidebar_filters, apply_filters_to_data
from config import OUTLIER_CONFIG, FEATURE_CONFIG

st.set_page_config(page_title="EDA", page_icon="🔬", layout="wide")

st.title("🔬 Exploratory Data Analysis")
st.markdown("### Deep Statistical Analysis & Pattern Discovery")

@st.cache_data
def load_and_analyze():
    df, _ = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    df = engineer_features(df, config=FEATURE_CONFIG)
    eda_results = perform_eda(df)
    return df, eda_results

try:
    with st.spinner("Performing deep statistical analysis..."):
        df, eda_results = load_and_analyze()
    
    filters = sidebar_filters(df)
    filtered_df = apply_filters_to_data(df, filters)
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Statistics",
        "📈 Distributions",
        "🔗 Correlations",
        "🌊 Time Series",
        "⚡ Stability"
    ])
    
    with tab1:
        st.subheader("Comprehensive Statistical Summary")
        
        # Show statistics
        if not eda_results['statistics'].empty:
            st.dataframe(eda_results['statistics'].head(20), use_container_width=True)
            
            st.download_button(
                "Download Full Statistics",
                eda_results['statistics'].to_csv(index=False).encode('utf-8'),
                "statistics.csv",
                "text/csv"
            )
        else:
            st.warning("No statistical data available")
    
    with tab2:
        st.subheader("Distribution Analysis")
        
        # Distribution characteristics
        if not eda_results['distribution'].empty:
            st.write("**Normality Tests & Distribution Characteristics**")
            st.dataframe(eda_results['distribution'], use_container_width=True)
            
            # Histogram
            viz = VisualizationFactory()
            fig = viz.histogram_distribution(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Distribution data not available")
    
    with tab3:
        st.subheader("Correlation Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            viz = VisualizationFactory()
            if not eda_results['correlation'].empty:
                # Select top correlated features
                corr_subset = eda_results['correlation'].iloc[:10, :10]
                fig = viz.correlation_heatmap(corr_subset, "Feature Correlation Matrix")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Correlation data not available")
        
        with col2:
            st.write("**Multicollinearity (VIF)**")
            if not eda_results['vif'].empty:
                st.dataframe(eda_results['vif'].head(10), use_container_width=True)
            else:
                st.info("VIF data not available")
    
    with tab4:
        st.subheader("Time Series Analysis")
        
        # Time series decomposition
        analytics = AdvancedAnalytics()
        
        # Location selector
        locations = filtered_df['geo_place_name'].unique()
        selected_location = st.selectbox("Select Location", locations[:10])
        
        # Pollutant selector
        pollutants = filtered_df['name'].unique()
        selected_pollutant = st.selectbox("Select Pollutant", pollutants)
        
        if st.button("Decompose Time Series"):
            with st.spinner("Decomposing time series..."):
                decomposition = analytics.time_series_decomposition(
                    filtered_df, 
                    location=selected_location,
                    pollutant=selected_pollutant.split('(')[0].strip()
                )
                
                if decomposition:
                    viz = VisualizationFactory()
                    fig = viz.seasonal_decomposition_plot(decomposition)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Insufficient data for decomposition. Need at least 24 months of data.")
    
    with tab5:
        st.subheader("Regional Stability Analysis")
        
        if not eda_results['stability'].empty:
            # Top stable regions
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Stable Regions**")
                stable = eda_results['stability'].nlargest(10, 'stability_score')
                st.dataframe(stable[['location', 'pollutant', 'stability_score']], use_container_width=True)
            
            with col2:
                st.write("**Most Volatile Regions**")
                volatile = eda_results['stability'].nsmallest(10, 'stability_score')
                st.dataframe(volatile[['location', 'pollutant', 'stability_score']], use_container_width=True)
        else:
            st.warning("Stability data not available")

except FileNotFoundError:
    st.error("❌ Air_Quality.csv not found!")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.exception(e)
