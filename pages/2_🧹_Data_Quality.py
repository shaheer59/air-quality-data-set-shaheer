"""
Page 2: Data Quality Report
Transparency into data cleaning, outliers, and data health
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from config import OUTLIER_CONFIG

st.set_page_config(page_title="Data Quality", page_icon="🧹", layout="wide")

st.title("🧹 Data Quality & Cleaning Report")
st.markdown("### Comprehensive Data Health Analysis")

@st.cache_data
def load_data_and_report():
    df, report = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    return df, report

try:
    with st.spinner("Processing data quality report..."):
        df, cleaning_report = load_data_and_report()
    
    # Summary Metrics
    st.subheader("📊 Cleaning Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Original Records",
            f"{cleaning_report['original_shape'][0]:,}",
            help="Total records before cleaning"
        )
    
    with col2:
        st.metric(
            "Clean Records",
            f"{cleaning_report['cleaned_shape'][0]:,}",
            delta=f"-{cleaning_report['rows_removed']:,}",
            help="Records after cleaning"
        )
    
    with col3:
        st.metric(
            "Features Added",
            f"+{cleaning_report['columns_added']}",
            help="New engineered features"
        )
    
    with col4:
        st.metric(
            "Processing Steps",
            cleaning_report['cleaning_steps'],
            help="Total cleaning operations"
        )
    
    st.markdown("---")
    
    # Cleaning Audit Log
    st.subheader("📋 Cleaning Audit Log")
    st.info("Detailed log of all data cleaning operations performed")
    
    for log_entry in cleaning_report['log']:
        st.text(log_entry)
    
    st.markdown("---")
    
    # Missing Values Analysis
    st.subheader("🔍 Missing Values Analysis")
    
    missing_df = pd.DataFrame({
        'Column': df.columns,
        'Missing Count': df.isnull().sum().values,
        'Missing Percentage': (df.isnull().sum().values / len(df) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("✅ No missing values detected after cleaning!")
    
    st.markdown("---")
    
    # Outlier Analysis
    st.subheader("⚠️ Outlier Detection Results")
    
    outlier_cols = [col for col in df.columns if 'outlier_flag' in col]
    
    if outlier_cols:
        outlier_summary = []
        for col in outlier_cols:
            base_col = col.replace('_outlier_flag', '')
            outlier_count = df[col].sum()
            outlier_pct = (outlier_count / len(df) * 100)
            
            outlier_summary.append({
                'Feature': base_col,
                'Outliers Detected': outlier_count,
                'Percentage': f"{outlier_pct:.2f}%"
            })
        
        outlier_df = pd.DataFrame(outlier_summary)
        st.dataframe(outlier_df, use_container_width=True)
        
        # Outlier visualization
        st.subheader("📊 Outlier Distribution")
        selected_feature = st.selectbox("Select feature to visualize", [s['Feature'] for s in outlier_summary])
        
        import plotly.express as px
        fig = px.box(df, y=selected_feature, title=f"Distribution of {selected_feature} with Outliers")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No outlier flags found in processed data")
    
    st.markdown("---")
    
    # Data Type Summary
    st.subheader("🔢 Data Type Summary")
    
    dtype_df = pd.DataFrame({
        'Column': df.dtypes.index,
        'Data Type': df.dtypes.values.astype(str),
        'Unique Values': [df[col].nunique() for col in df.columns],
        'Sample Value': [str(df[col].iloc[0])[:50] if len(df) > 0 else 'N/A' for col in df.columns]
    })
    
    st.dataframe(dtype_df, use_container_width=True)
    
    # Data Health Score
    st.markdown("---")
    st.subheader("💯 Overall Data Health Score")
    
    # Calculate health score
    completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    uniqueness = (df.drop_duplicates().shape[0] / len(df)) * 100
    outlier_ratio = (sum([df[col].sum() for col in outlier_cols]) / len(df)) * 10 if outlier_cols else 0
    health_score = ((completeness + uniqueness) / 2) - outlier_ratio
    health_score = max(0, min(100, health_score))
    
    st.progress(health_score / 100)
    st.metric("Data Health Score", f"{health_score:.1f}/100")
    
    health_interpretation = "Excellent" if health_score >= 90 else "Good" if health_score >= 75 else "Fair" if health_score >= 60 else "Poor"
    st.info(f"**Interpretation**: {health_interpretation} - This dataset is suitable for analysis")

except FileNotFoundError:
    st.error("❌ Air_Quality.csv not found!")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
