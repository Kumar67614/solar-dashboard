import streamlit as st
import plotly.graph_objects as go

# 🎨 Page Configuration & Custom CSS Styling
st.set_page_config(page_title="SQS Solar Water Heating Engine", layout="wide")

# Custom CSS for polished layout and clean KPI cards
st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-title { font-size: 14px; color: #6c757d; font-weight: bold; }
    .metric-value { font-size: 24px; color: #1c1c1e; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("☀️ SQS Solar Water Heating Design Engine")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS
st.sidebar.header("🎯 Customer Technical Inputs")

water = st.sidebar.number_input("Water Requirement (LPD)", value=5000, step=500)
tout = st.sidebar.number_input("Desired Output Temperature (°C)", value=80, min_value=30, max_value=100)
tin = st.sidebar.number_input("Cold Water Inlet Temperature (°C)", value=25, min_value=5, max_value=40)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ System Modifiers")
safety = st.sidebar.slider("Safety / Loss Factor", min_value=1.0, max_value=1.5, value=1.15, step=0.05)

# 🔢 CONSTANTS & CORE ENGINE CALCULATIONS
cp = 4.186          # Specific heat capacity of water
module_energy = 22  # kWh/day per module output
module_area = 7.2   # m² per module

# Thermodynamics
dt = tout - tin
energy = (water * cp * dt) / 3600  # Required energy in kWh/day

# Sizing
modules = round((energy * safety) / module_energy)
modules = max(modules, 1)  # Ensure at least 1 module is deployed
area = modules * module_area
flow_lpm = ((modules / 2) * 250) / 60  # Calculated system flow rate in LPM
flow_kghr = flow_lpm * 60             # Converted to kg/hr for the Flow Matrix

# Environmental & Financials
annual_savings = energy * 365 * 10
co2_reduction = energy * 365 * 0.82
efficiency = min((energy / (modules * module_energy)) * 100, 100.0)

# 📊 MAIN DASHBOARD ROW 1: PRIMARY HARDWARE METRICS
st.subheader("📋 Core Engineering Sizing")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-container"><div class="metric-title">🔥 THERMAL ENERGY DEMAND</div><div class="metric-value">{energy:.1f} kWh/day</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-left-color: #28a745;"><div class="metric-title">📦 REQUIRED MODULES</div><div class="metric-value">{modules} Units</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-left-color: #ffc107;"><div class="metric-title">📐 TOTAL COLLECTOR AREA</div><div class="metric-value">{area:.1f} m²</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-left-color: #17a2b8;"><div class="metric-title">💧 DESIGN FLOW RATE</div><div class="metric-value">{flow_lpm:.1f} LPM</div></div>', unsafe_allow_html=True)

st.markdown(" ")

# 📊 MAIN DASHBOARD ROW 2: SUSTAINABILITY & FINANCIALS
st.subheader("🌱 Sustainability & Financial Impacts")
c5, c6 = st.columns(2)

with c5:
    st.markdown(f'<div class="metric-container" style="border-left-color: #20c997;"><div class="metric-title">💰 ESTIMATED ANNUAL SAVINGS</div><div class="metric-value">₹ {annual_savings:,.0f}</div></div>', unsafe_allow_html=True)
with c6:
    st.markdown(f'<div class="metric-container" style="border-left-color: #6f42c1;"><div class="metric-title">📉 ANNUAL CO₂ REDUCTION</div><div class="metric-value">{co2_reduction:,.0f} kg/year</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ⚡ VISUALIZATIONS & LOGIC ENGINES
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("📈 System Operating Efficiency")
    
    # Advanced Gauge Chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=efficiency,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#007bff"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#f8d7da'},
                {'range': [50, 80], 'color': '#fff3cd'},
                {'range': [80, 100], 'color': '#d4edda'}
            ],
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🎛️ Flow Rate Control & Pump Automation")
    
    # Dynamically select operational parameters based on calculated flow (kg/hr)
    if flow_kghr <= 150:
        zone = "🟢 LOW THERMAL MASS"
        desc = "Fast Temp Response"
        start = "09:05 AM"
        irr = "> 320 W/m²"
        dt_stage = "+2.8°C to +3.5°C"
        harvest = "High Temperature Gain (Low Power)"
    elif flow_kghr <= 250:
        zone = "🟡 TRANSITIONAL ZONE"
        desc = "High Thermal Lag"
        start = "09:25 AM"
        irr = "> 370 W/m²"
        dt_stage = "+0.1°C to +0.5°C"
        harvest = "Sub-Optimal Efficiency"
    elif flow_kghr <= 350:
        zone = "🔵 CONVECTIVE RETENTION"
        desc = "Low Collector Loss"
        start = "09:05 AM"
        irr = "> 320 W/m²"
        dt_stage = "+0.5°C to +0.7°C"
        harvest = "High Wattage / Net Energy Yield"
    else:
        zone = "🔴 MAX VELOCITY"
        desc = "Instant Extraction"
        start = "09:00 AM"
        irr = "> 260 W/m²"
        dt_stage = "+0.3°C"
        harvest = "Max Mass Net Energy Yield"

    # Dynamic Pump Hardware Selection
    if flow_lpm < 20:
        pump = "1 HP Circulation Pump"
    elif flow_lpm < 40:
        pump = "2 HP Circulation Pump"
    else:
        pump = "3 HP Circulation Pump"

    # Render Hardware and Live Strategy Dashboard Data
    st.info(f"**Recommended Hardware:** {pump}")
    
    st.markdown(f"""
    | Operational Metric | Live Controller Data Status |
    | :--- | :--- |
    | **Current Target State** | **{zone}** ({flow_kghr:.1f} kg/hr) |
    | **Profile Strategy** | *"{desc}"* |
    | **Optimal Start Time** | ⏰ {start} |
    | **Target Irradiance Gate** | ☀️ {irr} |
    | **Expected Initial $\Delta$T** | 🌡️ {dt_stage} |
    | **Harvest Classification** | 🔋 {harvest} |
    """, unsafe_allow_html=True)