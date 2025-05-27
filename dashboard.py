import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# Load your cleaned dataset
df = pd.read_csv("California_Fire_Incidents.csv", parse_dates=['StartDate'])

# Sidebar filter
st.sidebar.title("Wildfire Dashboard")
month = st.sidebar.selectbox("Select Month", sorted(df['StartDate'].dt.month.unique()))

filtered_df = df[df['StartDate'].dt.month == month]

# Title
st.title("🔥 California Wildfire Dashboard")
st.write(f"Total fires in month {month}: {filtered_df.shape[0]}")

# Bar chart of fire severity
if 'Severity' in df.columns:
    st.subheader("Fire Severity Breakdown")
    st.bar_chart(filtered_df['Severity'].value_counts())

# Map
st.subheader("Wildfire Map")

m = folium.Map(location=[37.0, -120.0], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    popup_text = f"Name: {row['Name']}<br>Acres: {row['AcresBurned']}"
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=4,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.7,
        popup=popup_text
    ).add_to(marker_cluster)

st_data = st_folium(m, width=700, height=500)
