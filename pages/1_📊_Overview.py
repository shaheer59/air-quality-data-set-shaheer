"""
Page 1: Overview Dashboard
Executive summary, key metrics, and quick insights
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from modules.feature_engineering import engineer_features
from utils.utils import sidebar_filters, apply_filters_to_data, generate_insights, create_download_section, display_dataframe_stats
from modules.visualizations import VisualizationFactory
from config import OUTLIER_CONFIG, FEATURE_CONFIG

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("📊 Air Quality Overview Dashboard")
st.markdown("### Executive Summary & Key Insights")

# Load and prepare data
@st.cache_data
def load_data():
    df, report = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    df = engineer_features(df, config=FEATURE_CONFIG)
    return df, report

try:
    with st.spinner("Loading and processing data..."):
        df, cleaning_report = load_data()
    
    # Sidebar filters
    filters = sidebar_filters(df)
    filtered_df = apply_filters_to_data(df, filters)
    
    st.success(f"✅ Loaded {len(filtered_df):,} records")
    
    # Quick stats
    display_dataframe_stats(filtered_df)
    
    st.markdown("---")
    
    # Key Insights
    st.subheader("🔍 Auto-Generated Insights")
    insights = generate_insights(filtered_df)
    
    for insight in insights:
        st.info(insight)
    
    st.markdown("---")
    
    # Metrics Row
    st.subheader("📈 Key Environmental Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pollution = filtered_df['data_value'].mean()
        st.metric("Average Pollution Level", f"{avg_pollution:.2f}")
    
    with col2:
        max_pollution = filtered_df['data_value'].max()
        st.metric("Maximum Recorded", f"{max_pollution:.2f}")
    
    with col3:
        if 'is_anomaly' in filtered_df.columns:
            anomaly_count = filtered_df['is_anomaly'].sum()
            st.metric("Anomalies Detected", f"{anomaly_count:,}")
        else:
            st.metric("Locations Analyzed", filtered_df['geo_place_name'].nunique())
    
    with col4:
        if 'volatility_index' in filtered_df.columns:
            avg_volatility = filtered_df['volatility_index'].mean()
            st.metric("Avg Volatility Index", f"{avg_volatility:.1f}%")
        else:
            st.metric("Pollutants Tracked", filtered_df['name'].nunique())
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top Pollutants by Average Level")
        viz_factory = VisualizationFactory()
        fig = viz_factory.pollutant_comparison_bar(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Pollution Distribution")
        fig = viz_factory.distribution_box_plot(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series
    st.subheader("📉 Pollution Trends Over Time")
    if 'start_date' in filtered_df.columns:
        fig = viz_factory.time_series_line(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Temporal data not available for time-series visualization")
    
    # Regional Analysis
    st.subheader("🌍 Regional Snapshot")
    
    regional_avg = filtered_df.groupby('geo_place_name')['data_value'].agg(['mean', 'count']).reset_index()
    regional_avg.columns = ['Location', 'Average Pollution', 'Sample Count']
    regional_avg = regional_avg.sort_values('Average Pollution', ascending=False).head(10)
    
    st.dataframe(regional_avg, use_container_width=True)
    
    st.markdown("---")
    
    # Download Section
    create_download_section(filtered_df, "📥 Download Filtered Data")
    
    # Data Preview
    with st.expander("👀 View Raw Data"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

except FileNotFoundError:
    st.error("❌ Air_Quality.csv not found! Please ensure the data file is in the project directory.")
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please check that all required modules are installed and the data file exists.")
