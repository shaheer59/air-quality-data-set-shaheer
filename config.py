"""
Configuration file for Air Quality Analytics Platform
Contains constants, thresholds, and EPA standards
"""

# EPA AQI Breakpoints and Categories
AQI_CATEGORIES = {
    'Good': {'range': (0, 50), 'color': '#00E400'},
    'Moderate': {'range': (51, 100), 'color': '#FFFF00'},
    'Unhealthy for Sensitive Groups': {'range': (101, 150), 'color': '#FF7E00'},
    'Unhealthy': {'range': (151, 200), 'color': '#FF0000'},
    'Very Unhealthy': {'range': (201, 300), 'color': '#8F3F97'},
    'Hazardous': {'range': (301, 500), 'color': '#7E0023'}
}

# Pollutant Standards (EPA)
POLLUTANT_STANDARDS = {
    'NO2': {
        'unit': 'ppb',
        'annual_standard': 53,
        'hourly_standard': 100,
        'good_threshold': 25,
        'moderate_threshold': 50
    },
    'PM2.5': {
        'unit': 'mcg/m3',
        'annual_standard': 12,
        'daily_standard': 35,
        'good_threshold': 12,
        'moderate_threshold': 35.4
    },
    'O3': {
        'unit': 'ppb',
        'hourly_standard': 70,
        'good_threshold': 30,
        'moderate_threshold': 55
    }
}

# Outlier Detection Thresholds
OUTLIER_CONFIG = {
    'iqr_multiplier': 1.5,
    'z_score_threshold': 3,
    'rolling_window': 30
}

# Feature Engineering Parameters
FEATURE_CONFIG = {
    'rolling_windows': [7, 30],
    'temporal_aggregations': ['daily', 'weekly', 'monthly', 'yearly'],
    'volatility_window': 30, # Changed from 90
    
    # Advanced Analytics
    'contamination': 0.05,  # For anomaly detection
    'forecast_horizon': 30,  # Days
}

# --- UI/UX & Design Configuration ---

# Premium Dark Mode Palette
THEME_COLOR_PALETTE = {
    'background': '#0E1117',
    'card_background': '#1C1F26',
    'primary': '#00C6FF',      # Electric Blue
    'secondary': '#7F5AF0',    # Vibrant Purple
    'accent': '#00E676',       # Bright Green
    'text_primary': '#FFFFFF',
    'text_secondary': '#A0AEC0',
    'success': '#00E676',
    'warning': '#FFA500',      # Orange
    'danger': '#FF4C4C',       # Red
    'info': '#29B6F6',         # Light Blue
    'chart_colors': ['#00C6FF', '#7F5AF0', '#00E676', '#FFA500', '#FF4C4C', '#F06292', '#BA68C8']
}

# Map Configuration
MAP_CONFIG = {
    'initial_view_state': {
        'latitude': 40.7128,
        'longitude': -74.0060,
        'zoom': 10,
        'pitch': 45,
        'bearing': 0
    },
    'heatmap_radius': 20,
    'elevation_scale': 50
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'page_title': 'Air Quality Intelligence Platform', # Corrected typo: 'Air Quality Intelligence', Platform' -> 'Air Quality Intelligence Platform'
    'page_icon': '🌍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Color Schemes
COLOR_SCHEMES = {
    'pollutants': {
        'NO2': '#FF6B6B',
        'PM2.5': '#4ECDC4',
        'O3': '#45B7D1',
        'SO2': '#FFA07A',
        'CO': '#98D8C8'
    },
    'gradient': ['#00429d', '#4771b2', '#73a2c6', '#a5d5d8', '#ffffe0']
}

# Caching Settings
CACHE_TTL = 3600  # 1 hour in seconds

# Export Settings
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8',
    'date_format': '%Y-%m-%d',
    'float_format': '%.3f'
}

# Forecasting Parameters
FORECAST_CONFIG = {
    'forecast_periods': 12,
    'confidence_interval': 0.95,
    'seasonal_periods': 4
}

# Clustering Parameters
CLUSTERING_CONFIG = {
    'n_clusters': 5,
    'random_state': 42
}
