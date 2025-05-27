import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests
from io import StringIO

# --- Load the data from GitHub raw URL ---
CSV_URL = "https://raw.githubusercontent.com/PushpaRathna/ai-powered-wildfire-dashboard/main/California_Fire_Incidents.csv"

@st.cache_data
def load_data():
    response = requests.get(CSV_URL)
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text), parse_dates=['Started'])
        df.rename(columns={'Started': 'StartDate'}, inplace=True)
        df['StartDate'] = pd.to_datetime(df['StartDate'], errors='coerce')  # 🔧 FIX
        return df
    else:
        st.error("❌ Failed to load data from GitHub.")
        return pd.DataFrame()



df = load_data()

# --- Data preparation ---
if not df.empty:
    # Drop rows without coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Create severity level from AcresBurned
    def classify_severity(acres):
        if pd.isna(acres):
            return 'Unknown'
        elif acres < 100:
            return 'Low'
        elif acres < 1000:
            return 'Medium'
        else:
            return 'High'

    df['Severity'] = df['AcresBurned'].apply(classify_severity)

    # Extract month and day
    df['Month'] = df['StartDate'].dt.month
    df['Day'] = df['StartDate'].dt.day

    # --- Sidebar ---
    st.sidebar.title("🔥 Wildfire Dashboard Filters")
    selected_month = st.sidebar.selectbox("Select Month", sorted(df['Month'].dropna().unique()))

    filtered_df = df[df['Month'] == selected_month]

    # --- Main Interface ---
    st.title("🔥 California Wildfire Dashboard")
    st.markdown("An interactive AI-powered wildfire response dashboard based on historical data.")

    st.subheader(f"📅 Total fires in month {selected_month}: {filtered_df.shape[0]}")

    # --- Severity Chart ---
    st.subheader("🔥 Fire Severity Breakdown")
    severity_counts = filtered_df['Severity'].value_counts()
    st.bar_chart(severity_counts)

    # --- Map Visualization ---
    st.subheader("🗺️ Fire Location Map")

    wildfire_map = folium.Map(location=[37.0, -120.0], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(wildfire_map)

    # Marker color by severity
    def severity_color(severity):
        if severity == 'Low':
            return 'green'
        elif severity == 'Medium':
            return 'orange'
        elif severity == 'High':
            return 'red'
        else:
            return 'gray'

    for _, row in filtered_df.iterrows():
        popup_text = f"""
        🔥 <b>{row['Name']}</b><br>
        📍 County: {row['Counties']}<br>
        📆 Start: {row['StartDate'].date()}<br>
        🌡️ Severity: {row['Severity']}<br>
        🌲 Acres Burned: {row['AcresBurned']}
        """
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=severity_color(row['Severity']),
            fill=True,
            fill_color=severity_color(row['Severity']),
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(marker_cluster)

    st_data = st_folium(wildfire_map, width=700, height=500)

else:
    st.warning("No data to display. Check data source.")
