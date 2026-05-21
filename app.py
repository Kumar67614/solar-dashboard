import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Solar Thermal Collector Performance Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #FF4B4B; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #555555; margin-bottom: 25px; }
    .metric-card { background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; }
    </style>
""", unsafe_allowed_html=True)

# Map human-readable profiles to the uploaded files
REF_FILES = {
    "100 LPH Profile - Target 60°C": "60_06-02-2026_SQS.csv",
    "100 LPH Profile - Target 80°C": "80_18-02-2026_SQS.csv",
    "100 LPH Profile - Target 90°C": "90_09-02-2026_SQS_.csv",
    "200 LPH Profile - Target 60°C": "SQS_16-02-2026.csv",
    "200 LPH Profile - Target 90°C": "22-11-2025_SQS.csv",
    "200 LPH Profile - Target 95°C": "05-02-2026_SQS.csv",
    "200 LPH Profile - Target 100°C": "21-11-2025_SQS.csv",
    "300 LPH Profile - Target 60°C": "60_11-02-2026_SQS.csv",
    "300 LPH Profile - Target 70°C": "70_10-02-2026_SQS.csv",
    "300 LPH Profile - Target 80°C": "80__12-02-2026_SQS.csv",
    "300 LPH Profile - Target 90°C": "90_13-02-2026_SQS.csv",
    "300 LPH Profile - Target 100°C": "100_18.11.25_SQS.csv",
    "400 LPH Profile - Target 60°C": "28-01-2026_SQS_Jan28_60.csv",
    "400 LPH Profile - Target 70°C": "27-01-2026_SQS_70.csv",
    "400 LPH Profile - Target 80°C": "24-01-2026_SQS_80.csv",
    "400 LPH Profile - Target 100°C": "29-01-2026_SQS_100.csv"
}

# Helper function to programmatically match column names across varying dataset styles
def find_col(columns, keyword):
    for col in columns:
        if keyword.upper() in col.upper():
            return col
    return None

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/fluent/96/000000/solar-panel.png", width=80)
st.sidebar.header("🔧 Reference Controls")

selected_profile = st.sidebar.selectbox(
    "Select Flow Rate Profile:",
    options=list(REF_FILES.keys())
)

filename = REF_FILES[selected_profile]

# Load and process selected reference data file
if os.path.exists(filename):
    try:
        df = pd.read_csv(filename, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filename, encoding='latin1')
    
    # Standardize spaces in column headers
    df.columns = [c.strip() for c in df.columns]
    
    # Locate essential column mappings
    c_time = find_col(df.columns, 'TIME') or 'Time'
    c_tin = find_col(df.columns, 'TEMP IN')
    c_tout = find_col(df.columns, 'TEMP OUT')
    c_tamb = find_col(df.columns, 'AMBIENT TEMP')
    c_rad = find_col(df.columns, 'IT(') or find_col(df.columns, 'W/m2')
    c_flow = find_col(df.columns, 'FLOW RATE')
    c_ein = find_col(df.columns, 'ENERGY INPUT')
    c_eout = find_col(df.columns, 'ENERGY OUTPUT')
    c_eff = find_col(df.columns, 'EFFICIENCY')
    c_pin = find_col(df.columns, 'PRES IN')
    c_pout = find_col(df.columns, 'PRES OUT')
    c_pdel = find_col(df.columns, 'DELTA PRES')

    # Data Cleaning and Safe Conversion
    for col in [c_tin, c_tout, c_tamb, c_rad, c_flow, c_ein, c_eout, c_eff, c_pin, c_pout, c_pdel]:
        if col:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Normalize Efficiency column to standard decimal if stored as percentages > 1
    if c_eff and df[c_eff].max() > 1.0:
        df[c_eff] = df[c_eff] / 100.0

    # Filter data to active solar operational window for summary calculations
    active_df = df[(df[c_rad] > 50) & (df[c_flow] > 2)]
    if active_df.empty:
        active_df = df

    # App Main Layout Headers
    st.markdown(f"<div class='main-title'>☀️ Solar Thermal Performance Dashboard</div>", unsafe_allowed_html=True)
    st.markdown(f"<div class='subtitle'>Visualizing baseline characteristics for <b>{selected_profile}</b> (Source File: {filename})</div>", unsafe_allowed_html=True)

    # ------------------ KPI CARDS ------------------
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        avg_rad = active_df[c_rad].mean() if c_rad else 0
        st.metric(label="Avg Solar Radiation", value=f"{avg_rad:.1f} W/m²")
        
    with kpi2:
        avg_flow = active_df[c_flow].mean() if c_flow else 0
        st.metric(label="Avg Mass Flow Rate", value=f"{avg_flow:.1f} kg/hr")
        
    with kpi3:
        if c_tin and c_tout:
            max_delta = (df[c_tout] - df[c_tin]).max()
        else:
            max_delta = 0
        st.metric(label="Max Temp Rise (ΔT)", value=f"{max_delta:.1f} °C")
        
    with kpi4:
        avg_eout = active_df[c_eout].mean() if c_eout else 0
        st.metric(label="Avg Thermal Output", value=f"{avg_eout:.1f} W")
        
    with kpi5:
        avg_eff = active_df[c_eff].mean() * 100 if c_eff else 0
        # Restrict valid visual ranges for cleaner visualization
        avg_eff = min(max(avg_eff, 0.0), 100.0)
        st.metric(label="Mean Solar Efficiency", value=f"{avg_eff:.1f} %")

    st.markdown("---")

    # ------------------ INTERACTIVE TABS ------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Thermal & Radiation Profile", 
        "⚡ Energy Balance & Efficiency", 
        "💧 Hydraulics & Pressure Drop", 
        "📋 Raw Dataset Explorer"
    ])

    with tab1:
        st.subheader("Temperature Gradients and Available Solar Irradiance")
        
        # Plotly dual-axis chart for Temperatures vs Irradiance
        fig1 = go.Figure()
        if c_tin:
            fig1.add_trace(go.Scatter(x=df[c_time], y=df[c_tin], name="Inlet Temp (Tin)", line=dict(color='#1f77b4', width=2.5)))
        if c_tout:
            fig1.add_trace(go.Scatter(x=df[c_time], y=df[c_tout], name="Outlet Temp (Tout)", line=dict(color='#ff7f0e', width=2.5)))
        if c_tamb:
            fig1.add_trace(go.Scatter(x=df[c_time], y=df[c_tamb], name="Ambient Temp (Tamb)", line=dict(color='#2ca02c', dash='dash')))
            
        fig1.update_layout(
            yaxis=dict(title="Temperature (°C)", titlefont=dict(color="#1f77b4"), tickfont=dict(color="#1f77b4")),
            xaxis=dict(title="Time of Day", tickangle=45),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
            margin=dict(l=40, r=40, t=20, b=40),
            height=450
        )
        
        # Second axis for Solar Radiation
        if c_rad:
            fig1.add_trace(go.Scatter(x=df[c_time], y=df[c_rad], name="Solar Radiation (It)", yaxis="y2", line=dict(color='rgba(214, 39, 40, 0.4)', width=2), fill='tozeroy'))
            fig1.update_layout(
                yaxis2=dict(title="Solar Radiation (W/m²)", titlefont=dict(color="#d62728"), tickfont=dict(color="#d62728"), overlaying="y", side="right")
            )
            
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("Thermal Power Output vs. Efficiency Dynamics")
        col_t2_1, col_t2_2 = st.columns(2)
        
        with col_t2_1:
            fig_eng = go.Figure()
            if c_ein:
                fig_eng.add_trace(go.Scatter(x=df[c_time], y=df[c_ein], name="Energy Input (W)", line=dict(color='#aec7e8')))
            if c_eout:
                fig_eng.add_trace(go.Scatter(x=df[c_time], y=df[c_eout], name="Thermal Energy Output (W)", line=dict(color='#ff4b4b', width=3)))
            fig_eng.update_layout(title="System Thermal Power Balance", xaxis_title="Time", yaxis_title="Power (W)", height=380)
            st.plotly_chart(fig_eng, use_container_width=True)
            
        with col_t2_2:
            fig_eff = go.Figure()
            if c_eff:
                # Filter out outlier noise for dynamic tracking
                valid_eff = df[(df[c_eff] >= 0) & (df[c_eff] <= 1)]
                fig_eff.add_trace(go.Scatter(x=valid_eff[c_time], y=valid_eff[c_eff] * 100, name="Efficiency (%)", mode='lines+markers', line=dict(color='#2ca02c')))
            fig_eff.update_layout(title="Collector Instantaneous Efficiency Curve", xaxis_title="Time", yaxis_title="Efficiency (%)", yaxis_range=[0, 105], height=380)
            st.plotly_chart(fig_eff, use_container_width=True)

    with tab3:
        st.subheader("Hydraulic Loop Diagnostics")
        col_t3_1, col_t3_2 = st.columns([2, 1])
        
        with col_t3_1:
            fig_pres = go.Figure()
            if c_pin:
                fig_pres.add_trace(go.Scatter(x=df[c_time], y=df[c_pin], name="Inlet Pressure", line=dict(color='#17becf')))
            if c_pout:
                fig_pres.add_trace(go.Scatter(x=df[c_time], y=df[c_pout], name="Outlet Pressure", line=dict(color='#9467bd')))
            fig_pres.update_layout(title="Fluid Line Pressures", xaxis_title="Time", yaxis_title="Pressure (bar)", height=380)
            st.plotly_chart(fig_pres, use_container_width=True)
            
        with col_t3_2:
            fig_pdel = go.Figure()
            if c_pdel:
                fig_pdel.add_trace(go.Bar(x=df[c_time], y=df[c_pdel], name="Pressure Drop", marker_color='#7f7f7f'))
            fig_pdel.update_layout(title="System Pressure Drop (ΔP)", xaxis_title="Time", yaxis_title="Drop (bar)", height=380)
            st.plotly_chart(fig_pdel, use_container_width=True)

    with tab4:
        st.subheader("Time Series Reference Data View")
        st.dataframe(df, use_container_width=True)
        
        # Download Option
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download current reference configuration as CSV",
            data=csv_data,
            file_name=f"processed_{filename}",
            mime="text/csv"
        )
else:
    st.error(f"⚠️ Reference data file `{filename}` was not found in the workspace directory. Please double-check file presence.")
