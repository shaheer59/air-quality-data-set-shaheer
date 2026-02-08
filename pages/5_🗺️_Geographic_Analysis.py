"""
Page 5: Geographic Analysis
Advanced interactive mapping and spatial intelligence
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from modules.feature_engineering import engineer_features
from modules.visualizations import VisualizationFactory
from utils.utils import sidebar_filters, apply_filters_to_data
from config import OUTLIER_CONFIG, FEATURE_CONFIG, THEME_COLOR_PALETTE

# Page Config
st.set_page_config(page_title="Geographic Intelligence", page_icon="🗺️", layout="wide")

# Custom Metric Styling
st.markdown(f"""
<style>
    .map-container {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {THEME_COLOR_PALETTE['card_background']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Geographic Intelligence")
st.markdown(f"### <span style='color:{THEME_COLOR_PALETTE['secondary']}'>Spatial Analysis & Regional insights</span>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Load and clean data (includes coordinate enrichment)
    df, _ = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    df = engineer_features(df, config=FEATURE_CONFIG)
    return df

try:
    with st.spinner("Initializing geospatial engine..."):
        df = load_data()
    
    # Check if we have coordinates
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.error("⚠️ Spatial data not found. Please ensure coordinate enrichment is active.")
        st.stop()
        
    # Sidebar Controls
    st.sidebar.markdown("---")
    st.sidebar.header("🛠️ Map Controls")
    
    map_type = st.sidebar.selectbox(
        "Map Visualization Type",
        options=["Scatter Plot", "Heatmap", "Hexagon Density"],
        index=0
    )
    
    # Main Filters
    filters = sidebar_filters(df)
    filtered_df = apply_filters_to_data(df, filters)
    
    # Initialize Viz Factory
    viz = VisualizationFactory()
    
    # --- Top Section: Interactive Map ---
    col_map, col_stats = st.columns([2, 1])
    
    with col_map:
        st.subheader("📍 Interactive Pollution Map")
        st.caption(f"Showing {len(filtered_df)} data points across NYC")
        
        map_deck = viz.create_advanced_map(
            filtered_df,
            map_type=map_type.split(' ')[0].lower() # 'scatter', 'heatmap', 'hexagon'
        )
        
        if map_deck:
            st.pydeck_chart(map_deck, use_container_width=True)
        else:
            st.warning("Not enough data for this selection to generate map.")
            
    with col_stats:
        st.subheader("📊 Regional Snapshot")
        
        # Top 5 Polluted Regions
        top_regions = filtered_df.groupby('geo_place_name')['data_value'].mean().nlargest(5)
        
        st.markdown("##### Most Polluted Areas")
        for region, val in top_regions.items():
            st.markdown(f"""
            <div style="background-color:{THEME_COLOR_PALETTE['card_background']}; padding:10px; border-radius:8px; margin-bottom:8px; border-left: 4px solid {THEME_COLOR_PALETTE['danger']}">
                <div style="font-weight:bold; font-size:0.9rem;">{region}</div>
                <div style="color:{THEME_COLOR_PALETTE['danger']}; font-weight:bold;">{val:.2f} <span style="font-size:0.8rem; color:{THEME_COLOR_PALETTE['text_secondary']}">avg level</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Cleanest
        st.markdown("##### Cleanest Areas", unsafe_allow_html=True)
        clean_regions = filtered_df.groupby('geo_place_name')['data_value'].mean().nsmallest(3)
        for region, val in clean_regions.items():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.1); padding:4px 0;">
                <span style="color:{THEME_COLOR_PALETTE['success']}">{region}</span>
                <span>{val:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # --- Middle Section: Comparative Analysis ---
    st.subheader("🔍 Regional Comparison")
    
    tabs = st.tabs(["🌳 Hierarchy Tree", "🕸️ Pollutant Radar", "📉 Trends"])
    
    with tabs[0]:
        st.markdown("**Geographic Hierarchy (Borough > Neighborhood > Pollutant)**")
        fig_tree = viz.geographic_treemap(filtered_df)
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with tabs[1]:
        st.markdown("**Multi-Pollutant Regional Profile**")
        locations = filtered_df['geo_place_name'].unique()
        selected_radar = st.multiselect("Select Regions for Radar", options=locations, default=list(locations[:3]) if len(locations)>0 else [])
        
        if selected_radar:
             pollutants = [p.split('(')[0].strip() for p in filtered_df['name'].unique()]
             fig_radar = viz.radar_chart(
                 filtered_df, 
                 locations=selected_radar,
                 pollutants=pollutants[:5]
             )
             st.plotly_chart(fig_radar, use_container_width=True)
             
    with tabs[2]:
        st.markdown("**Regional Trends Over Time**")
        fig_trend = viz.animated_time_series(filtered_df, title="Pollution Evolution by Region")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    st.markdown("---")
    
    # --- Bottom: Data Table ---
    with st.expander("📥 View & Download Regional Data"):
        st.dataframe(filtered_df[['start_date', 'geo_place_name', 'name', 'data_value', 'latitude', 'longitude']].sort_values('start_date', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.exception(e)
