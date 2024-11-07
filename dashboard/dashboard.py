import pandas as pd
import plotly.express as px
import streamlit as st
import os

# Set up Streamlit page configuration
st.set_page_config(page_title="Bike Rental Analysis", layout="wide")

# Define paths for file access
if os.getenv("STREAMLIT_CLOUD"):
    file_path = "dashboard/df_day.csv"
    image_path = "dashboard/bike.jpg"
else:
    file_path = "df_day.csv"
    image_path = "bike.jpg"

# Load data
try:
    day_df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error("CSV file not found. Please check the path and try again.")
    st.stop()

day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Define data processing functions
def month_users_df(day_df):
    month_df = day_df.resample(rule='M', on='dteday').agg({"cnt": "sum"})
    month_df.index = month_df.index.strftime('%b-%y')
    month_df = month_df.reset_index()
    month_df.rename(columns={"dteday": "yearmonth", "cnt": "total_users"}, inplace=True)
    return month_df                   

def weekday_users_df(day_df):
    weekday_df = day_df.groupby("weekday").agg({"casual": "sum", "registered": "sum", "cnt": "sum"})
    weekday_df = weekday_df.reset_index()
    weekday_df.rename(columns={"cnt": "total_users", "casual": "casual_users", "registered": "registered_users"}, inplace=True)
    weekday_df = pd.melt(weekday_df, id_vars=['weekday'], value_vars=['casual_users', 'registered_users'], var_name='User Status', value_name='count_users')
    weekday_df['weekday'] = pd.Categorical(weekday_df['weekday'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    weekday_df = weekday_df.sort_values('weekday')
    return weekday_df

def season_users_df(day_df):
    season_df = day_df.groupby("season").agg({"casual": "sum", "registered": "sum", "cnt": "sum"})
    season_df = season_df.reset_index()
    season_df.rename(columns={"cnt": "total_users", "casual": "casual_users", "registered": "registered_users"}, inplace=True)
    season_df = pd.melt(season_df, id_vars=['season'], value_vars=['casual_users', 'registered_users'], var_name='User Status', value_name='count_users')
    season_df['season'] = pd.Categorical(season_df['season'], categories=['Spring', 'Summer', 'Fall', 'Winter'])
    season_df = season_df.sort_values('season')
    return season_df

# Sidebar date filter
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image(image_path, width=275)
    st.sidebar.header("Filter:")
    
    date_selection = st.date_input(
    label="Date Filter",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date = date_selection[0] if isinstance(date_selection, (list, tuple)) else date_selection
    end_date = max_date

# Pastikan kedua nilai adalah tipe datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data berdasarkan start_date dan end_date
main_df = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]

# Data processing
month_df = month_users_df(main_df)
weekday_df = weekday_users_df(main_df)
season_df = season_users_df(main_df)

# Display metrics and plots
st.title(":chart_with_upwards_trend: Bike Rental Analysis")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("Total All Users:", value=main_df['cnt'].sum())
col2.metric("Total Casual Users:", value=main_df['casual'].sum())
col3.metric("Total Registered Users:", value=main_df['registered'].sum())
st.markdown("---")

# Create plots
fig = px.line(month_df, x='yearmonth', y='total_users', color_discrete_sequence=["red"], markers=True, title="Recap of Bike Rentals by Month (All Users)")
fig.update_layout(xaxis_title='Month-Year', yaxis_title='Total users', yaxis_tickformat='d', showlegend=False)
st.plotly_chart(fig, use_container_width=True)

fig1 = px.bar(weekday_df, x='weekday', y='count_users', color='User Status', barmode='group', color_discrete_sequence=["lightgray", "salmon"], title='Recap of Bike Rentals by Weekday')
fig1.update_layout(xaxis_title='Day', yaxis_title='Total users', yaxis_tickformat='d')
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(season_df, x='season', y='count_users', color='User Status', color_discrete_sequence=["lightgray", "salmon"], title='Recap of Bike Rentals by Season')
fig2.update_layout(xaxis_title='Season', yaxis_title='Total users', yaxis_tickformat='d')
st.plotly_chart(fig2, use_container_width=True)

st.caption('Created by Irka Tri Agustin')
