import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Industrial Solar Thermal Analyzer",
    layout="wide"
)

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

.main{
    background:#f4f6f9;
}

.title{
    font-size:42px;
    font-weight:bold;
    color:#0f52ba;
}

.card{
    background:white;
    padding:18px;
    border-radius:12px;
    text-align:center;
    box-shadow:0px 2px 8px rgba(0,0,0,0.1);
    border-top:5px solid #0f52ba;
}

.metric{
    font-size:30px;
    font-weight:bold;
    color:#111;
}

.label{
    font-size:14px;
    color:gray;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# TITLE
# ======================================================

st.markdown(
    '<div class="title">☀️ Industrial Solar Water Heating System</div>',
    unsafe_allow_html=True
)

st.markdown("### Real Time Solar Thermal Proposal Dashboard")

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("⚙️ Input Parameters")

industry = st.sidebar.selectbox(
    "Select Industry",
    [
        "Dairy Plant",
        "Textile Industry",
        "Pharmaceutical Plant",
        "Chemical Industry",
        "Hotel"
    ]
)

flow = st.sidebar.slider(
    "Flow Rate (LPH)",
    100,
    400,
    200,
    50
)

tin = st.sidebar.number_input(
    "Cold Water Temperature (°C)",
    value=25
)

tout = st.sidebar.number_input(
    "Hot Water Temperature (°C)",
    value=80
)

ambient = st.sidebar.number_input(
    "Ambient Temperature (°C)",
    value=30
)

solar_radiation = st.sidebar.slider(
    "Solar Radiation (W/m²)",
    400,
    1200,
    800,
    50
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost ₹",
    value=85
)

# ======================================================
# CALCULATIONS
# ======================================================

cp = 4.186

dt = tout - tin

energy = (flow * cp * dt) / 3600

efficiency = (
    0.75 - ((tout - ambient)/1000)
)

efficiency = max(
    0.35,
    min(efficiency,0.75)
)

collector_area = energy / (
    (solar_radiation/1000) * efficiency
)

modules = round(
    collector_area / 7.2
)

tank = flow * 1.2

annual_savings = energy * 300 * fuel_cost

payback = (
    collector_area * 14000
) / annual_savings

co2 = energy * 300 * 0.82 / 1000

# ======================================================
# PUMP
# ======================================================

if flow <= 150:
    pump = "1 HP"
    pipe = "DN25"

elif flow <= 250:
    pump = "2 HP"
    pipe = "DN32"

else:
    pump = "3 HP"
    pipe = "DN40"

# ======================================================
# KPI
# ======================================================

st.markdown("---")

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
    <div class="label">THERMAL ENERGY</div>
    <div class="metric">{energy:.1f}</div>
    kWh/day
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
    <div class="label">COLLECTOR AREA</div>
    <div class="metric">{collector_area:.1f}</div>
    m²
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
    <div class="label">SOLAR MODULES</div>
    <div class="metric">{modules}</div>
    Units
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
    <div class="label">STORAGE TANK</div>
    <div class="metric">{tank:.0f}</div>
    Liters
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# SECOND ROW
# ======================================================

c5,c6,c7,c8 = st.columns(4)

with c5:
    st.markdown(f"""
    <div class="card">
    <div class="label">EFFICIENCY</div>
    <div class="metric">{efficiency*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="card">
    <div class="label">PUMP</div>
    <div class="metric">{pump}</div>
    </div>
    """, unsafe_allow_html=True)

with c7:
    st.markdown(f"""
    <div class="card">
    <div class="label">PAYBACK</div>
    <div class="metric">{payback:.1f}</div>
    Years
    </div>
    """, unsafe_allow_html=True)

with c8:
    st.markdown(f"""
    <div class="card">
    <div class="label">CO₂ SAVED</div>
    <div class="metric">{co2:.1f}</div>
    Tons/year
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# GAUGE
# ======================================================

st.markdown("---")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=efficiency*100,
    title={'text':"Collector Efficiency"},
    gauge={
        'axis':{'range':[0,100]},
        'bar':{'color':"green"}
    }
))

st.plotly_chart(fig,use_container_width=True)

# ======================================================
# SOLAR RADIATION GRAPH
# ======================================================

st.markdown("---")

months = [
    "Jan","Feb","Mar","Apr",
    "May","Jun","Jul","Aug",
    "Sep","Oct","Nov","Dec"
]

radiation = [
    650,720,850,980,
    1100,950,780,760,
    820,900,700,620
]

df = pd.DataFrame({
    "Month":months,
    "Radiation":radiation
})

fig2 = px.line(
    df,
    x="Month",
    y="Radiation",
    markers=True,
    title="Monthly Solar Radiation"
)

fig2.update_layout(
    yaxis_title="Solar Radiation (W/m²)",
    xaxis_title="Month"
)

st.plotly_chart(fig2,use_container_width=True)

# ======================================================
# INDUSTRIAL P&ID
# ======================================================

# =========================================================
# INDUSTRIAL P&ID DIAGRAM
# =========================================================

st.markdown("## 🏭 Industrial Process P&ID")

industry_process = {
    "Dairy Plant (Pasteurization/CIP)": "Pasteurizer",
    "Textile Dyeing Mills": "Dyeing Tank",
    "Pharmaceutical Synthesis": "Reactor",
    "Thermal Power Pre-Heating": "Feed Water",
    "Chemical Processing Tank": "Chemical Tank"
}

process_name = industry_process[industry_type]

pid_code = f"""
digraph G {{

    graph [pad="0.5", nodesep="0.8", ranksep="1"]
    rankdir=LR;
    splines=ortho;
    bgcolor="white";

    node [
        shape=box,
        style="filled",
        color="black",
        fillcolor="#d9edf7",
        fontname="Arial",
        fontsize=12
    ];

    edge [
        color="black",
        penwidth=2,
        arrowsize=1
    ];

    Tank [
        label="STORAGE TANK\\nCapacity = {storage_tank_capacity:.0f} L"
        shape=cylinder
        fillcolor="#ffe599"
    ];

    Pump [
        label="PUMP\\n{pump_hp}"
        shape=circle
        fillcolor="#b6d7a8"
    ];

    Collector [
        label="SOLAR COLLECTOR FIELD\\n{modules} Modules"
        shape=box
        fillcolor="#f4cccc"
    ];

    Boiler [
        label="AUX BOILER\\n{aux_fuel_type}"
        shape=box
        fillcolor="#d9d2e9"
    ];

    HX [
        label="HEAT EXCHANGER"
        shape=box
        fillcolor="#cfe2f3"
    ];

    Process [
        label="{process_name}\\nProcess Temp = {tout} C"
        shape=box
        fillcolor="#ead1dc"
    ];

    Valve1 [
        label="CV"
        shape=diamond
        fillcolor="#ffffff"
    ];

    Valve2 [
        label="CV"
        shape=diamond
        fillcolor="#ffffff"
    ];

    FT [
        label="FT"
        shape=circle
        fillcolor="#fff2cc"
    ];

    TT [
        label="TT"
        shape=circle
        fillcolor="#fff2cc"
    ];

    PI [
        label="PI"
        shape=circle
        fillcolor="#fff2cc"
    ];

    Tank -> Pump;
    Pump -> FT;
    FT -> Collector;
    Collector -> TT;
    TT -> HX;
    HX -> Valve1;
    Valve1 -> Process;

    Process -> Valve2;
    Valve2 -> Tank;

    HX -> Boiler;
    Boiler -> HX;

    Collector -> PI;

}}
"""

st.graphviz_chart(pid_code)

# ======================================================
# SUMMARY
# ======================================================

st.markdown("---")

summary = pd.DataFrame({

    "Parameter":[
        "Industry",
        "Flow Rate",
        "Collector Area",
        "Modules",
        "Pump",
        "Pipe",
        "Efficiency"
    ],

    "Value":[
        industry,
        f"{flow} LPH",
        f"{collector_area:.1f} m²",
        modules,
        pump,
        pipe,
        f"{efficiency*100:.1f}%"
    ]
})

st.dataframe(
    summary,
    use_container_width=True
)