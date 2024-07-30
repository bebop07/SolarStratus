import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Solar Power Forecast Dashboard',
    page_icon=':sunny:',  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Generate some realistic-looking data.

@st.cache_data
def generate_solar_forecast_data():
    """Generate simulated solar power forecast data."""

    np.random.seed(42)
    start_date = dt.date(2024, 1, 1)
    end_date = dt.date(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='H')
    hours = list(range(24))

    # Create DataFrame for hourly forecasts
    hourly_data = []
    for single_date in date_range:
        for hour in hours:
            hourly_data.append([
                single_date,
                hour,
                np.random.uniform(0, 5),  # Model 1
                np.random.uniform(0, 5),  # Model 2
                np.random.uniform(0, 5)   # Model 3
            ])

    df = pd.DataFrame(hourly_data, columns=['Date', 'Hour', 'Model 1', 'Model 2', 'Model 3'])

    return df

solar_df = generate_solar_forecast_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.title(':sunny: Solar Power Forecast Dashboard')
st.markdown("Browse solar power forecasts for your rooftop solar panels. View both daily and hourly predictions from various models to optimize your solar energy usage.")

# Add some spacing
st.write('')

# Convert date columns to datetime objects for correct filtering
min_date = solar_df['Date'].min().date()
max_date = solar_df['Date'].max().date()

# Date range slider
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
    (solar_df['Date'].dt.date >= date_range[0]) &
    (solar_df['Date'].dt.date <= date_range[1])
]

st.header('Solar Power Forecasts', anchor='gray')

# Create line charts for daily predictions
for model in selected_models:
    st.subheader(f'{model} Daily Forecast')
    daily_forecast = filtered_solar_df.groupby('Date').agg({model: 'mean'}).reset_index()
    daily_forecast['Date'] = pd.to_datetime(daily_forecast['Date'])
    st.line_chart(daily_forecast, x='Date', y=model)

# Create line charts for hourly predictions
st.header('Hourly Forecasts', anchor='gray')
hourly_forecast = filtered_solar_df.groupby(['Date', 'Hour'])[selected_models].mean().reset_index()

for model in selected_models:
    st.subheader(f'{model} Hourly Forecast')
    for date in hourly_forecast['Date'].dt.date.unique():
        daily_hourly_data = hourly_forecast[hourly_forecast['Date'].dt.date == date]
        st.line_chart(daily_hourly_data, x='Hour', y=model, title=f'{model} Forecast for {date}')

