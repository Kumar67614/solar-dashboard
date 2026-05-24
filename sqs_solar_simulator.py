import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="SQS Industrial SHIP Analyzer",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

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
    box-shadow:0px 2px 6px rgba(0,0,0,0.1);
    margin-bottom:10px;
}

.metric-title{
    font-size:13px;
    font-weight:bold;
    color:#555;
}

.metric-value{
    font-size:28px;
    font-weight:bold;
    color:#111;
}

.section-header{
    color:#0f52ba;
    font-size:24px;
    margin-top:25px;
    margin-bottom:15px;
    border-bottom:2px solid #0f52ba;
    padding-bottom:5px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("SQS Industrial Solar Process Heat Analyzer")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("Process Inputs")

industry = st.sidebar.selectbox(
    "Industry Type",
    [
        "Dairy Plant",
        "Textile Industry",
        "Pharmaceutical",
        "Thermal Power",
        "Chemical Plant"
    ]
)

water = st.sidebar.number_input(
    "Water Requirement LPD",
    min_value=100,
    value=8000,
    step=100
)

tin = st.sidebar.number_input(
    "Inlet Temperature °C",
    value=25
)

tout = st.sidebar.number_input(
    "Outlet Temperature °C",
    value=90
)

ambient = st.sidebar.number_input(
    "Ambient Temperature °C",
    value=30
)

wind = st.sidebar.slider(
    "Wind Speed m/s",
    0.0,
    10.0,
    3.0
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost ₹",
    value=85.0
)

# ---------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------

cp = 4.186

dt = max(tout - tin, 1)

energy = (water * cp * dt) / 3600

collector_efficiency = 0.72 - (0.01 * wind)

collector_efficiency = max(0.35, min(collector_efficiency, 0.80))

module_output = 22 * collector_efficiency

modules = max(1, round(energy / module_output))

area = modules * 7.2

flow = ((modules / 2) * 250) / 60

annual_savings = energy * 365 * fuel_cost * 0.35

co2 = energy * 365 * 0.82 / 1000

capex = area * 14000

payback = capex / annual_savings if annual_savings > 0 else 0

roi = (annual_savings / capex) * 100 if capex > 0 else 0

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Engineering Design Outputs</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-title">THERMAL ENERGY</div>
        <div class="metric-value">{energy:.1f} kWh/day</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-title">SOLAR MODULES</div>
        <div class="metric-value">{modules}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-title">COLLECTOR AREA</div>
        <div class="metric-value">{area:.1f} m²</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-title">FLOW RATE</div>
        <div class="metric-value">{flow:.1f} LPM</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# ECONOMICS
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Economic Analysis</div>',
    unsafe_allow_html=True
)

e1, e2, e3, e4 = st.columns(4)

e1.metric("Annual Savings", f"₹ {annual_savings:,.0f}")
e2.metric("CO2 Reduction", f"{co2:.1f} Ton/year")
e3.metric("Payback", f"{payback:.2f} Years")
e4.metric("ROI", f"{roi:.1f} %")

# ---------------------------------------------------
# EFFICIENCY GAUGE
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Collector Efficiency</div>',
    unsafe_allow_html=True
)

fig = go.Figure(go.Indicator(
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

fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# SOLAR RADIATION GRAPH
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Monthly Solar Radiation</div>',
    unsafe_allow_html=True
)

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

radiation = [
    5.3,6.1,6.8,7.1,7.2,5.0,
    3.8,3.9,5.1,5.5,5.2,4.9
]

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=months,
    y=radiation
))

fig2.update_layout(
    xaxis_title="Month",
    yaxis_title="kWh/m²/day",
    height=400
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# PUMP RECOMMENDATION
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Pump Recommendation</div>',
    unsafe_allow_html=True
)

if flow < 25:
    pump = "1.5 HP Pump"
elif flow < 50:
    pump = "3 HP Pump"
else:
    pump = "5 HP Pump"

st.success(f"Recommended Pump: {pump}")

# ---------------------------------------------------
# GRAPHVIZ P&ID
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">P&ID Diagram</div>',
    unsafe_allow_html=True
)

diagram = f"""
digraph {{
    rankdir=LR;

    node [shape=box style=filled fillcolor=lightblue];

    Inlet[label="Cold Water"];
    Tank[label="Storage Tank"];
    Pump[label="Pump"];
    Collector[label="Solar Collector"];
    Process[label="Process Load"];

    Inlet -> Tank;
    Tank -> Pump;
    Pump -> Collector;
    Collector -> Process;
}}
"""

st.graphviz_chart(diagram)

# ---------------------------------------------------
# SUMMARY TABLE
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Proposal Summary</div>',
    unsafe_allow_html=True
)

st.table({
    "Parameter": [
        "Industry",
        "Thermal Load",
        "Modules",
        "Area",
        "Flow",
        "Pump",
        "Payback"
    ],
    "Value": [
        industry,
        f"{energy:.1f} kWh/day",
        modules,
        f"{area:.1f} m²",
        f"{flow:.1f} LPM",
        pump,
        f"{payback:.2f} Years"
    ]
})
