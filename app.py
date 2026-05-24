import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# =========================================================
# 1. PAGE CONFIG & THEMING
# =========================================================

st.set_page_config(
    page_title="SQS Solar SHIP Dashboard",
    layout="wide"
)

# Custom Premium CSS Styling for Enterprise look
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
    border-radius: 10px;
    border-left: 5px solid #0f52ba;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
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
# 2. TITLE
# =========================================================

st.title("☀️ SQS Solar Water Heating Design Proposal")
st.markdown("---")

# =========================================================
# 3. SIDEBAR INTERFACE (SYSTEM INPUTS)
# =========================================================

st.sidebar.header("⚙️ System Inputs")

industry_type = st.sidebar.selectbox(
    "Select Industry",
    ["Dairy Plant", "Textile Industry", "Pharmaceutical", "Chemical Plant", "Food Processing"]
)

water = st.sidebar.number_input(
    "Daily Hot Water Requirement (LPD)",
    min_value=100,
    value=5000,
    step=100
)

tout = st.sidebar.number_input(
    "Required Output Temperature (°C)",
    min_value=30,
    max_value=120,
    value=80
)

tin = st.sidebar.number_input(
    "Cold Water Inlet Temperature (°C)",
    min_value=1,
    max_value=70,
    value=25
)

ambient_temp = st.sidebar.slider(
    "Ambient Temperature (°C)",
    10,
    45,
    30
)

wind_speed = st.sidebar.slider(
    "Wind Speed (m/s)",
    0.0,
    10.0,
    2.0
)

fuel_type = st.sidebar.selectbox(
    "Backup Fuel Type",
    ["Diesel", "Natural Gas", "Electric Heater"]
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost (₹)",
    value=85
)

# =========================================================
# 4. ENGINEERING CONSTANTS & MULTIPLIERS
# =========================================================

cp = 4.186
module_area = 7.2
module_output = 22
safety_factor = 1.15

# =========================================================
# 5. ADVANCED CALCULATIONS CORE
# =========================================================

dt = tout - tin
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
payback = project_cost / annual_savings if annual_savings > 0 else 0

# =========================================================
# 6. HYDRAULIC PIPING & PUMP MATRIX DEFINITIONS
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
# 7. ENGINEERING KPI SECTION
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

# SECOND ROW KPI
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
# 8. FINANCIAL SECTION
# =========================================================

st.markdown('<div class="section-title">💰 Financial Analysis</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PROJECT COST</div>
        <div class="metric-value">₹ {project_cost:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">ANNUAL SAVINGS</div>
        <div class="metric-value">₹ {annual_savings:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PAYBACK</div>
        <div class="metric-value">{payback:.1f} Years</div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">CO₂ REDUCTION</div>
        <div class="metric-value">{co2:.1f} Tons/Yr</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 9. CHARTS VISUALIZATIONS SECTION
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

# SOLAR RADIATION GRAPH
st.markdown('<div class="section-title">☀️ Solar Radiation Analysis</div>', unsafe_allow_html=True)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
radiation = [650, 720, 850, 920, 980, 860, 720, 690, 810, 850, 760, 680]

fig_rad = go.Figure()
fig_rad.add_trace(go.Bar(x=months, y=radiation, marker_color="#f4a261"))
fig_rad.update_layout(
    title="Monthly Solar Radiation",
    xaxis_title="Month",
    yaxis_title="Solar Radiation (W/m²)",
    height=400
)
st.plotly_chart(fig_rad, use_container_width=True)

# EFFICIENCY CURVE TREND
st.markdown('<div class="section-title">📈 Efficiency Curve</div>', unsafe_allow_html=True)

x_space = np.linspace(0, 100, 50)
y_space = 82 - (0.35 * x_space)

fig_eff = go.Figure()
fig_eff.add_trace(go.Scatter(x=x_space, y=y_space, mode='lines', line=dict(color="#0f52ba", width=4), name="Efficiency"))
fig_eff.update_layout(
    title="Collector Efficiency Trend",
    xaxis_title="Operating Parameter",
    yaxis_title="Efficiency %",
    height=400
)
st.plotly_chart(fig_eff, use_container_width=True)

# =========================================================
# 10. INDUSTRIAL ISA-5.1 COMPLIANT P&ID DIAGRAM
# =========================================================

st.markdown('<div class="section-title">🏭 Industrial P&ID Diagram</div>', unsafe_allow_html=True)

process_map = {
    "Dairy Plant": "Pasteurizer Unit",
    "Textile Industry": "Dyeing Jet Vats",
    "Pharmaceutical": "Sanitary Reactor Jacket",
    "Chemical Plant": "Process Preheating Vat",
    "Food Processing": "Batch Cooker Retort"
}
process_name = process_map[industry_type]

# Double backslashes (\\n) handle string interpolation boundaries gracefully for Graphviz compilers
pid = f"""
digraph G {{
    rankdir=LR;
    nodesep=0.6;
    ranksep=0.7;
    
    edge [fontname="Arial", fontsize=9, color="#2c3e50", penwidth=1.5, arrowhead=normal, arrowsize=0.8];
    node [fontname="Arial", fontsize=10, shape=box, style="filled,bold", fillcolor="#ffffff", color="#2c3e50", penwidth=1.5];

    Tank [
        label="TK-101\\nThermal Buffer Tank\\n{storage_tank_capacity:.0f} L"
        shape=cylinder
        fillcolor="#fff9db"
        color="#f59f00"
        height=1.4
        width=1.0
    ];

    Pump [
        label="P-101A\\nLoop Pump\\n{pump}"
        shape=circle
        fillcolor="#e2f0d9"
        color="#385723"
        fixedsize=true
        width=1.1
    ];

    Collector [
        label="⚡\\nSOLAR FIELD ARRAY\\n{modules} Manifold Modules\\n({area:.1f} m²)"
        shape=box3d
        fillcolor="#fce8e6"
        color="#c00000"
        margin="0.2,0.1"
    ];

    Boiler [
        label="BLR-01\\nAuxiliary Boiler\\n({fuel_type})"
        shape=component
        fillcolor="#f3f0ff"
        color="#7048e8"
        height=1.2
    ];

    HX [
        label="HX-101\\nPlate Heat Exchanger"
        shape=diamond
        fillcolor="#e6f4ea"
        color="#137333"
        fixedsize=true
        width=1.3
        height=1.3
    ];

    Process [
        label="🏭\\nPROCESS END-USE\\n{process_name}\\nTarget: {tout}°C"
        shape=house
        fillcolor="#fbf1f5"
        color="#d0146f"
        margin="0.2,0.1"
    ];

    Tank:s -> Pump:w [label=" Suction Line", weight=2];
    Pump:e -> Collector:w [label=" Cold Feed\\n {flow_lpm:.1f} LPM"];
    Collector:e -> HX:n [label=" Hot Glycol\\n Return"];
    
    HX:s -> Tank:n [label=" Secondary Thermal\\n Charge Loop", color="#1c7ed6", penwidth=2.0];
    
    Tank:e -> Process:w [label=" Hot Water Supply\\n Delivery", color="#e03131", penwidth=2.0];
    Boiler:e -> HX:w [label=" High-Temp\\n Top-up Request", style=dashed, color="#7048e8"];
    HX:e -> Boiler:s [label=" Return", style=dashed, color="#7048e8"];
    
    Process:s -> Tank:w [label=" Low-Temp Residual\\n Recirculation Return", color="#748ffc"];
}}
"""

with st.container():
    st.graphviz_chart(pid, use_container_width=True)

# =========================================================
# 11. PROPOSAL SUMMARY TABLE MATRIX
# =========================================================

st.markdown('<div class="section-title">📋 Proposal Summary</div>', unsafe_allow_html=True)

df_summary = pd.DataFrame({
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
        str(modules),
        f"{area:.1f} m²",
        f"{storage_tank_capacity:.0f} L",
        f"{flow_lpm:.1f} LPM",
        str(pump),
        str(pipe),
        f"₹ {project_cost:,.0f}",
        f"₹ {annual_savings:,.0f}",
        f"{payback:.1f} Years"
    ]
})

st.dataframe(df_summary, use_container_width=True, hide_index=True)

# =========================================================
# FOOTER COMPLIANCE ALERT
# =========================================================

st.markdown("---")
st.success("✅ Industrial Solar Water Heating Proposal Generated Successfully")
