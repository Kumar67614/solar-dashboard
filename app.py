import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="SQS Solar Water Heating Design Engine",
    page_icon="☀️",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

h1, h2, h3 {
    color: #0E4D92;
}

div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    border-left: 5px solid #0E4D92;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("☀️ SQS Solar Water Heating Design Engine")
st.markdown("---")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("Customer Inputs")

water = st.sidebar.number_input(
    "Daily Water Requirement (LPD)",
    min_value=100,
    value=5000,
    step=100
)

tout = st.sidebar.number_input(
    "Target Output Temperature (°C)",
    min_value=30,
    max_value=100,
    value=60
)

tin = st.sidebar.number_input(
    "Cold Water Temperature (°C)",
    min_value=0,
    max_value=40,
    value=25
)

psh = st.sidebar.slider(
    "Peak Sun Hours",
    1.0,
    10.0,
    5.5
)

st.sidebar.markdown("---")

# ---------------------------------------------------
# CONSTANTS
# ---------------------------------------------------

cp = 4.186
module_energy = 22
module_area = 7.2
flow_per_row = 250
safety_factor = 1.15

# ---------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------

dt = tout - tin

energy = (water * cp * dt) / 3600

modules = round((energy * safety_factor) / module_energy)

area = modules * module_area

rows = round(modules / 2)

flow_kg = rows * flow_per_row

flow_lpm = flow_kg / 60

tank = water

annual_savings = energy * 365 * 10

co2 = energy * 365 * 0.82

efficiency = (energy / (modules * module_energy)) * 100

solar_fraction = min((efficiency / 100) * 100, 100)

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

st.subheader("📊 System KPIs")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Thermal Energy",
    f"{energy:.1f} kWh/day"
)

c2.metric(
    "SQS Modules",
    modules
)

c3.metric(
    "Aperture Area",
    f"{area:.1f} m²"
)

c4.metric(
    "Flow Rate",
    f"{flow_lpm:.1f} LPM"
)

c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Hydraulic Rows",
    rows
)

c6.metric(
    "Storage Tank",
    f"{tank:,.0f} L"
)

c7.metric(
    "Annual Savings",
    f"₹ {annual_savings:,.0f}"
)

c8.metric(
    "CO₂ Reduction",
    f"{co2:,.0f} kg/year"
)

st.markdown("---")

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "System Performance",
    "Monthly Analysis",
    "Pump & Pipe Sizing",
    "Engineering Summary"
])

# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------

with tab1:

    st.subheader("⚡ System Efficiency")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=efficiency,
        title={'text': "Collector Efficiency (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "lightgreen"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("☀️ Solar Fraction")

    st.progress(int(solar_fraction))

    st.write(f"Solar Fraction = {solar_fraction:.1f}%")

# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------

with tab2:

    st.subheader("📈 Monthly Thermal Energy Analysis")

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    monthly_energy = [
        energy*0.90,
        energy*0.92,
        energy*0.98,
        energy*1.05,
        energy*1.10,
        energy*1.15,
        energy*1.12,
        energy*1.08,
        energy*1.02,
        energy*0.97,
        energy*0.92,
        energy*0.88
    ]

    df = pd.DataFrame({
        "Month": months,
        "Energy": monthly_energy
    })

    chart = px.line(
        df,
        x="Month",
        y="Energy",
        markers=True
    )

    st.plotly_chart(chart, use_container_width=True)

# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------

with tab3:

    st.subheader("🔧 Pump Recommendation")

    if flow_lpm < 20:
        pump = "1 HP Centrifugal Pump"
    elif flow_lpm < 40:
        pump = "2 HP Centrifugal Pump"
    elif flow_lpm < 80:
        pump = "3 HP Centrifugal Pump"
    else:
        pump = "5 HP Industrial Pump"

    st.success(pump)

    st.subheader("🚰 Recommended Pipe Size")

    if flow_lpm < 20:
        pipe = "1 inch Pipe"
    elif flow_lpm < 40:
        pipe = "1.5 inch Pipe"
    elif flow_lpm < 80:
        pipe = "2 inch Pipe"
    else:
        pipe = "3 inch Pipe"

    st.info(pipe)

# ---------------------------------------------------
# TAB 4
# ---------------------------------------------------

with tab4:

    st.subheader("📑 Engineering Summary")

    summary = pd.DataFrame({
        "Parameter": [
            "Daily Water Requirement",
            "Output Temperature",
            "Temperature Lift",
            "Thermal Energy",
            "SQS Modules",
            "Aperture Area",
            "Flow Rate",
            "Storage Tank",
            "Solar Fraction"
        ],

        "Value": [
            f"{water} LPD",
            f"{tout} °C",
            f"{dt} °C",
            f"{energy:.1f} kWh/day",
            modules,
            f"{area:.1f} m²",
            f"{flow_lpm:.1f} LPM",
            f"{tank} Liters",
            f"{solar_fraction:.1f}%"
        ]
    })

    st.dataframe(summary, use_container_width=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <center>
    <b>SQS Solar Thermal Engineering Dashboard</b><br>
    Developed using Streamlit & Plotly
    </center>
    """,
    unsafe_allow_html=True
)