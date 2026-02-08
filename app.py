"""
Air Quality Intelligence Platform - Main Streamlit Application
A production-level analytics dashboard for air quality data
"""

import streamlit as st
import sys
import os

# Force UTF-8 encoding for stdout/stderr to prevent Windows charmap errors
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add modules to path
sys.path.append(os.path.dirname(__file__))

# Import configuration
from config import STREAMLIT_CONFIG

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

# Import theme config
from config import THEME_COLOR_PALETTE

# Custom CSS for Premium Dark Mode
st.markdown(f"""
<style>
    /* Main Background */
    .stApp {{
        background-color: {THEME_COLOR_PALETTE['background']};
        color: {THEME_COLOR_PALETTE['text_primary']};
    }}
    
    /* Headers */
    .main-header {{
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, {THEME_COLOR_PALETTE['primary']} 0%, {THEME_COLOR_PALETTE['secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    
    .subtitle {{
        font-size: 1.2rem;
        color: {THEME_COLOR_PALETTE['text_secondary']};
        margin-bottom: 2rem;
        font-weight: 300;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background-color: {THEME_COLOR_PALETTE['card_background']};
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
        border-color: {THEME_COLOR_PALETTE['primary']};
    }}
    
    /* Streamlit Components Override */
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem;
        font-weight: 600;
        color: {THEME_COLOR_PALETTE['text_primary']};
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 0.9rem;
        color: {THEME_COLOR_PALETTE['text_secondary']};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 20px;
        background-color: {THEME_COLOR_PALETTE['card_background']};
        border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.05);
        color: {THEME_COLOR_PALETTE['text_secondary']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {THEME_COLOR_PALETTE['primary']} !important;
        color: white !important;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {THEME_COLOR_PALETTE['card_background']};
        border-right: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Charts */
    .js-plotly-plot .plotly .modebar {{
        orientation: v;
        top: 0;
        right: 0;
        transform: translateY(0);
    }}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🌍 Air Quality Intelligence")
st.sidebar.markdown("---")

# Application info
st.sidebar.info(
    """
    **About This Platform**
    
    A production-level air quality analytics platform featuring:
    
    - 🧹 Professional data cleaning
    - 📊 Deep exploratory analysis
    - 🎨 Advanced visualizations
    - 🚀 Innovative analytics
    - 🗺️ Geographic intelligence
    - 🔮 Predictive forecasting
    
    **Data**: NYC Air Quality (2008-2021)
    """
)

# Main content
st.markdown('<p class="main-header">🌍 Air Quality Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Professional-Grade Environmental Analytics & Forecasting System</p>', unsafe_allow_html=True)

st.markdown("---")

# Welcome section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Overview")
    st.write("""
    Explore comprehensive air quality trends, patterns, and insights across NYC regions from 2008-2021.
    """)

with col2:
    st.markdown("### 🚀 Advanced Analytics")
    st.write("""
    Access cutting-edge analytics including AQSI scores, spike detection, and ML-based forecasting.
    """)

with col3:
    st.markdown("### 🗺️ Geographic Intelligence")
    st.write("""
    Discover spatial patterns, regional comparisons, and location-specific pollution profiles.
    """)

st.markdown("---")

# Quick Stats Section
st.subheader("📈 Platform Capabilities")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; color:{THEME_COLOR_PALETTE['primary']}">16,218</h3>
        <p style="margin:0; color:{THEME_COLOR_PALETTE['text_secondary']}">Total Records</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; color:{THEME_COLOR_PALETTE['secondary']}">3</h3>
        <p style="margin:0; color:{THEME_COLOR_PALETTE['text_secondary']}">Pollutants Tracked</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; color:{THEME_COLOR_PALETTE['accent']}">13+</h3>
        <p style="margin:0; color:{THEME_COLOR_PALETTE['text_secondary']}">Years of Data</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin:0; color:{THEME_COLOR_PALETTE['warning']}">100+</h3>
        <p style="margin:0; color:{THEME_COLOR_PALETTE['text_secondary']}">NYC Regions</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Navigation Guide
st.subheader("🧭 Navigation Guide")

st.write("Use the pages in the sidebar to explore different aspects of the platform:")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.markdown("""
    **📊 1. Overview**
    - Executive summary and key metrics
    - Auto-generated insights
    - Quick data exploration
    
    **🧹 2. Data Quality**
    - Cleaning audit log
    - Missing value analysis
    - Outlier detection results
    
   **🔬 3. Exploratory Analysis**
    - Statistical summaries
    - Distribution analysis
    - Correlation matrices
    - Time-series decomposition
    """)

with nav_col2:
    st.markdown("""
    **🚀 4. Advanced Analytics**
    - Air Quality Stability Index (AQSI)
    - Pollution spike detection
    - Exposure risk calculator
    - Regional rankings
    - Clustering analysis
    
    **🗺️ 5. Geographic Analysis**
    - Regional comparisons
    - Spatial patterns
    - Multi-pollutant profiles
    
    **🔮 6. Forecasting**
    - ARIMA time-series forecasts
    - Confidence intervals
    - Model performance metrics
    """)

st.markdown("---")

# Technology Stack
with st.expander("🛠️ Technology Stack"):
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        **Data Processing**
        - pandas
        - numpy
        - scipy
        """)
    
    with tech_col2:
        st.markdown("""
        **Analytics & ML**
        - scikit-learn
        - statsmodels
        - prophet
        """)
    
    with tech_col3:
        st.markdown("""
        **Visualization**
        - plotly
        - streamlit
        - matplotlib
        """)

# Footer
st.markdown("---")
st.caption("💡 **Tip**: Use the sidebar filters on each page to customize your analysis")
st.caption("🌟 **Built with**: Streamlit • Python • Advanced Analytics • 2026-level Intelligence")
