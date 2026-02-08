"""
Utility Functions
Data loading, caching, theme management, export utilities
"""

import pandas as pd
import streamlit as st
from functools import wraps
import io
from typing import Callable
import os


def load_and_cache_data(filepath: str, force_reload: bool = False) -> pd.DataFrame:
    """Load data with caching support"""
    
    @st.cache_data(ttl=3600)
    def _load_data(path: str):
        return pd.read_csv(path)
    
    if force_reload:
        st.cache_data.clear()
    
    return _load_data(filepath)


def get_data_download_link(df: pd.DataFrame, filename: str = "data.csv",
                           link_text: str = "Download CSV") -> str:
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    return csv


def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply multiple filters to dataframe"""
    filtered_df = df.copy()
    
    for column, values in filters.items():
        if column in filtered_df.columns and values:
            if isinstance(values, list):
                filtered_df = filtered_df[filtered_df[column].isin(values)]
            else:
                filtered_df = filtered_df[filtered_df[column] == values]
    
    return filtered_df


def create_metric_card(label: str, value, delta=None, help_text=None):
    """Create a metric display card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=label, value=value, delta=delta, help=help_text)


def format_large_number(num: float, decimals: int = 2) -> str:
    """Format large numbers with K, M, B suffixes"""
    if abs(num) >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{decimals}f}B"
    elif abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.{decimals}f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def get_color_for_aqi(category: str) -> str:
    """Get color code for AQI category"""
    color_map = {
        'Good': '#00E400',
        'Moderate': '#FFFF00',
        'Unhealthy for Sensitive Groups': '#FF7E00',
        'Unhealthy': '#FF0000',
        'Very Unhealthy': '#8F3F97',
        'Hazardous': '#7E0023'
    }
    return color_map.get(category, '#808080')


def sidebar_filters(df: pd.DataFrame) -> dict:
    """Create standard sidebar filters"""
    st.sidebar.header("🔍 Filters")
    
    filters = {}
    
    # Date range filter
    if 'start_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['start_date']):
        min_date = df['start_date'].min()
        max_date = df['start_date'].max()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            filters['date_range'] = date_range
    
    # Year filter
    if 'year' in df.columns:
        years = sorted(df['year'].dropna().unique())
        if years:
            selected_years = st.sidebar.multiselect(
                "Year",
                options=years,
                default=years
            )
            filters['year'] = selected_years
    
    # Pollutant filter
    if 'name' in df.columns:
        pollutants = sorted(df['name'].unique())
        selected_pollutants = st.sidebar.multiselect(
            "Pollutant",
            options=pollutants,
            default=pollutants[:3] if len(pollutants) > 3 else pollutants
        )
        filters['name'] = selected_pollutants
    
    # Location filter
    if 'geo_place_name' in df.columns:
        locations = sorted(df['geo_place_name'].unique())
        selected_locations = st.sidebar.multiselect(
            "Location",
            options=locations,
            default=None
        )
        if selected_locations:
            filters['geo_place_name'] = selected_locations
    
    # Geography type filter
    if 'geo_type_name' in df.columns:
        geo_types = sorted(df['geo_type_name'].unique())
        selected_geo_type = st.sidebar.selectbox(
            "Geography Type",
            options=['All'] + geo_types
        )
        if selected_geo_type != 'All':
            filters['geo_type_name'] = selected_geo_type
    
    return filters


def apply_filters_to_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filters to dataframe"""
    filtered_df = df.copy()
    
    # Apply date range
    if 'date_range' in filters and len(filters['date_range']) == 2:
        filtered_df = filtered_df[
            (filtered_df['start_date'] >= pd.Timestamp(filters['date_range'][0])) &
            (filtered_df['start_date'] <= pd.Timestamp(filters['date_range'][1]))
        ]
    
    # Apply other filters
    for key, values in filters.items():
        if key != 'date_range' and key in filtered_df.columns and values:
            if isinstance(values, list):
                filtered_df = filtered_df[filtered_df[key].isin(values)]
            else:
                filtered_df = filtered_df[filtered_df[key] == values]
    
    return filtered_df


def generate_insights(df: pd.DataFrame) -> list:
    """Auto-generate key insights from data"""
    insights = []
    
    # Overall pollution trend
    if 'year' in df.columns and len(df['year'].unique()) > 1:
        yearly_avg = df.groupby('year')['data_value'].mean()
        trend = "decreasing" if yearly_avg.iloc[-1] < yearly_avg.iloc[0] else "increasing"
        pct_change = abs((yearly_avg.iloc[-1] - yearly_avg.iloc[0]) / yearly_avg.iloc[0] * 100)
        insights.append(f"📊 Overall pollution has been {trend} by {pct_change:.1f}% from {int(yearly_avg.index[0])} to {int(yearly_avg.index[-1])}")
    
    # Worst pollutant
    if 'name' in df.columns:
        worst_pollutant = df.groupby('name')['data_value'].mean().idxmax()
        insights.append(f"⚠️ Highest average pollution: {worst_pollutant}")
    
    # Best location
    if 'geo_place_name' in df.columns:
        best_location = df.groupby('geo_place_name')['data_value'].mean().idxmin()
        insights.append(f"✅ Cleanest area: {best_location}")
    
    # Anomaly count
    if 'is_anomaly' in df.columns:
        anomaly_count = df['is_anomaly'].sum()
        anomaly_pct = (anomaly_count / len(df) * 100)
        insights.append(f"🚨 Detected {anomaly_count} anomalies ({anomaly_pct:.2f}% of data)")
    
    return insights


def export_to_csv(df: pd.DataFrame, filename: str = "export.csv"):
    """Export dataframe to CSV"""
    csv = df.to_csv(index=False).encode('utf-8')
    return csv


def display_dataframe_stats(df: pd.DataFrame):
    """Display quick dataframe statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Date Range", f"{df['year'].min():.0f}-{df['year'].max():.0f}" if 'year' in df.columns else "N/A")
    with col4:
        st.metric("Locations", df['geo_place_name'].nunique() if 'geo_place_name' in df.columns else "N/A")


def create_download_section(df: pd.DataFrame, section_title: str = "📥 Download Data"):
    """Create a download section with multiple format options"""
    st.subheader(section_title)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = export_to_csv(df, "air_quality_data.csv")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="air_quality_data.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        st.download_button(
            label="Download as Excel",
            data=buffer.getvalue(),
            file_name="air_quality_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


if __name__ == "__main__":
    print("Utility functions module ready!")
