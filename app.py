import streamlit as st
import plotly.graph_objects as go
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SQS Solar Dashboard",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.metric-container{
    background:white;
    padding:15px;
    border-radius:10px;
    border-left:5px solid #0f52ba;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    margin-bottom:15px;
}

.metric-title{
    font-size:14px;
    font-weight:bold;
    color:#555;
}

.metric-value{
    font-size:28px;
    font-weight:bold;
    color:#111;
}

.section-header{
    font-size:24px;
    font-weight:bold;
    color:#0f52ba;
    margin-top:25px;
    margin-bottom:15px;
    border-bottom:2px solid #0f52ba;
    padding-bottom:8px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("SQS Industrial Solar Process Heat Analyzer")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Input Parameters")

industry = st.sidebar.selectbox(
    "Industry Type",
    [
        "Dairy Plant",
        "Textile Industry",
        "Chemical Plant",
        "Pharmaceutical Industry",
        "Power Plant"
    ]
)

water = st.sidebar.number_input(
    "Water Requirement (LPD)",
    min_value=100,
    value=5000,
    step=100
)

tin = st.sidebar.number_input(
    "Inlet Temperature (°C)",
    min_value=1,
    max_value=80,
    value=25
)

tout = st.sidebar.number_input(
    "Outlet Temperature (°C)",
    min_value=30,
    max_value=120,
    value=85
)

ambient = st.sidebar.number_input(
    "Ambient Temperature (°C)",
    value=28
)

wind = st.sidebar.slider(
    "Wind Speed (m/s)",
    0.0,
    10.0,
    3.0
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost ₹/Unit",
    value=85.0
)

# =========================================================
# CONSTANTS
# =========================================================

cp = 4.186
collector_area_per_module = 7.2
eta0 = 0.75
irradiance = 800

# =========================================================
# CALCULATIONS
# =========================================================

dt = tout - tin

if dt <= 0:
    dt = 1

thermal_load = (water * cp * dt) / 3600

collector_efficiency = eta0 - (
    ((tout - ambient) / irradiance) * 2.5
)

collector_efficiency = max(0.35, min(collector_efficiency, 0.75))

energy_per_module = (
    collector_area_per_module *
    collector_efficiency *
    4.5
)

modules = max(1, round(thermal_load / energy_per_module))

total_area = modules * collector_area_per_module

flow_lpm = (water / 24) / 60

annual_energy = thermal_load * 300

annual_savings = annual_energy * fuel_cost

capex = total_area * 14000

payback = capex / annual_savings if annual_savings > 0 else 0

co2 = annual_energy * 0.82 / 1000

# =========================================================
# KPI SECTION
# =========================================================

st.markdown(
    '<div class="section-header">Engineering Sizing Results</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-container">
    <div class="metric-title">Thermal Load</div>
    <div class="metric-value">{thermal_load:.1f} kWh/day</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-container">
    <div class="metric-title">Solar Modules</div>
    <div class="metric-value">{modules}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-container">
    <div class="metric-title">Collector Area</div>
    <div class="metric-value">{total_area:.1f} m²</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-container">
    <div class="metric-title">Flow Rate</div>
    <div class="metric-value">{flow_lpm:.1f} LPM</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SECOND ROW
# =========================================================

c5, c6, c7 = st.columns(3)

with c5:
    st.metric(
        "Annual Savings",
        f"₹ {annual_savings:,.0f}"
    )

with c6:
    st.metric(
        "Payback Period",
        f"{payback:.2f} Years"
    )

with c7:
    st.metric(
        "CO₂ Reduction",
        f"{co2:.1f} Tons/Year"
    )

# =========================================================
# EFFICIENCY GAUGE
# =========================================================

st.markdown(
    '<div class="section-header">Collector Efficiency</div>',
    unsafe_allow_html=True
)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=collector_efficiency * 100,
    title={'text': "Collector Efficiency %"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "green"},
        'steps': [
            {'range': [0, 40], 'color': "#ffcccc"},
            {'range': [40, 70], 'color': "#fff0b3"},
            {'range': [70, 100], 'color': "#ccffcc"}
        ]
    }
))

fig_gauge.update_layout(height=400)

st.plotly_chart(fig_gauge, use_container_width=True)

# =========================================================
# MONTHLY RADIATION GRAPH
# =========================================================

st.markdown(
    '<div class="section-header">Monthly Solar Radiation</div>',
    unsafe_allow_html=True
)

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

radiation = [
    5.1,5.8,6.5,7.0,7.2,5.5,
    4.0,4.2,5.1,5.5,5.0,4.8
]

fig_rad = go.Figure()

fig_rad.add_trace(go.Bar(
    x=months,
    y=radiation
))

fig_rad.update_layout(
    xaxis_title="Month",
    yaxis_title="kWh/m²/day",
    height=400
)

st.plotly_chart(fig_rad, use_container_width=True)

# =========================================================
# PUMP RECOMMENDATION
# =========================================================

st.markdown(
    '<div class="section-header">Pump Recommendation</div>',
    unsafe_allow_html=True
)

if flow_lpm < 20:
    pump = "1 HP Pump"
elif flow_lpm < 50:
    pump = "2 HP Pump"
else:
    pump = "5 HP Pump"

st.success(f"Recommended Pump: {pump}")

# =========================================================
# PIPE SIZE
# =========================================================

if flow_lpm < 20:
    pipe = "DN25"
elif flow_lpm < 50:
    pipe = "DN40"
else:
    pipe = "DN50"

st.info(f"Recommended Pipe Size: {pipe}")

# =========================================================
# SIMPLE P&ID
# =========================================================

st.markdown(
    '<div class="section-header">System P&ID</div>',
    unsafe_allow_html=True
)

graph = """
digraph G {

rankdir=LR;

node [shape=box style=filled fillcolor=lightblue];

Tank [label="Storage Tank"];
Pump [label="Pump"];
Collector [label="Solar Collector"];
Process [label="Process Load"];

Tank -> Pump;
Pump -> Collector;
Collector -> Process;
Process -> Tank;

}
"""

st.graphviz_chart(graph)

# =========================================================
# SUMMARY TABLE
# =========================================================

st.markdown(
    '<div class="section-header">Project Summary</div>',
    unsafe_allow_html=True
)

st.table({
    "Parameter": [
        "Industry",
        "Thermal Load",
        "Modules",
        "Collector Area",
        "Flow Rate",
        "Annual Savings",
        "Payback"
    ],
    "Value": [
        industry,
        f"{thermal_load:.1f} kWh/day",
        modules,
        f"{total_area:.1f} m²",
        f"{flow_lpm:.1f} LPM",
        f"₹ {annual_savings:,.0f}",
        f"{payback:.2f} Years"
    ]
})
