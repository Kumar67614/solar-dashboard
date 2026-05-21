import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Solar Dashboard", layout="wide")

st.title("SQS Solar Water Heating Design Engine")

# SIDEBAR INPUTS
st.sidebar.header("Customer Inputs")

water = st.sidebar.number_input(
    "Water Requirement (LPD)",
    value=5000
)

tout = st.sidebar.number_input(
    "Output Temperature (°C)",
    value=80
)

tin = st.sidebar.number_input(
    "Cold Water Temperature (°C)",
    value=25
)

# CONSTANTS
cp = 4.186
safety = 1.15
module_energy = 22
module_area = 7.2

# CALCULATIONS
dt = tout - tin

energy = (water * cp * dt)/3600

modules = round((energy * safety)/module_energy)

area = modules * module_area

flow = ((modules/2)*250)/60

annual = energy * 365 * 10

co2 = energy * 365 * 0.82

efficiency = (energy/(modules*module_energy))*100

# KPI CARDS
c1,c2,c3,c4 = st.columns(4)

c1.metric("Thermal Energy", f"{energy:.1f} kWh/day")
c2.metric("Modules", modules)
c3.metric("Area", f"{area:.1f} m²")
c4.metric("Flow", f"{flow:.1f} LPM")

# SECOND ROW
c5,c6 = st.columns(2)

c5.metric("Annual Savings", f"₹ {annual:,.0f}")
c6.metric("CO₂ Reduction", f"{co2:,.0f} kg/year")

# GAUGE
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=efficiency,
    title={'text':"Efficiency"},
    gauge={
        'axis':{'range':[0,100]}
    }
))

st.plotly_chart(fig, use_container_width=True)

# PUMP
if flow < 20:
    pump = "1 HP Pump"
elif flow < 40:
    pump = "2 HP Pump"
else:
    pump = "3 HP Pump"

st.subheader("Pump Recommendation")
st.success(pump)