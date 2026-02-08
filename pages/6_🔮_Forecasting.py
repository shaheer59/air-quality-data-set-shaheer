"""
Page 6: Forecasting
ARIMA time-series forecasting with confidence intervals
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.data_processor import clean_air_quality_data
from modules.feature_engineering import engineer_features
from modules.advanced_analytics import PollutionForecaster
import plotly.graph_objects as go
from config import OUTLIER_CONFIG, FEATURE_CONFIG

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")

st.title("🔮 Air Quality Forecasting")
st.markdown("### Predictive Analytics Using ARIMA Models")

@st.cache_data
def load_data():
    df, _ = clean_air_quality_data('Air_Quality.csv', config=OUTLIER_CONFIG)
    df = engineer_features(df, config=FEATURE_CONFIG)
    return df

try:
    with st.spinner("Loading data for forecasting..."):
        df = load_data()
    
    st.info("**Note**: ARIMA forecasting requires time-series data with sufficient temporal coverage")
    
    # Forecast configuration
    st.subheader("⚙️ Forecast Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Location selector
        locations = df['geo_place_name'].unique()
        selected_location = st.selectbox("Select Location", sorted(locations))
    
    with col2:
        # Pollutant selector
        pollutants = df['name'].unique()
        selected_pollutant = st.selectbox("Select Pollutant", pollutants)
    
    with col3:
        # Forecast horizon
        forecast_periods = st.slider("Forecast Periods (months)", 3, 24, 12)
    
    # Run forecast
    if st.button("🚀 Generate Forecast", type="primary"):
        with st.spinner(f"Generating {forecast_periods}-month forecast..."):
            forecaster = PollutionForecaster()
            
            pollutant_name = selected_pollutant.split('(')[0].strip()
            
            forecast_result = forecaster.forecast_arima(
                df,
                location=selected_location,
                pollutant=pollutant_name,
                periods=forecast_periods
            )
            
            if forecast_result:
                # Display forecast visualization
                st.subheader("📈 Forecast Results")
                
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=forecast_result['historical'].index,
                    y=forecast_result['historical'].values,
                    mode='lines',
                    name='Historical',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_result['forecast'].index,
                    y=forecast_result['forecast'].values,
                    mode='lines',
                    name='Forecast',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
                
                # Confidence interval
                fig.add_trace(go.Scatter(
                    x=forecast_result['forecast'].index,
                    y=forecast_result['upper_ci'].values,
                    mode='lines',
                    name='Upper CI (95%)',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=forecast_result['forecast'].index,
                    y=forecast_result['lower_ci'].values,
                    mode='lines',
                    name='Lower CI (95%)',
                    fill='tonexty',
                    fillcolor='rgba(255, 127, 14, 0.2)',
                    line=dict(width=0)
                ))
                
                fig.update_layout(
                    title=f"Forecast: {selected_pollutant} in {selected_location}",
                    xaxis_title="Date",
                    yaxis_title="Pollution Level",
                    template='plotly_white',
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Forecast statistics
                st.subheader("📊 Forecast Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Avg Forecast",
                        f"{forecast_result['forecast'].mean():.2f}"
                    )
                
                with col2:
                    last_historical = forecast_result['historical'].iloc[-1]
                    first_forecast = forecast_result['forecast'].iloc[0]
                    change = ((first_forecast - last_historical) / last_historical * 100)
                    st.metric(
                        "Immediate Change",
                        f"{change:.1f}%",
                        delta=f"{change:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Min Forecast",
                        f"{forecast_result['forecast'].min():.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Max Forecast",
                        f"{forecast_result['forecast'].max():.2f}"
                    )
                
                # Forecast table
                st.subheader("📋 Detailed Forecast Table")
                
                forecast_table = pd.DataFrame({
                    'Date': forecast_result['forecast'].index,
                    'Forecast': forecast_result['forecast'].values,
                    'Lower CI (95%)': forecast_result['lower_ci'].values,
                    'Upper CI (95%)': forecast_result['upper_ci'].values
                })
                
                st.dataframe(forecast_table, use_container_width=True)
                
                # Download forecast
                st.download_button(
                    "Download Forecast Data",
                    forecast_table.to_csv(index=False).encode('utf-8'),
                    f"forecast_{selected_location}_{pollutant_name}.csv",
                    "text/csv"
                )
                
                # Model summary
                with st.expander("📄 View Model Summary"):
                    st.text(str(forecast_result['model_summary']))
                
            else:
                st.warning("⚠️ Unable to generate forecast. Possible reasons:")
                st.write("- Insufficient data points (need at least 20 observations)")
                st.write("- Data too sparse or irregular")
                st.write("- Try a different location or pollutant")
    
    # Historical trends for context
    st.markdown("---")
    st.subheader("📉 Historical Context")
    
    # Filter for selected location and pollutant
    context_df = df[
        (df['geo_place_name'] == selected_location) &
        (df['name'].str.contains(selected_pollutant.split('(')[0].strip(), case=False, na=False))
    ].sort_values('start_date')
    
    if len(context_df) > 0:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Historical Mean", f"{context_df['data_value'].mean():.2f}")
        with col2:
            st.metric("Historical Max", f"{context_df['data_value'].max():.2f}")
        with col3:
            st.metric("Historical Min", f"{context_df['data_value'].min():.2f}")
        with col4:
            st.metric("Data Points", len(context_df))
        
        # Historical plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=context_df['start_date'],
            y=context_df['data_value'],
            mode='lines+markers',
            name='Historical',
            line=dict(color='#1f77b4')
        ))
        
        fig.update_layout(
            title=f"Historical Trend: {selected_pollutant} in {selected_location}",
            xaxis_title="Date",
            yaxis_title="Pollution Level",
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data available for the selected combination")

except FileNotFoundError:
    st.error("❌ Air_Quality.csv not found!")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.exception(e)
