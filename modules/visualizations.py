"""
Advanced Visualization Factory
Standard and advanced interactive visualizations using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import pydeck as pdk
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class VisualizationFactory:
    """Create standard and advanced visualizations"""
    
    def __init__(self, color_scheme: Dict = None):
        self.color_scheme = color_scheme or {
            'NO2': '#FF6B6B',
            'PM2.5': '#4ECDC4',
            'O3': '#45B7D1'
        }
    
    # ==================== STANDARD VISUALIZATIONS ====================
    
    def time_series_line(self, df: pd.DataFrame, x_col: str = 'start_date',
                        y_col: str = 'data_value', color_col: str = 'name',
                        title: str = 'Air Quality Trends Over Time') -> go.Figure:
        """Interactive time-series line chart"""
        
        fig = px.line(df, x=x_col, y=y_col, color=color_col,
                     title=title,
                     labels={y_col: 'Pollutant Level', x_col: 'Date'},
                     color_discrete_map=self.color_scheme)
        
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        
        return fig
    
    def pollutant_comparison_bar(self, df: pd.DataFrame, agg_func: str = 'mean',
                                title: str = 'Pollutant Comparison') -> go.Figure:
        """Bar chart comparing pollutants"""
        
        agg_data = df.groupby('name')['data_value'].agg(agg_func).reset_index()
        agg_data = agg_data.sort_values('data_value', ascending=False)
        
        fig = px.bar(agg_data, x='name', y='data_value',
                    title=f'{title} ({agg_func.capitalize()})',
                    labels={'data_value': f'{agg_func.capitalize()} Value', 'name': 'Pollutant'},
                    color='name',
                    color_discrete_map=self.color_scheme)
        
        fig.update_layout(
            showlegend=False,
            template='plotly_white',
            height=450
        )
        
        return fig
    
    def distribution_box_plot(self, df: pd.DataFrame, y_col: str = 'data_value',
                             color_col: str = 'name',
                             title: str = 'Pollutant Distribution') -> go.Figure:
        """Box plot showing distribution"""
        
        fig = px.box(df, y=y_col, x=color_col, color=color_col,
                    title=title,
                    labels={y_col: 'Pollutant Level', color_col: 'Pollutant'},
                    color_discrete_map=self.color_scheme)
        
        fig.update_layout(
            showlegend=False,
            template='plotly_white',
            height=450
        )
        
        return fig
    
    def histogram_distribution(self, df: pd.DataFrame, value_col: str = 'data_value',
                              facet_col: str = 'name',
                              title: str = 'Pollutant Distribution') -> go.Figure:
        """Histogram with KDE overlay"""
        
        fig = px.histogram(df, x=value_col, color=facet_col,
                          marginal='box',
                          title=title,
                          labels={value_col: 'Pollutant Level'},
                          color_discrete_map=self.color_scheme,
                          opacity=0.7)
        
        fig.update_layout(
            barmode='overlay',
            template='plotly_white',
            height=450
        )
        
        return fig
    
    def correlation_heatmap(self, corr_matrix: pd.DataFrame,
                           title: str = 'Feature Correlation Matrix') -> go.Figure:
        """Interactive correlation heatmap"""
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu_r',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=600,
            width=800
        )
        
        return fig
    
    # ==================== ADVANCED VISUALIZATIONS ====================
    
    def animated_time_series(self, df: pd.DataFrame,
                            value_col: str = 'data_value',
                            animation_frame: str = 'year',
                            title: str = 'Animated Pollution Evolution') -> go.Figure:
        """Animated time-series"""
        
        if animation_frame not in df.columns:
            return self.time_series_line(df, title=title)
        
        fig = px.scatter(df, x='geo_place_name', y=value_col,
                        animation_frame=animation_frame,
                        animation_group='geo_place_name',
                        color='name',
                        size=value_col,
                        hover_name='geo_place_name',
                        title=title,
                        range_y=[0, df[value_col].max() * 1.1],
                        color_discrete_map=self.color_scheme)
        
        fig.update_layout(
            template='plotly_white',
            height=600,
            xaxis={'categoryorder': 'total descending'}
        )
        
        return fig
    
    def seasonal_decomposition_plot(self, decomposition: Dict,
                                   title: str = 'Time Series Decomposition') -> go.Figure:
        """Multi-panel seasonal decomposition plot"""
        
        if not decomposition:
            return go.Figure()
        
        fig = make_subplots(rows=4, cols=1,
                           subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'),
                           vertical_spacing=0.08)
        
        # Observed
        fig.add_trace(go.Scatter(x=decomposition['observed'].index,
                                y=decomposition['observed'].values,
                                mode='lines', name='Observed',
                                line=dict(color='#1f77b4')),
                     row=1, col=1)
        
        # Trend
        fig.add_trace(go.Scatter(x=decomposition['trend'].index,
                                y=decomposition['trend'].values,
                                mode='lines', name='Trend',
                                line=dict(color='#ff7f0e')),
                     row=2, col=1)
        
        # Seasonal
        fig.add_trace(go.Scatter(x=decomposition['seasonal'].index,
                                y=decomposition['seasonal'].values,
                                mode='lines', name='Seasonal',
                                line=dict(color='#2ca02c')),
                     row=3, col=1)
        
        # Residual
        fig.add_trace(go.Scatter(x=decomposition['residual'].index,
                                y=decomposition['residual'].values,
                                mode='lines', name='Residual',
                                line=dict(color='#d62728')),
                     row=4, col=1)
        
        fig.update_layout(
            title_text=title,
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def radar_chart(self, df: pd.DataFrame, locations: List[str],
                   pollutants: List[str],
                   title: str = 'Regional Pollution Profile') -> go.Figure:
        """Radar chart for multi-pollutant comparison"""
        
        fig = go.Figure()
        
        for location in locations[:5]:  # Limit to 5 locations
            values = []
            for pollutant in pollutants:
                subset = df[(df['geo_place_name'] == location) & 
                           (df['name'].str.contains(pollutant, case=False, na=False))]
                avg_val = subset['data_value'].mean() if len(subset) > 0 else 0
                values.append(avg_val)
            
            # Close the polygon
            values += values[:1]
            pollutants_closed = pollutants + [pollutants[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=pollutants_closed,
                fill='toself',
                name=location[:30]  # Truncate long names
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(values) * 1.1])),
            title=title,
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def scatter_matrix(self, df: pd.DataFrame, dimensions: List[str],
                      color_col: str = 'name',
                      title: str = 'Feature Scatter Matrix') -> go.Figure:
        """Scatter plot matrix (SPLOM)"""
        
        # Limit dimensions to avoid overcrowding
        dimensions = dimensions[:5]
        
        fig = px.scatter_matrix(df, dimensions=dimensions,
                               color=color_col,
                               title=title,
                               color_discrete_map=self.color_scheme,
                               opacity=0.6)
        
        fig.update_layout(
            height=800,
            width=1000,
            template='plotly_white'
        )
        
        return fig
    
    def anomaly_highlighted_series(self, df: pd.DataFrame,
                                   x_col: str = 'start_date',
                                   y_col: str = 'data_value',
                                   anomaly_col: str = 'is_anomaly',
                                   title: str = 'Pollution with Anomalies Highlighted') -> go.Figure:
        """Time series with anomalies highlighted"""
        
        fig = go.Figure()
        
        # Normal data
        normal_data = df[df[anomaly_col] == 0]
        fig.add_trace(go.Scatter(
            x=normal_data[x_col],
            y=normal_data[y_col],
            mode='lines',
            name='Normal',
            line=dict(color='#1f77b4')
        ))
        
        # Anomalies
        anomaly_data = df[df[anomaly_col] == 1]
        if len(anomaly_data) > 0:
            fig.add_trace(go.Scatter(
                x=anomaly_data[x_col],
                y=anomaly_data[y_col],
                mode='markers',
                name='Anomaly',
                marker=dict(size=10, color='red', symbol='x')
            ))
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def rolling_volatility_chart(self, df: pd.DataFrame,
                                 value_col: str = 'data_value',
                                 rolling_col: str = 'rolling_avg_30d',
                                 std_col: str = 'rolling_std_30d',
                                 title: str = 'Rolling Volatility (Bollinger Bands)') -> go.Figure:
        """Bollinger Bands style volatility visualization"""
        
        fig = go.Figure()
        
        # Sort by date
        df_sorted = df.sort_values('start_date')
        
        # Upper band
        fig.add_trace(go.Scatter(
            x=df_sorted['start_date'],
            y=df_sorted[rolling_col] + 2 * df_sorted[std_col],
            mode='lines',
            name='Upper Band',
            line=dict(width=0),
            showlegend=False
        ))
        
        # Lower band
        fig.add_trace(go.Scatter(
            x=df_sorted['start_date'],
            y=df_sorted[rolling_col] - 2 * df_sorted[std_col],
            mode='lines',
            name='Lower Band',
            fill='tonexty',
            fillcolor='rgba(68, 68, 68, 0.2)',
            line=dict(width=0)
        ))
        
        # Rolling average
        fig.add_trace(go.Scatter(
            x=df_sorted['start_date'],
            y=df_sorted[rolling_col],
            mode='lines',
            name='30-Day Average',
            line=dict(color='#ff7f0e', width=2)
        ))
        
        # Actual values
        fig.add_trace(go.Scatter(
            x=df_sorted['start_date'],
            y=df_sorted[value_col],
            mode='markers',
            name='Actual',
            marker=dict(size=4, color='#1f77b4', opacity=0.5)
        ))
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def geographic_treemap(self, df: pd.DataFrame,
                          title: str = 'Geographic Pollution Hierarchy') -> go.Figure:
        """Treemap visualization of geographic hierarchy"""
        
        # Aggregate by geography
        geo_agg = df.groupby(['geo_type_name', 'geo_place_name', 'name'])['data_value'].mean().reset_index()
        
        fig = px.treemap(geo_agg,
                        path=['geo_type_name', 'geo_place_name', 'name'],
                        values='data_value',
                        title=title,
                        color='data_value',
                        color_continuous_scale='RdYlGn_r')
        
        fig.update_layout(
            template='plotly_white',
            height=600
        )
        
        return fig


    
    def create_advanced_map(self, df: pd.DataFrame, 
                           lat_col: str = 'latitude', 
                           lon_col: str = 'longitude',
                           value_col: str = 'data_value',
                           map_type: str = 'scatter') -> pdk.Deck:
        """Create advanced 3D maps using PyDeck"""
        
        # Check if coordinates exist
        if lat_col not in df.columns or lon_col not in df.columns:
            return None
            
        # Define view state
        if df[lat_col].isnull().all() or df[lon_col].isnull().all():
             return None
             
        view_state = pdk.ViewState(
            latitude=df[lat_col].mean(),
            longitude=df[lon_col].mean(),
            zoom=10,
            pitch=45,
            bearing=0
        )
        
        layers = []
        
        if map_type == 'scatter':
            layer = pdk.Layer(
                "ScatterplotLayer",
                df,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=10,
                radius_min_pixels=3,
                radius_max_pixels=30,
                line_width_min_pixels=1,
                get_position=[lon_col, lat_col],
                get_radius=value_col,
                get_fill_color=[255, 140, 0, 200], # Orange default
                get_line_color=[0, 0, 0],
            )
            layers.append(layer)
            
        elif map_type == 'heatmap':
            layer = pdk.Layer(
                "HeatmapLayer",
                df,
                pickable=False,
                opacity=0.9,
                get_position=[lon_col, lat_col],
                get_weight=value_col,
                radius_pixels=40,
            )
            layers.append(layer)
            
        elif map_type == 'hexagon':
            layer = pdk.Layer(
                "HexagonLayer",
                df,
                pickable=True,
                extruded=True,
                radius=300,
                elevation_scale=10,
                elevation_range=[0, 3000],
                get_position=[lon_col, lat_col],
                get_elevation_weight=value_col,
                auto_highlight=True,
            )
            layers.append(layer)
            
        # Tooltip
        tooltip = {
            "html": "<b>Location:</b> {geo_place_name}<br/>"
                    "<b>Value:</b> {" + value_col + "}"
        }
        
        return pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style='mapbox://styles/mapbox/dark-v10'
        )


# Convenience function
def create_visualization(df: pd.DataFrame, viz_type: str, **kwargs) -> go.Figure:
    """Quick create any visualization type"""
    factory = VisualizationFactory()
    
    viz_methods = {
        'time_series': factory.time_series_line,
        'bar': factory.pollutant_comparison_bar,
        'box': factory.distribution_box_plot,
        'histogram': factory.histogram_distribution,
        'heatmap': factory.correlation_heatmap,
        'animated': factory.animated_time_series,
        'radar': factory.radar_chart,
        'scatter_matrix': factory.scatter_matrix,
        'anomaly': factory.anomaly_highlighted_series,
        'volatility': factory.rolling_volatility_chart,
        'treemap': factory.geographic_treemap,
        'map': factory.create_advanced_map
    }
    
    return viz_methods.get(viz_type, factory.time_series_line)(df, **kwargs)


if __name__ == "__main__":
    print("Visualization module ready!")
    print("Available visualizations:")
    print("  - Standard: time_series, bar, box, histogram, heatmap")
    print("  - Advanced: animated, radar, scatter_matrix, anomaly, volatility, treemap")
