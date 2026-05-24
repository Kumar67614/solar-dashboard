import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SQS Solar SHIP Dashboard",
    page_icon="☀️",
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

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.metric-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 6px solid #0f52ba;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.metric-title {
    font-size: 14px;
    color: gray;
    font-weight: 600;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #111;
}

.section-title {
    font-size: 26px;
    font-weight: bold;
    color: #0f52ba;
    margin-top: 20px;
    margin-bottom: 10px;
}

.small-card {
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☀️ SQS Solar Water Heating Design Engine")
st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ System Inputs")

industry_type = st.sidebar.selectbox(
    "Select Industry",
    [
        "Dairy Plant",
        "Textile Industry",
        "Pharmaceutical",
        "Chemical Plant",
        "Food Processing"
    ],
    key="industry_select"
)

water = st.sidebar.number_input(
    "Daily Hot Water Requirement (LPD)",
    min_value=100,
    value=5000,
    step=100,
    key="water_input"
)

tout = st.sidebar.number_input(
    "Required Output Temperature (°C)",
    min_value=30,
    max_value=120,
    value=80,
    key="tout_input"
)

tin = st.sidebar.number_input(
    "Cold Water Inlet Temperature (°C)",
    min_value=1,
    max_value=50,
    value=25,
    key="tin_input"
)

ambient_temp = st.sidebar.slider(
    "Ambient Temperature (°C)",
    10,
    45,
    30,
    key="ambient_input"
)

wind_speed = st.sidebar.slider(
    "Wind Speed (m/s)",
    0.0,
    10.0,
    2.0,
    key="wind_input"
)

fuel_type = st.sidebar.selectbox(
    "Backup Fuel Type",
    [
        "Diesel",
        "Natural Gas",
        "Electric Heater"
    ],
    key="fuel_select"
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost (₹/Unit)",
    value=85,
    step=5,
    key="fuel_cost"
)

# =========================================================
# CONSTANTS
# =========================================================

cp = 4.186
module_area = 7.2
module_output = 22
safety_factor = 1.15

# =========================================================
# CALCULATIONS
# =========================================================

dt = tout - tin

if dt <= 0:
    dt = 1

energy = (water * cp * dt) / 3600

gross_energy = energy * safety_factor

modules = round(gross_energy / module_output)

if modules < 1:
    modules = 1

area = modules * module_area

storage_tank_capacity = water * 1.2

flow_lpm = ((modules / 2) * 250) / 60

flow_kghr = flow_lpm * 60

efficiency = (energy / (modules * module_output)) * 100

efficiency = max(35, min(efficiency, 85))

annual_energy = gross_energy * 365

annual_savings = annual_energy * fuel_cost * 0.25

co2 = annual_energy * 0.82 / 1000

project_cost = area * 14000

if annual_savings > 0:
    payback = project_cost / annual_savings
else:
    payback = 0

# =========================================================
# PUMP & PIPE SELECTION
# =========================================================

if flow_lpm < 25:
    pump = "1 HP"
    pipe = "DN25"

elif flow_lpm < 50:
    pump = "2 HP"
    pipe = "DN40"

else:
    pump = "5 HP"
    pipe = "DN50"

# =========================================================
# KPI SECTION
# =========================================================

st.markdown('<div class="section-title">📊 Engineering Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">THERMAL LOAD</div>
        <div class="metric-value">{energy:.1f} kWh/day</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">SOLAR MODULES</div>
        <div class="metric-value">{modules}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">COLLECTOR AREA</div>
        <div class="metric-value">{area:.1f} m²</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">FLOW RATE</div>
        <div class="metric-value">{flow_lpm:.1f} LPM</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SECOND ROW
# =========================================================

c5, c6, c7, c8 = st.columns(4)

with c5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">STORAGE TANK</div>
        <div class="metric-value">{storage_tank_capacity:.0f} L</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">SYSTEM EFFICIENCY</div>
        <div class="metric-value">{efficiency:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c7:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PUMP SELECTION</div>
        <div class="metric-value">{pump}</div>
    </div>
    """, unsafe_allow_html=True)

with c8:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PIPE SIZE</div>
        <div class="metric-value">{pipe}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FINANCIAL SECTION
# =========================================================

st.markdown('<div class="section-title">💰 Financial Analysis</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.metric("Project Cost", f"₹ {project_cost:,.0f}")

with f2:
    st.metric("Annual Savings", f"₹ {annual_savings:,.0f}")

with f3:
    st.metric("Payback", f"{payback:.1f} Years")

with f4:
    st.metric("CO₂ Reduction", f"{co2:.1f} Tons/Yr")

# =========================================================
# EFFICIENCY GAUGE
# =========================================================

st.markdown('<div class="section-title">🎯 Collector Efficiency Gauge</div>', unsafe_allow_html=True)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=efficiency,
    title={'text': "Collector Efficiency %"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#0f52ba"},
        'steps': [
            {'range': [0, 40], 'color': "#ffcccc"},
            {'range': [40, 70], 'color': "#fff2cc"},
            {'range': [70, 100], 'color': "#d9ead3"}
        ]
    }
))

fig_gauge.update_layout(height=350)

st.plotly_chart(fig_gauge, use_container_width=True)

# =========================================================
# SOLAR RADIATION GRAPH
# =========================================================

st.markdown('<div class="section-title">☀️ Solar Radiation Analysis</div>', unsafe_allow_html=True)

months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

radiation = [
    650, 720, 850, 920,
    980, 860, 720, 690,
    810, 850, 760, 680
]

fig_rad = go.Figure()

fig_rad.add_trace(go.Bar(
    x=months,
    y=radiation,
    marker_color="#f4a261"
))

fig_rad.update_layout(
    title="Monthly Solar Radiation",
    xaxis_title="Month",
    yaxis_title="Solar Radiation (W/m²)",
    height=400
)

st.plotly_chart(fig_rad, use_container_width=True)

# =========================================================
# EFFICIENCY CURVE
# =========================================================

st.markdown('<div class="section-title">📈 Efficiency Curve</div>', unsafe_allow_html=True)

x = np.linspace(0, 100, 50)

y = 82 - (0.35 * x)

fig_eff = go.Figure()

fig_eff.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines',
    line=dict(color="#0f52ba", width=4),
    name="Efficiency"
))

fig_eff.update_layout(
    title="Collector Efficiency Trend",
    xaxis_title="Operating Parameter",
    yaxis_title="Efficiency %",
    height=400
)

st.plotly_chart(fig_eff, use_container_width=True)

# =========================================================
# INDUSTRIAL P&ID
# =========================================================

st.markdown('<div class="section-title">🏭 Industrial P&ID Diagram</div>', unsafe_allow_html=True)

process_map = {
    "Dairy Plant": "Pasteurizer",
    "Textile Industry": "Dyeing Machine",
    "Pharmaceutical": "Reactor",
    "Chemical Plant": "Chemical Tank",
    "Food Processing": "Food Heater"
}

process_name = process_map[industry_type]

pid = f"""
digraph G {{

rankdir=LR;
splines=ortho;

node [
shape=box
style=filled
fillcolor="#d9edf7"
fontname=Arial
];

Tank [
label="Storage Tank\\n{storage_tank_capacity:.0f} L"
shape=cylinder
fillcolor="#ffe599"
];

Pump [
label="Pump\\n{pump}"
shape=circle
fillcolor="#b6d7a8"
];

Collector [
label="Solar Collector\\n{modules} Modules"
fillcolor="#f4cccc"
];

Boiler [
label="Boiler\\n{fuel_type}"
fillcolor="#d9d2e9"
];

HX [
label="Heat Exchanger"
fillcolor="#cfe2f3"
];

Process [
label="{process_name}\\n{tout} °C"
fillcolor="#ead1dc"
];

Tank -> Pump;
Pump -> Collector;
Collector -> HX;
HX -> Process;
Process -> Tank;

Boiler -> HX;

}}
"""

st.graphviz_chart(pid)

# =========================================================
# PROPOSAL SUMMARY TABLE
# =========================================================

st.markdown('<div class="section-title">📋 Proposal Summary</div>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Parameter": [
        "Industry",
        "Water Requirement",
        "Outlet Temperature",
        "Inlet Temperature",
        "Thermal Load",
        "Solar Modules",
        "Collector Area",
        "Tank Capacity",
        "Flow Rate",
        "Pump",
        "Pipe Size",
        "Project Cost",
        "Annual Savings",
        "Payback"
    ],

    "Value": [
        industry_type,
        f"{water} LPD",
        f"{tout} °C",
        f"{tin} °C",
        f"{energy:.1f} kWh/day",
        modules,
        f"{area:.1f} m²",
        f"{storage_tank_capacity:.0f} L",
        f"{flow_lpm:.1f} LPM",
        pump,
        pipe,
        f"₹ {project_cost:,.0f}",
        f"₹ {annual_savings:,.0f}",
        f"{payback:.1f} Years"
    ]
})

st.dataframe(df, use_container_width=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.success("✅ Industrial Solar Water Heating Proposal Generated Successfully")
