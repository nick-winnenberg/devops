import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import numpy as np
from scipy import stats
import plotly.graph_objects as go

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(page_title="NOAA Climate Data Explorer", layout="wide")

st.title("NOAA Climate Data Explorer")
st.markdown("""
Welcome to the NOAA Climate Data Explorer. This application provides comprehensive visualization 
and analysis of historical climate data from the National Oceanic and Atmospheric Administration (NOAA). 
Explore global temperature trends and greenhouse gas emissions data.
""")

API_TOKEN = "nXqknZjknkBdOOmxuuVDSQyZbxeTnMIN"
BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
headers = {"token": API_TOKEN}

today = datetime.today().date()
this_year = today.year

# ========================================
# DATA FETCHING FUNCTIONS
# ========================================

@st.cache_data(ttl=3600)
def fetch_global_temperature_data():
    """
    Fetch global temperature anomaly data from NOAA/NCEI
    This uses the actual global land and ocean temperature anomalies
    """
    try:
        # NOAA Global Temperature Anomalies (published dataset)
        url = "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series/globe/land_ocean/1/0/1850-2024.csv"
        
        # Read CSV, skip first 4 header rows
        df = pd.read_csv(url, skiprows=4)
        df.columns = ['Date', 'Anomaly']
        
        # Extract year from YYYYMM format
        df['year'] = df['Date'].astype(str).str[:4].astype(int)
        
        # Calculate annual average from monthly anomalies
        df_annual = df.groupby('year')['Anomaly'].mean().reset_index()
        
        # Convert anomaly to actual temperature (baseline is ~13.9°C for 20th century average)
        baseline_temp = 13.9
        df_annual['Average Temperature (°C)'] = baseline_temp + df_annual['Anomaly']
        df_annual = df_annual.rename(columns={'year': 'Year'})
        
        return df_annual[['Year', 'Average Temperature (°C)']]
    except Exception as e:
        st.error(f"Error fetching NOAA global temperature data: {e}")
        # Fallback to NASA GISS data
        try:
            url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
            df = pd.read_csv(url, skiprows=1)
            df = df[['Year', 'J-D']]  # J-D is January-December average
            df.columns = ['Year', 'Anomaly']
            df = df[df['Year'] != 'Year'].dropna()
            df['Year'] = df['Year'].astype(int)
            df['Anomaly'] = pd.to_numeric(df['Anomaly'], errors='coerce')
            
            # Convert anomaly to actual temperature (NASA baseline is 14.0°C)
            baseline_temp = 14.0
            df['Average Temperature (°C)'] = baseline_temp + df['Anomaly']
            
            return df[['Year', 'Average Temperature (°C)']]
        except Exception as e2:
            st.error(f"Error fetching NASA GISS data: {e2}")
            return None

@st.cache_data(ttl=3600)
def fetch_carbon_emissions():
    """Fetch global CO2 emissions data from Our World in Data"""
    try:
        url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
        df_co2 = pd.read_csv(url)
        
        df_world = df_co2[df_co2['country'] == 'World'].copy()
        df_world = df_world[['year', 'co2', 'co2_per_capita']].dropna()
        
        return df_world
    except Exception as e:
        st.error(f"Error fetching carbon emissions data: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_methane_emissions():
    """Fetch global methane emissions data from Our World in Data"""
    try:
        url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
        df_methane = pd.read_csv(url)
        
        df_world = df_methane[df_methane['country'] == 'World'].copy()
        df_world = df_world[['year', 'methane', 'methane_per_capita']].dropna()
        
        return df_world
    except Exception as e:
        st.error(f"Error fetching methane emissions data: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_nitrous_oxide_emissions():
    """Fetch global nitrous oxide emissions data from Our World in Data"""
    try:
        url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
        df_n2o = pd.read_csv(url)
        
        df_world = df_n2o[df_n2o['country'] == 'World'].copy()
        df_world = df_world[['year', 'nitrous_oxide', 'nitrous_oxide_per_capita']].dropna()
        
        return df_world
    except Exception as e:
        st.error(f"Error fetching nitrous oxide emissions data: {e}")
        return None

@st.cache_data(ttl=3600)
def create_combined_dataframe(df_global_annual, df_emissions, df_methane, df_n2o):
    """Combine temperature and emissions data into a single DataFrame"""
    try:
        df_combined = df_global_annual.copy()
        df_combined = df_combined.rename(columns={'Year': 'year', 'Average Temperature (°C)': 'avg_temp_c'})
        
        if df_emissions is not None and not df_emissions.empty:
            df_combined = df_combined.merge(
                df_emissions[['year', 'co2']], 
                on='year', 
                how='left'
            )
        
        if df_methane is not None and not df_methane.empty:
            df_combined = df_combined.merge(
                df_methane[['year', 'methane']], 
                on='year', 
                how='left'
            )
        
        if df_n2o is not None and not df_n2o.empty:
            df_combined = df_combined.merge(
                df_n2o[['year', 'nitrous_oxide']], 
                on='year', 
                how='left'
            )
        
        df_combined = df_combined.fillna(method='ffill')
        
        return df_combined
    except Exception as e:
        st.error(f"Error creating combined dataframe: {e}")
        return None

# ========================================
# LOAD ALL DATA
# ========================================

with st.spinner("Loading global climate and emissions data..."):
    df_global_annual = fetch_global_temperature_data()
    df_emissions = fetch_carbon_emissions()
    df_methane = fetch_methane_emissions()
    df_n2o = fetch_nitrous_oxide_emissions()

# ========================================
# COMBINED DATA ANALYSIS (TOP SECTION)
# ========================================
st.header("Combined Climate and Emissions Analysis")
st.divider()

if df_global_annual is not None and not df_global_annual.empty:
    df_combined = create_combined_dataframe(df_global_annual, df_emissions, df_methane, df_n2o)
    
    if df_combined is not None:
        st.info(f"Combined dataset: {len(df_combined)} years of integrated climate and emissions data")
        
        df_combined["Total Emissions (Mt)"] = df_combined[["co2", "methane", "nitrous_oxide"]].sum(axis=1, skipna=True)
        
        st.subheader("Total Emissions and Temperature Over Time")
        
        emissions_and_temp_fig = go.Figure()
        emissions_and_temp_fig.add_trace(
            go.Bar(
                x=df_combined['year'], 
                y=df_combined['Total Emissions (Mt)'],
                name='Total Emissions (Mt)',
                marker=dict(color='steelblue'),
                yaxis='y1'
            )
        )
        
        emissions_and_temp_fig.add_trace(
            go.Scatter(
                x=df_combined['year'], 
                y=df_combined['avg_temp_c'],
                mode='lines+markers',
                name='Temperature (°C)',
                line=dict(color='red', width=2),
                yaxis='y2'
            )
        )
        
        emissions_and_temp_fig.update_layout(
            title='Total Greenhouse Gas Emissions and Global Temperature',
            xaxis=dict(title='Year'),
            yaxis=dict(title='Total Emissions (Mt)', side='left'),
            yaxis2=dict(title='Temperature (°C)', overlaying='y', side='right'),
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(emissions_and_temp_fig, use_container_width=True)
        st.caption("Temperature Source: NOAA/NCEI Global Temperature Anomalies")
        st.caption("Emission Source: Our World in Data (CO2 and Greenhouse Gas Emissions Database)")        
        st.subheader("Correlation Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            co2_corr = df_combined['co2'].corr(df_combined['avg_temp_c'])
            st.metric(label="CO2 vs Temperature Correlation", value=f"{co2_corr:.3f}")
        with col2:
            methane_corr = df_combined['methane'].corr(df_combined['avg_temp_c'])
            st.metric(label="CH4 vs Temperature Correlation", value=f"{methane_corr:.3f}")
        with col3:
            n2o_corr = df_combined['nitrous_oxide'].corr(df_combined['avg_temp_c'])
            st.metric(label="N2O vs Temperature Correlation", value=f"{n2o_corr:.3f}")

        st.subheader("Statistical Significance Tests")
        st.write("Testing whether the correlations between greenhouse gas emissions and temperature are statistically significant:")


        col1, col2, col3 = st.columns(3)

        with col1:
            # Remove NaN values for CO2 correlation test
            mask_co2 = df_combined[['co2', 'avg_temp_c']].notna().all(axis=1)
            if mask_co2.sum() > 2:
                r_co2, p_co2 = stats.pearsonr(
                    df_combined.loc[mask_co2, 'co2'], 
                    df_combined.loc[mask_co2, 'avg_temp_c']
                )
                st.metric("CO2 p-value", f"{p_co2:.4f}")
                if p_co2 < 0.05:
                    st.success("✓ Significant (p < 0.05)")
                else:
                    st.warning("Not significant")

        with col2:
            # Remove NaN values for methane correlation test
            mask_ch4 = df_combined[['methane', 'avg_temp_c']].notna().all(axis=1)
            if mask_ch4.sum() > 2:
                r_ch4, p_ch4 = stats.pearsonr(
                    df_combined.loc[mask_ch4, 'methane'], 
                    df_combined.loc[mask_ch4, 'avg_temp_c']
                )
                st.metric("CH4 p-value", f"{p_ch4:.4f}")
                if p_ch4 < 0.05:
                    st.success("✓ Significant (p < 0.05)")
                else:
                    st.warning("Not significant")

        with col3:
            # Remove NaN values for N2O correlation test
            mask_n2o = df_combined[['nitrous_oxide', 'avg_temp_c']].notna().all(axis=1)
            if mask_n2o.sum() > 2:
                r_n2o, p_n2o = stats.pearsonr(
                    df_combined.loc[mask_n2o, 'nitrous_oxide'], 
                    df_combined.loc[mask_n2o, 'avg_temp_c']
                )
                st.metric("N2O p-value", f"{p_n2o:.4f}")
                if p_n2o < 0.05:
                    st.success("✓ Significant (p < 0.05)")
                else:
                    st.warning("Not significant")

        st.caption("P-values < 0.05 indicate statistically significant correlations at the 95% confidence level")
        
        st.subheader("Combined Dataset Preview")
        st.dataframe(df_combined.tail(10), use_container_width=True)
        
        csv = df_combined.to_csv(index=False)
        st.download_button(
            label="Download Combined Data as CSV",
            data=csv,
            file_name="combined_climate_emissions_data.csv",
            mime="text/csv"
        )
        
        with st.expander("About Correlation Analysis"):
            st.write("""
            Correlation coefficients range from -1 to 1, where:
            - Values close to 1 indicate a strong positive relationship
            - Values close to -1 indicate a strong negative relationship
            - Values close to 0 indicate little to no linear relationship
            
            These metrics help quantify the relationship between greenhouse gas emissions 
            and global temperature changes.
            """)
    else:
        st.error("Unable to create combined dataset.")
else:
    st.warning("Global temperature data not available for combined analysis.")

# ========================================
# GLOBAL TEMPERATURE SECTION
# ========================================
st.divider()
st.header("Global Temperature Trends")
st.divider()

if df_global_annual is not None and not df_global_annual.empty:
    
    st.info(f"Dataset: {len(df_global_annual)} years ({df_global_annual['Year'].min()} - {df_global_annual['Year'].max()})")
    
    # Calculate linear regression for global data
    years_numeric = df_global_annual['Year'] - df_global_annual['Year'].min()
    z_global = np.polyfit(years_numeric, df_global_annual['Average Temperature (°C)'], 1)
    global_temp_change_per_year = z_global[0]
    total_years = df_global_annual['Year'].max() - df_global_annual['Year'].min()
    global_temp_change = global_temp_change_per_year * total_years
    global_temp_change_in_fahrenheit = global_temp_change * 9/5

    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=f"Temperature Change Over {total_years} Years (Celsius)", 
            value=f"{global_temp_change:.2f} °C"
        )
    with col2:
        st.metric(
            label=f"Temperature Change Over {total_years} Years (Fahrenheit)", 
            value=f"{global_temp_change_in_fahrenheit:.2f} °F"
        )
    with col3:
        st.metric(
            label="Rate of Change Per Decade", 
            value=f"{global_temp_change_per_year * 10:.3f} °C"
        )
    
    # Create interactive chart with trendline for global data
    st.subheader("Temperature Visualization")
    p_global = np.poly1d(z_global)
    df_global_annual['trendline'] = p_global(years_numeric)
    
    fig_global = go.Figure()
    fig_global.add_trace(
        go.Bar(
            x=df_global_annual['Year'], 
            y=df_global_annual['Average Temperature (°C)'], 
            name='Annual Average',
            marker=dict(color='steelblue')
        )
    )
    fig_global.add_trace(
        go.Scatter(
            x=df_global_annual['Year'], 
            y=df_global_annual['trendline'], 
            mode='lines', 
            name='Trendline', 
            line=dict(dash='dash', color='red', width=2)
        )
    )
    fig_global.update_layout(
        title='Global Annual Average Temperature',
        xaxis_title='Year', 
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_global, use_container_width=True)
    
    with st.expander("About the Temperature Data"):
        st.write("""
        **Data Source:** This data comes from NOAA's National Centers for Environmental Information (NCEI) 
        global temperature anomaly dataset, with fallback to NASA GISS Surface Temperature Analysis (GISTEMP v4).
        
        **What is shown:** Annual average global land and ocean surface temperatures. Temperature anomalies 
        (differences from the 20th century baseline) are converted to actual temperatures for easier interpretation.
        
        **Trendline Methodology:** Linear regression is used to illustrate the overall direction of temperature changes.
        This helps visualize whether temperatures are generally increasing, decreasing, or remaining stable over time.
        
        **Why this matters:** This is the authoritative global temperature dataset used by climate scientists 
        worldwide. It combines thousands of weather stations, ships, and buoys to create a comprehensive 
        picture of Earth's temperature.
        """)
else:
    st.error("Unable to fetch global climate data. Please check your internet connection and try again.")

st.caption("Source: NOAA National Centers for Environmental Information (NCEI) / NASA GISS")

# ========================================
# CARBON EMISSIONS DATA SECTION
# ========================================
st.divider()
st.header("Global Carbon Emissions")

if df_emissions is not None and not df_emissions.empty:
    st.info(f"Dataset: {len(df_emissions)} years ({int(df_emissions['year'].min())} - {int(df_emissions['year'].max())})")
    
    recent_emissions = df_emissions['co2'].iloc[-1]
    earliest_emissions = df_emissions['co2'].iloc[0]
    emissions_change = recent_emissions - earliest_emissions
    percent_change = (emissions_change / earliest_emissions) * 100
    
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Current Annual CO2 Emissions", 
            value=f"{recent_emissions:,.0f} Mt"
        )
    with col2:
        st.metric(
            label=f"Change Since {int(df_emissions['year'].min())}", 
            value=f"{emissions_change:,.0f} Mt",
            delta=f"{percent_change:.1f}%"
        )
    with col3:
        st.metric(
            label="Current Per Capita Emissions", 
            value=f"{df_emissions['co2_per_capita'].iloc[-1]:.2f} t/person"
        )
    
    st.subheader("CO2 Emissions Over Time")
    
    fig_emissions = go.Figure()
    fig_emissions.add_trace(
        go.Scatter(
            x=df_emissions['year'], 
            y=df_emissions['co2'], 
            mode='lines',
            name='Total Emissions',
            fill='tozeroy',
            line=dict(color='darkred')
        )
    )
    fig_emissions.update_layout(
        title='Global CO2 Emissions (Million Tonnes)',
        xaxis_title='Year',
        yaxis_title='CO2 Emissions (Mt)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_emissions, use_container_width=True)
    
    st.subheader("Per Capita CO2 Emissions")
    fig_per_capita = go.Figure()
    fig_per_capita.add_trace(
        go.Scatter(
            x=df_emissions['year'], 
            y=df_emissions['co2_per_capita'], 
            mode='lines',
            name='Per Capita Emissions',
            line=dict(color='orange')
        )
    )
    fig_per_capita.update_layout(
        title='Global Per Capita CO2 Emissions',
        xaxis_title='Year',
        yaxis_title='CO2 Emissions (tonnes per person)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_per_capita, use_container_width=True)
    
    with st.expander("About Carbon Emissions Data"):
        st.write("""
        This data shows global carbon dioxide (CO2) emissions measured in million tonnes (Mt). 
        The data is sourced from Our World in Data, which compiles information from multiple 
        authoritative sources including the Global Carbon Project and BP Statistical Review.
        
        - **Total Emissions:** Annual global CO2 emissions from fossil fuels and industry
        - **Per Capita Emissions:** Average CO2 emissions per person globally
        
        Rising CO2 levels are the primary driver of climate change and correlate strongly 
        with the temperature increases shown in the climate data above.
        """)
    
    st.caption("Source: Our World in Data (CO2 and Greenhouse Gas Emissions Database)")
else:
    st.error("Unable to load carbon emissions data.")

# ========================================
# METHANE EMISSIONS DATA SECTION
# ========================================
st.divider()
st.header("Global Methane Emissions")

if df_methane is not None and not df_methane.empty:
    st.info(f"Dataset: {len(df_methane)} years ({int(df_methane['year'].min())} - {int(df_methane['year'].max())})")
    
    recent_methane = df_methane['methane'].iloc[-1]
    earliest_methane = df_methane['methane'].iloc[0]
    methane_change = recent_methane - earliest_methane
    percent_change_methane = (methane_change / earliest_methane) * 100
    
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Current Annual CH4 Emissions", 
            value=f"{recent_methane:,.0f} Mt"
        )
    with col2:
        st.metric(
            label=f"Change Since {int(df_methane['year'].min())}", 
            value=f"{methane_change:,.0f} Mt",
            delta=f"{percent_change_methane:.1f}%"
        )
    with col3:
        st.metric(
            label="Current Per Capita Emissions", 
            value=f"{df_methane['methane_per_capita'].iloc[-1]:.2f} t/person"
        )
    
    st.subheader("CH4 Emissions Over Time")
    
    fig_methane = go.Figure()
    fig_methane.add_trace(
        go.Scatter(
            x=df_methane['year'], 
            y=df_methane['methane'], 
            mode='lines',
            name='Total Emissions',
            fill='tozeroy',
            line=dict(color='darkgreen')
        )
    )
    fig_methane.update_layout(
        title='Global Methane Emissions (Million Tonnes)',
        xaxis_title='Year',
        yaxis_title='CH4 Emissions (Mt)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_methane, use_container_width=True)
    
    st.subheader("Per Capita CH4 Emissions")
    fig_per_capita_methane = go.Figure()
    fig_per_capita_methane.add_trace(
        go.Scatter(
            x=df_methane['year'], 
            y=df_methane['methane_per_capita'], 
            mode='lines',
            name='Per Capita Emissions',
            line=dict(color='green')
        )
    )
    fig_per_capita_methane.update_layout(
        title='Global Per Capita Methane Emissions',
        xaxis_title='Year',
        yaxis_title='CH4 Emissions (tonnes per person)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_per_capita_methane, use_container_width=True)
    
    with st.expander("About Methane Emissions Data"):
        st.write("""
        This data shows global methane (CH4) emissions measured in million tonnes (Mt). 
        The data is sourced from Our World in Data, which compiles information from multiple 
        authoritative sources.
        
        - **Total Emissions:** Annual global CH4 emissions from various sources
        - **Per Capita Emissions:** Average CH4 emissions per person globally
        
        Methane is a potent greenhouse gas with a global warming potential much higher than CO2 
        over shorter time periods. Major sources include agriculture (livestock), natural gas 
        production, and landfills. Reducing methane emissions is crucial for climate mitigation.
        """)
    
    st.caption("Source: Our World in Data (CO2 and Greenhouse Gas Emissions Database)")
else:
    st.error("Unable to load methane emissions data.")

# ========================================
# NITROUS OXIDE EMISSIONS DATA SECTION
# ========================================
st.divider()
st.header("Global Nitrous Oxide Emissions")

if df_n2o is not None and not df_n2o.empty:
    st.info(f"Dataset: {len(df_n2o)} years ({int(df_n2o['year'].min())} - {int(df_n2o['year'].max())})")
    
    recent_n2o = df_n2o['nitrous_oxide'].iloc[-1]
    earliest_n2o = df_n2o['nitrous_oxide'].iloc[0]
    n2o_change = recent_n2o - earliest_n2o
    percent_change_n2o = (n2o_change / earliest_n2o) * 100
    
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Current Annual N2O Emissions", 
            value=f"{recent_n2o:,.0f} Mt"
        )
    with col2:
        st.metric(
            label=f"Change Since {int(df_n2o['year'].min())}", 
            value=f"{n2o_change:,.0f} Mt",
            delta=f"{percent_change_n2o:.1f}%"
        )
    with col3:
        st.metric(
            label="Current Per Capita Emissions", 
            value=f"{df_n2o['nitrous_oxide_per_capita'].iloc[-1]:.2f} t/person"
        )
    
    st.subheader("N2O Emissions Over Time")
    
    fig_n2o = go.Figure()
    fig_n2o.add_trace(
        go.Scatter(
            x=df_n2o['year'], 
            y=df_n2o['nitrous_oxide'], 
            mode='lines',
            name='Total Emissions',
            fill='tozeroy',
            line=dict(color='purple')
        )
    )
    fig_n2o.update_layout(
        title='Global Nitrous Oxide Emissions (Million Tonnes)',
        xaxis_title='Year',
        yaxis_title='N2O Emissions (Mt)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_n2o, use_container_width=True)
    
    st.subheader("Per Capita N2O Emissions")
    fig_per_capita_n2o = go.Figure()
    fig_per_capita_n2o.add_trace(
        go.Scatter(
            x=df_n2o['year'], 
            y=df_n2o['nitrous_oxide_per_capita'], 
            mode='lines',
            name='Per Capita Emissions',
            line=dict(color='mediumpurple')
        )
    )
    fig_per_capita_n2o.update_layout(
        title='Global Per Capita Nitrous Oxide Emissions',
        xaxis_title='Year',
        yaxis_title='N2O Emissions (tonnes per person)',
        hovermode='x unified',
        template='plotly_white'
    )
    st.plotly_chart(fig_per_capita_n2o, use_container_width=True)
    
    with st.expander("About Nitrous Oxide Emissions Data"):
        st.write("""
        This data shows global nitrous oxide (N2O) emissions measured in million tonnes (Mt). 
        The data is sourced from Our World in Data.
        
        - **Total Emissions:** Annual global N2O emissions from various sources
        - **Per Capita Emissions:** Average N2O emissions per person globally
        
        Nitrous oxide has a global warming potential approximately 300 times that of CO2 over 
        a 100-year period. Major sources include agricultural soil management (fertilizers), 
        livestock manure, industrial processes, and fossil fuel combustion. N2O also depletes 
        the ozone layer, making its reduction critical for both climate and atmospheric health.
        """)
    
    st.caption("Source: Our World in Data (CO2 and Greenhouse Gas Emissions Database)")
else:
    st.error("Unable to load nitrous oxide emissions data.")
