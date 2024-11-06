import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

day_df = pd.read_csv("dashboard/df_day.csv")

day_df['dteday'] = pd.to_datetime(day_df['dteday'])

st.set_page_config(page_title="Bike Rental Analysis",
                   layout="wide")

def month_users_df(day_df):
    month_df = day_df.resample(rule='M', on='dteday').agg({
        "cnt": "sum"  
    })

    month_df.index = month_df.index.strftime('%b-%y')
    month_df = month_df.reset_index()
    month_df.rename(columns={
        "dteday": "yearmonth",
        "cnt": "total_users" 
    }, inplace=True)
    
    return month_df                   

def weekday_users_df(day_df):
    weekday_df = day_df.groupby("weekday").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    weekday_df = weekday_df.reset_index()
    weekday_df.rename(columns={
        "cnt": "total_users",
        "casual": "casual_users",
        "registered": "registered_users"
    }, inplace=True)
    
    weekday_df = pd.melt(weekday_df,
                         id_vars=['weekday'],
                         value_vars=['casual_users', 'registered_users'],
                         var_name='User Status',
                         value_name='count_users')
    
    weekday_df['weekday'] = pd.Categorical(weekday_df['weekday'],
                                           categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    weekday_df = weekday_df.sort_values('weekday')
    
    return weekday_df

def season_users_df(day_df):
    season_df = day_df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    season_df = season_df.reset_index()
    season_df.rename(columns={
        "cnt": "total_users",
        "casual": "casual_users",
        "registered": "registered_users"
    }, inplace=True)
    
    season_df = pd.melt(season_df,
                        id_vars=['season'],
                        value_vars=['casual_users', 'registered_users'],
                        var_name='User Status',
                        value_name='count_users')
    
    season_df['season'] = pd.Categorical(season_df['season'],
                          categories=['Spring', 'Summer', 'Fall', 'Winter'])
    
    season_df = season_df.sort_values('season')
    
    return season_df


min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()    

with st.sidebar:
    st.image("bike.jpg", width=275)

    st.sidebar.header("Filter:")

    start_date, end_date = st.date_input(
        label="Date Filter", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[
    (day_df["dteday"] >= str(start_date)) &
    (day_df["dteday"] <= str(end_date))
]

month_df = month_users_df(main_df)
weekday_df = weekday_users_df(main_df)
season_df = season_users_df(main_df)

st.title(":chart_with_upwards_trend: Bike Rental Analysis")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    all_rides = main_df['cnt'].sum()
    st.metric("Total All Users :", value=all_rides)
with col2:
    casual_rides = main_df['casual'].sum()
    st.metric("Total Casual Users :", value=casual_rides)
with col3:
    registered_rides = main_df['registered'].sum()
    st.metric("Total Registered Users :", value=registered_rides)

st.markdown("---")

fig = px.line(month_df,
    x='yearmonth',
    y=['total_users'],
    color_discrete_sequence=["red"],
    markers=True,
    title="Recap of Bike Rentals by Month (All Users)").update_layout(xaxis_title='Month-Year', yaxis_title='Total users',yaxis_tickformat='d',showlegend=False)

fig1 = px.bar(
    weekday_df,
    x='weekday',
    y='count_users',
    color='User Status',
    barmode='group',
    color_discrete_sequence=["lightgray", "salmon"],
    title='Recap of Bike Rentals by Weekday'
).update_layout(xaxis_title='Day', yaxis_title='Total users',yaxis_tickformat='d')

fig2 = px.bar(
    season_df,
    x='season',
    y='count_users',
    color='User Status',
    color_discrete_sequence=["lightgray", "salmon"],
    title='Recap of Bike Rentals by Season'
).update_layout(xaxis_title='Season', yaxis_title='Total users',yaxis_tickformat='d')


st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.caption('Created by Irka Tri Agustin')
