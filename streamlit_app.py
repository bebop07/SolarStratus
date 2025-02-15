import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='SolarStattus',
    page_icon=':sunny:',  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Generate realistic-looking data with variability.

@st.cache_data
def generate_solar_forecast_data():
    """Generate simulated solar power forecast data with variability."""
    
    np.random.seed(42)
    start_date = dt.date(2024, 1, 1)
    end_date = dt.date(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='H')

    # Create DataFrame for hourly forecasts
    hourly_data = []
    for single_date in date_range:
        for hour in range(24):
            # Add variability to peak hour
            peak_hour = np.random.randint(10, 16)  # Peak between 10 AM and 4 PM
            base_power = 250
            max_power = 400
            power = base_power + (max_power - base_power) * np.exp(-((hour - peak_hour) ** 2) / 2)
            hourly_data.append([
                single_date,
                hour,
                power,  # Model 1
                power * np.random.uniform(0.90, 1.10),  # Model 2 with wider variance
                power * np.random.uniform(0.90, 1.10)   # Model 3 with wider variance
            ])

    df = pd.DataFrame(hourly_data, columns=['Date', 'Hour', 'Model 1', 'Model 2', 'Model 3'])

    return df

solar_df = generate_solar_forecast_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.title(':sunny: SolarStattus Dashboard')
st.markdown("Explore solar power forecasts for your rooftop panels. Compare predictions from various models to optimize your solar energy usage.")

# Add some spacing
st.write('')

# Convert date columns to datetime objects for correct filtering
solar_df['Date'] = pd.to_datetime(solar_df['Date'])

min_date = solar_df['Date'].min().date()
max_date = solar_df['Date'].max().date()

# Weekly date range slider
week_start = st.date_input(
    'Select the start date for weekly forecast:',
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

week_end = week_start + pd.DateOffset(weeks=1)

# List of forecast models
forecast_models = [col for col in solar_df.columns if col not in ['Date', 'Hour']]

selected_models = st.multiselect(
    'Which forecast models would you like to view?',
    forecast_models,
    forecast_models
)

# Filter the data for weekly view
weekly_data = solar_df[
    (solar_df['Date'].dt.date >= week_start) &
    (solar_df['Date'].dt.date < week_end.date())
]

st.header('Weekly Solar Power Forecasts')

# Create line charts for daily predictions
for model in selected_models:
    st.subheader(f'{model} Daily Forecast')
    daily_forecast = weekly_data.groupby('Date').agg({model: 'mean'}).reset_index()
    daily_forecast['Date'] = pd.to_datetime(daily_forecast['Date'])
    
    # Normalize data with added variability
    daily_forecast[model] = np.clip(daily_forecast[model], 250, 400) * np.random.uniform(0.98, 1.02)
    
    # Plot with Streamlit
    st.line_chart(daily_forecast.set_index('Date')[model])

# Hourly forecasts
hourly_start = st.date_input(
    'Select the start date for hourly forecast:',
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

hourly_end = hourly_start + pd.DateOffset(days=1)

# Filter the data for hourly view
hourly_data = solar_df[
    (solar_df['Date'].dt.date >= hourly_start) &
    (solar_df['Date'].dt.date < hourly_end.date())
]

st.header('Hourly Solar Power Forecasts')

# Create line charts for hourly predictions
for model in selected_models:
    st.subheader(f'{model} Hourly Forecast')
    hourly_forecast = hourly_data[hourly_data['Date'].dt.date == hourly_start]
    
    if not hourly_forecast.empty:
        hourly_avg = hourly_forecast.groupby('Hour').agg({model: 'mean'}).reset_index()
        
        # Normalize data with added variability
        hourly_avg[model] = np.clip(hourly_avg[model], 250, 400) * np.random.uniform(0.98, 1.02)
        
        st.write(f'{model} Forecast for {hourly_start}')
        st.line_chart(hourly_avg.set_index('Hour')[model])
    else:
        st.write(f'No data available for {model} on {hourly_start}')

# Adding some styling and information
st.write('''
#### Tips:
- For daily forecasts, choose a week to see the trend over that period.
- For hourly forecasts, select a single day to view detailed hourly predictions.
''')

# Add some more styling
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stTitle {
        color: #ffb547;
        font-size: 2em;
    }
    .stHeader {
        color: #ff8c00;
    }
    .stMarkdown {
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)
