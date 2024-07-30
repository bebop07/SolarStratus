import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Solar Power Forecast Dashboard',
    page_icon=':sunny:',  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_solar_forecast_data():
    """Grab solar power forecast data from a CSV file.

    This uses caching to avoid having to read the file every time.
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent / 'data/solar_forecast_data.csv'
    raw_solar_df = pd.read_csv(DATA_FILENAME)

    MIN_DATE = '2024-01-01'
    MAX_DATE = '2024-12-31'

    # The data above might have columns like:
    # - Date
    # - Hour
    # - Forecast Model 1
    # - Forecast Model 2
    # - ...
    #
    # We might need to reshape or clean the data accordingly.
    # For simplicity, assuming it is already in the desired format.

    # Convert Date from string to datetime
    raw_solar_df['Date'] = pd.to_datetime(raw_solar_df['Date'])

    return raw_solar_df

solar_df = get_solar_forecast_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :sunny: Solar Power Forecast Dashboard

Browse solar power forecasts for your rooftop solar panels. View both daily and hourly predictions from various models to optimize your solar energy usage.
'''

# Add some spacing
''
''

min_date = solar_df['Date'].min()
max_date = solar_df['Date'].max()

date_range = st.slider(
    'Select the date range:',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    format='YYYY-MM-DD'
)

# List of forecast models
forecast_models = [col for col in solar_df.columns if col not in ['Date', 'Hour']]

selected_models = st.multiselect(
    'Which forecast models would you like to view?',
    forecast_models,
    forecast_models
)

# Filter the data
filtered_solar_df = solar_df[
    (solar_df['Date'] >= date_range[0]) &
    (solar_df['Date'] <= date_range[1])
]

st.header('Solar Power Forecasts', divider='gray')

# Create line charts for daily predictions
for model in selected_models:
    st.subheader(f'{model} Daily Forecast')
    daily_forecast = filtered_solar_df.groupby('Date')[model].mean().reset_index()
    st.line_chart(daily_forecast, x='Date', y=model)

# Create line charts for hourly predictions
st.header('Hourly Forecasts', divider='gray')
hourly_forecast = filtered_solar_df.groupby(['Date', 'Hour'])[selected_models].mean().reset_index()

for model in selected_models:
    st.subheader(f'{model} Hourly Forecast')
    for date in hourly_forecast['Date'].unique():
        daily_hourly_data = hourly_forecast[hourly_forecast['Date'] == date]
        st.line_chart(daily_hourly_data, x='Hour', y=model, title=f'{model} Forecast for {date.date()}')

