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

st.markdown("---")

st.subheader("🏭 Industrial Process P&ID")

color = "#2196f3"

if industry == "Textile Industry":
    color = "#9c27b0"

elif industry == "Pharmaceutical Plant":
    color = "#009688"

elif industry == "Chemical Industry":
    color = "#e53935"

elif industry == "Hotel":
    color = "#ff9800"

pid = f"""
<svg width="1000" height="350">

<rect x="40" y="120" width="170" height="70"
fill="#b3d9ea"
stroke="black"
stroke-width="2"/>
<text x="70" y="160"
font-size="22">
Storage Tank
</text>

<circle cx="320" cy="150"
r="35"
fill="#d4edda"
stroke="black"
stroke-width="2"/>
<text x="295" y="155"
font-size="18">
Pump
</text>

<rect x="430" y="105"
width="220"
height="90"
fill="#ffe082"
stroke="black"
stroke-width="2"/>
<text x="470" y="155"
font-size="24">
Solar Collector
</text>

<rect x="760" y="120"
width="180"
height="70"
fill="{color}"
stroke="black"
stroke-width="2"/>
<text x="790" y="160"
font-size="22"
fill="white">
Process Load
</text>

<rect x="430" y="250"
width="180"
height="60"
fill="#ffccbc"
stroke="black"
stroke-width="2"/>
<text x="470" y="287"
font-size="22">
Boiler
</text>

<line x1="210" y1="150"
x2="285" y2="150"
stroke="black"
stroke-width="4"/>

<polygon points="285,150 270,142 270,158"
fill="black"/>

<line x1="355" y1="150"
x2="430" y2="150"
stroke="black"
stroke-width="4"/>

<polygon points="430,150 415,142 415,158"
fill="black"/>

<line x1="650" y1="150"
x2="760" y2="150"
stroke="black"
stroke-width="4"/>

<polygon points="760,150 745,142 745,158"
fill="black"/>

<line x1="850" y1="190"
x2="850" y2="280"
stroke="red"
stroke-width="4"/>

<line x1="850" y1="280"
x2="610" y2="280"
stroke="red"
stroke-width="4"/>

<polygon points="610,280 625,272 625,288"
fill="red"/>

<line x1="430" y1="280"
x2="200" y2="280"
stroke="red"
stroke-width="4"/>

<line x1="200" y1="280"
x2="200" y2="190"
stroke="red"
stroke-width="4"/>

<line x1="200" y1="190"
x2="120" y2="190"
stroke="red"
stroke-width="4"/>

</svg>
"""

st.markdown(
    pid,
    unsafe_allow_html=True
)

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