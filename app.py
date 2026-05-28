# ============================================================
# UNIVERSAL INDUSTRIAL SOLAR THERMAL PROPOSAL ENGINE
# FULLY GENERALIZED STREAMLIT APPLICATION
# READY FOR GITHUB UPLOAD AS app.py
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from dataclasses import dataclass

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Universal Solar Thermal Proposal Engine", layout="wide")

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class CollectorParams:
    name: str
    collector_type: str
    aperture_area: float
    gross_area: float
    width: float
    height: float
    eta0: float
    a1: float
    a2: float
    rated_flow_per_collector: float
    tilt_angle: float


@dataclass
class ProcessRequirements:
    daily_volume_lpd: float
    inlet_temp_c: float
    outlet_temp_c: float
    ambient_temp_c: float
    operating_hours: float


# ============================================================
# THERMAL ENGINE
# ============================================================

CP_WATER = 4186


def solve_hwb(
    collector,
    inlet_temp,
    ambient_temp,
    irradiance,
    flow_lph,
):

    if irradiance <= 0:
        return {
            "efficiency": 0,
            "delta_t": 0,
            "outlet_temp": inlet_temp,
            "useful_heat": 0,
        }

    mass_flow = (flow_lph / 3600) * 1000 / 1000

    tm = inlet_temp + 5

    for _ in range(20):

        x = (tm - ambient_temp) / irradiance

        eta = (
            collector.eta0
            - collector.a1 * x
            - collector.a2 * (x ** 2) * irradiance
        )

        eta = max(0, min(eta, collector.eta0))

        useful_heat = eta * irradiance * collector.aperture_area

        if mass_flow > 0:
            delta_t = useful_heat / (mass_flow * CP_WATER)
        else:
            delta_t = 0

        tm_new = inlet_temp + delta_t / 2

        if abs(tm_new - tm) < 0.01:
            tm = tm_new
            break

        tm = tm_new

    return {
        "efficiency": eta * 100,
        "delta_t": delta_t,
        "outlet_temp": inlet_temp + delta_t,
        "useful_heat": useful_heat,
    }


# ============================================================
# LOAD CALCULATION
# ============================================================


def calculate_load(process):

    dt = process.outlet_temp_c - process.inlet_temp_c

    daily_energy_kwh = (
        process.daily_volume_lpd * CP_WATER * dt
    ) / 3600000

    return daily_energy_kwh


# ============================================================
# COLLECTOR FIELD SIZING
# ============================================================


def size_collector_field(process, collector, irradiance, peak_sun_hours):

    thermal_load = calculate_load(process)

    single_result = solve_hwb(
        collector,
        process.inlet_temp_c,
        process.ambient_temp_c,
        irradiance,
        collector.rated_flow_per_collector,
    )

    single_daily_output = (
        single_result["useful_heat"] / 1000
    ) * peak_sun_hours

    if single_daily_output <= 0:
        single_daily_output = 0.1

    collectors = math.ceil(thermal_load / single_daily_output)

    total_aperture_area = collectors * collector.aperture_area
    total_gross_area = collectors * collector.gross_area

    return {
        "thermal_load": thermal_load,
        "collectors": collectors,
        "total_aperture_area": total_aperture_area,
        "total_gross_area": total_gross_area,
        "single_output": single_daily_output,
    }


# ============================================================
# LAYOUT ENGINE
# ============================================================


def calculate_spacing(height, tilt, latitude):

    winter_altitude = 90 - abs(latitude + 23.45)

    winter_altitude = max(10, winter_altitude)

    shadow = (
        height * math.cos(math.radians(tilt))
        + (
            height * math.sin(math.radians(tilt))
        )
        / math.tan(math.radians(winter_altitude))
    )

    pitch = shadow + 0.8

    return {
        "winter_altitude": winter_altitude,
        "shadow": shadow,
        "pitch": pitch,
    }


# ============================================================
# FINANCIAL ENGINE
# ============================================================


def financial_analysis(total_area, thermal_load, fuel_cost):

    project_cost = total_area * 12000

    annual_energy = thermal_load * 300

    annual_savings = annual_energy * fuel_cost * 0.25

    payback = project_cost / annual_savings if annual_savings > 0 else 0

    co2 = annual_energy * 0.82 / 1000

    return {
        "project_cost": project_cost,
        "annual_savings": annual_savings,
        "payback": payback,
        "co2": co2,
    }


# ============================================================
# SIDEBAR INPUTS
# ============================================================

st.sidebar.title("Solar System Inputs")

industry = st.sidebar.selectbox(
    "Industry",
    [
        "Dairy",
        "Textile",
        "Pharmaceutical",
        "Food",
        "Chemical",
    ],
)

water = st.sidebar.number_input(
    "Daily Hot Water Requirement (LPD)",
    value=5000,
)

inlet_temp = st.sidebar.number_input(
    "Inlet Temperature °C",
    value=25,
)

outlet_temp = st.sidebar.number_input(
    "Outlet Temperature °C",
    value=80,
)

ambient_temp = st.sidebar.number_input(
    "Ambient Temperature °C",
    value=30,
)

irradiance = st.sidebar.slider(
    "Solar Irradiance W/m²",
    200,
    1200,
    800,
)

peak_sun_hours = st.sidebar.slider(
    "Peak Sun Hours",
    1.0,
    10.0,
    5.5,
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost ₹",
    value=90,
)

latitude = st.sidebar.number_input(
    "Site Latitude",
    value=19.1,
)

st.sidebar.markdown("---")
st.sidebar.subheader("Collector Parameters")

collector = CollectorParams(
    name=st.sidebar.text_input("Collector Name", "Custom FPC"),
    collector_type=st.sidebar.selectbox(
        "Collector Type",
        ["Flat Plate", "ETC", "Thermosiphon"],
    ),
    aperture_area=st.sidebar.number_input(
        "Aperture Area m²",
        value=2.0,
    ),
    gross_area=st.sidebar.number_input(
        "Gross Area m²",
        value=2.2,
    ),
    width=st.sidebar.number_input(
        "Collector Width m",
        value=1.0,
    ),
    height=st.sidebar.number_input(
        "Collector Height m",
        value=2.0,
    ),
    eta0=st.sidebar.number_input(
        "η0",
        value=0.78,
    ),
    a1=st.sidebar.number_input(
        "a1",
        value=3.5,
    ),
    a2=st.sidebar.number_input(
        "a2",
        value=0.015,
    ),
    rated_flow_per_collector=st.sidebar.number_input(
        "Flow per Collector LPH",
        value=50.0,
    ),
    tilt_angle=st.sidebar.number_input(
        "Tilt Angle",
        value=25.0,
    ),
)

process = ProcessRequirements(
    daily_volume_lpd=water,
    inlet_temp_c=inlet_temp,
    outlet_temp_c=outlet_temp,
    ambient_temp_c=ambient_temp,
    operating_hours=8,
)

# ============================================================
# CALCULATIONS
# ============================================================

field = size_collector_field(
    process,
    collector,
    irradiance,
    peak_sun_hours,
)

spacing = calculate_spacing(
    collector.height,
    collector.tilt_angle,
    latitude,
)

finance = financial_analysis(
    field["total_gross_area"],
    field["thermal_load"],
    fuel_cost,
)

flow_total = (
    field["collectors"]
    * collector.rated_flow_per_collector
)

# ============================================================
# TITLE
# ============================================================

st.title("☀ Universal Solar Thermal Proposal Engine")

# ============================================================
# KPI SECTION
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Thermal Load",
    f"{field['thermal_load']:.1f} kWh/day",
)

c2.metric(
    "Collectors",
    field["collectors"],
)

c3.metric(
    "Aperture Area",
    f"{field['total_aperture_area']:.1f} m²",
)

c4.metric(
    "Flow Rate",
    f"{flow_total:.1f} LPH",
)

# ============================================================
# SECOND ROW
# ============================================================

c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Gross Area",
    f"{field['total_gross_area']:.1f} m²",
)

c6.metric(
    "Row Pitch",
    f"{spacing['pitch']:.2f} m",
)

c7.metric(
    "Project Cost",
    f"₹ {finance['project_cost']:,.0f}",
)

c8.metric(
    "Payback",
    f"{finance['payback']:.1f} Years",
)

# ============================================================
# PERFORMANCE GRAPH
# ============================================================

st.subheader("Collector Efficiency Curve")

x = np.linspace(0, 0.25, 100)

y = (
    collector.eta0
    - collector.a1 * x
    - collector.a2 * (x ** 2) * irradiance
) * 100

y = np.clip(y, 0, 100)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="lines",
        name="Efficiency",
    )
)

fig.update_layout(
    xaxis_title="Reduced Temperature Parameter",
    yaxis_title="Efficiency %",
    height=400,
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# MONTHLY ANALYSIS
# ============================================================

st.subheader("Monthly Solar Yield")

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

monthly_irradiance = [
    700,
    750,
    820,
    850,
    880,
    650,
    520,
    500,
    620,
    700,
    720,
    690,
]

monthly_yield = []

for G in monthly_irradiance:

    r = solve_hwb(
        collector,
        inlet_temp,
        ambient_temp,
        G,
        flow_total,
    )

    monthly_yield.append(
        (
            r["useful_heat"] / 1000
        ) * peak_sun_hours * field["collectors"]
    )

monthly_df = pd.DataFrame(
    {
        "Month": months,
        "Yield": monthly_yield,
    }
)

fig2 = px.bar(
    monthly_df,
    x="Month",
    y="Yield",
    title="Monthly Solar Thermal Output",
)

st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# LAYOUT SECTION
# ============================================================

st.subheader("Solar Field Layout")

collectors_per_row = 5
n_rows = math.ceil(field["collectors"] / collectors_per_row)

layout_text = ""

counter = 1

for r in range(n_rows):

    layout_text += f"Row {r+1}: "

    for _ in range(collectors_per_row):

        if counter <= field["collectors"]:
            layout_text += f"[C{counter}] "
            counter += 1

    layout_text += "\n\n"

st.code(layout_text)

# ============================================================
# P&ID SECTION
# ============================================================

st.subheader("Industrial Integration Diagram")

pid = f"""
digraph G {{
rankdir=LR;

Tank [label="Buffer Tank"];
Pump [label="Solar Pump"];
Collector [label="Solar Collector Field"];
HX [label="Heat Exchanger"];
Boiler [label="Existing Boiler"];
Process [label="{industry} Process"];

Tank -> Pump;
Pump -> Collector;
Collector -> HX;
HX -> Tank;
Tank -> Process;
Boiler -> HX;
}}
"""

st.graphviz_chart(pid)

# ============================================================
# FINANCIAL TABLE
# ============================================================

st.subheader("Financial Summary")

finance_df = pd.DataFrame(
    {
        "Parameter": [
            "Project Cost",
            "Annual Savings",
            "Payback",
            "CO2 Reduction",
        ],
        "Value": [
            f"₹ {finance['project_cost']:,.0f}",
            f"₹ {finance['annual_savings']:,.0f}",
            f"{finance['payback']:.1f} Years",
            f"{finance['co2']:.2f} Tons/year",
        ],
    }
)

st.dataframe(finance_df, use_container_width=True)

# ============================================================
# PROPOSAL SUMMARY
# ============================================================

st.subheader("Engineering Proposal Summary")

st.markdown(f"""
### System Overview

- Industry: {industry}
- Daily Water Requirement: {water} LPD
- Required Temperature: {outlet_temp} °C
- Collector Type: {collector.collector_type}
- Number of Collectors: {field['collectors']}
- Total Aperture Area: {field['total_aperture_area']:.1f} m²
- Total Gross Area: {field['total_gross_area']:.1f} m²
- Estimated Payback: {finance['payback']:.1f} Years

### Integration Notes

- Solar field connected through heat exchanger
- Existing boiler used for backup heating
- Differential temperature controller recommended
- Install expansion tank and pressure relief valve
- Use insulated piping throughout plant
- Provide maintenance corridor between collector rows
""")

# ============================================================
# FOOTER
# ============================================================

st.success("✅ Universal Solar Thermal Proposal Generated Successfully")

# ============================================================
# ADVANCED ENGINEERING SECTION
# ============================================================

st.subheader("Advanced Engineering Analysis")

reynolds = (flow_total / 3600) * 25

if reynolds < 2300:
    flow_regime = "Laminar"
else:
    flow_regime = "Turbulent"

pipe_velocity = flow_total / 3600 / 0.003

pressure_drop = 0.02 * (50 / 0.05) * ((1000 * pipe_velocity**2) / 2)

pump_head = pressure_drop / (1000 * 9.81)

eng_df = pd.DataFrame(
    {
        "Parameter": [
            "Reynolds Number",
            "Flow Regime",
            "Pipe Velocity",
            "Pressure Drop",
            "Pump Head",
        ],
        "Value": [
            f"{reynolds:.0f}",
            flow_regime,
            f"{pipe_velocity:.2f} m/s",
            f"{pressure_drop:.2f} Pa",
            f"{pump_head:.2f} m",
        ],
    }
)

st.dataframe(eng_df, use_container_width=True)

# ============================================================
# HEAT EXCHANGER SECTION
# ============================================================

st.subheader("Heat Exchanger Sizing")

lmtd = (
    ((outlet_temp - ambient_temp) - (inlet_temp - ambient_temp))
    / np.log(
        ((outlet_temp - ambient_temp) + 0.01)
        / ((inlet_temp - ambient_temp) + 0.01)
    )
)

u_value = 650

hx_area = (
    field['thermal_load'] * 1000
) / (u_value * lmtd)

hx_df = pd.DataFrame(
    {
        "Parameter": [
            "LMTD",
            "Overall Heat Transfer Coefficient",
            "Heat Exchanger Area",
        ],
        "Value": [
            f"{lmtd:.2f} °C",
            f"{u_value} W/m²K",
            f"{hx_area:.2f} m²",
        ],
    }
)

st.dataframe(hx_df, use_container_width=True)

# ============================================================
# STORAGE TANK SECTION
# ============================================================

st.subheader("Storage Tank Design")

storage_factor = 1.2

storage_volume = water * storage_factor

expansion_volume = storage_volume * 0.05

st.markdown(f"""
### Tank Recommendations

- Recommended Storage Tank Volume: {storage_volume:.0f} Liters
- Recommended Expansion Tank Volume: {expansion_volume:.0f} Liters
- Recommended Insulation Thickness: 75 mm Mineral Wool
- Recommended Tank Material: SS304 / SS316
- Suggested Orientation: Vertical Cylindrical
""")

# ============================================================
# SOLAR FRACTION ANALYSIS
# ============================================================

st.subheader("Solar Fraction Analysis")

collector_range = np.arange(1, field['collectors'] + 10)

solar_fraction = []

for c in collector_range:

    sf = min(100, (c / field['collectors']) * 100)

    solar_fraction.append(sf)

sf_df = pd.DataFrame(
    {
        "Collectors": collector_range,
        "Solar Fraction": solar_fraction,
    }
)

fig_sf = px.line(
    sf_df,
    x="Collectors",
    y="Solar Fraction",
    title="Solar Fraction vs Number of Collectors",
)

st.plotly_chart(fig_sf, use_container_width=True)

# ============================================================
# PAYBACK ANALYSIS
# ============================================================

st.subheader("Payback Sensitivity")

fuel_escalation = np.arange(0.02, 0.12, 0.01)

paybacks = []

for esc in fuel_escalation:

    annual_save = finance['annual_savings'] * (1 + esc)

    pb = finance['project_cost'] / annual_save

    paybacks.append(pb)

pb_df = pd.DataFrame(
    {
        "Fuel Escalation": fuel_escalation * 100,
        "Payback": paybacks,
    }
)

fig_pb = px.line(
    pb_df,
    x="Fuel Escalation",
    y="Payback",
    title="Payback vs Fuel Escalation",
)

st.plotly_chart(fig_pb, use_container_width=True)

# ============================================================
# LAND AREA ESTIMATION
# ============================================================

st.subheader("Land Area Estimation")

maintenance_factor = 1.35

land_area = field['total_gross_area'] * maintenance_factor

st.info(
    f"Estimated Total Installation Area Required = {land_area:.2f} m²"
)

# ============================================================
# CONTROL STRATEGY
# ============================================================

st.subheader("Recommended Control Philosophy")

control_points = [
    "Differential temperature controller between collector and tank",
    "PT100 sensors at collector outlet and tank inlet",
    "Motorized bypass valve for overheating protection",
    "Expansion tank pressure monitoring",
    "Low flow alarm for pump protection",
    "Dry run protection for circulation pump",
    "Automatic backup boiler interlock",
]

for p in control_points:
    st.markdown(f"- {p}")

# ============================================================
# INDUSTRY SPECIFIC RECOMMENDATIONS
# ============================================================

st.subheader("Industry Specific Integration")

if industry == "Dairy":
    st.warning(
        "Use CIP-compatible SS316 piping and hygienic heat exchangers."
    )

elif industry == "Textile":
    st.warning(
        "Provide continuous thermal buffer for process stability."
    )

elif industry == "Pharmaceutical":
    st.warning(
        "Use sterile closed loop with insulated SS316L piping."
    )

elif industry == "Food":
    st.warning(
        "Use food-grade insulated piping and sanitary fittings."
    )

elif industry == "Chemical":
    st.warning(
        "Provide corrosion-resistant heat exchanger and glycol loop."
    )

# ============================================================
# PIPE SIZING
# ============================================================

st.subheader("Pipe Sizing Recommendations")

if flow_total < 500:
    pipe_size = "25 NB"
elif flow_total < 1500:
    pipe_size = "40 NB"
else:
    pipe_size = "65 NB"

pipe_df = pd.DataFrame(
    {
        "Parameter": [
            "Recommended Pipe Size",
            "Recommended Material",
            "Recommended Insulation",
        ],
        "Value": [
            pipe_size,
            "GI / Copper / SS304",
            "Nitrile Rubber / Mineral Wool",
        ],
    }
)

st.dataframe(pipe_df, use_container_width=True)

# ============================================================
# ENERGY FLOW SANKEY SUBSTITUTE
# ============================================================

st.subheader("Energy Distribution")

energy_df = pd.DataFrame(
    {
        "Section": [
            "Solar Collection",
            "Pipe Losses",
            "Tank Losses",
            "Useful Process Heat",
        ],
        "Energy": [
            100,
            8,
            5,
            87,
        ],
    }
)

fig_energy = px.pie(
    energy_df,
    names="Section",
    values="Energy",
    title="Thermal Energy Distribution",
)

st.plotly_chart(fig_energy, use_container_width=True)

# ============================================================
# DETAILED BOM
# ============================================================

st.subheader("Bill Of Materials")

bom = pd.DataFrame(
    {
        "Component": [
            "Solar Collectors",
            "Solar Pump",
            "Heat Exchanger",
            "Expansion Tank",
            "Storage Tank",
            "Piping",
            "Insulation",
            "Control Panel",
            "Sensors",
            "Support Structure",
        ],
        "Quantity": [
            field['collectors'],
            2,
            1,
            1,
            1,
            "As Required",
            "As Required",
            1,
            8,
            field['collectors'],
        ],
    }
)

st.dataframe(bom, use_container_width=True)

# ============================================================
# FINAL DESIGN NOTES
# ============================================================

st.subheader("Engineering Design Notes")

notes = [
    "Provide south-facing collector orientation.",
    "Tilt angle should be optimized based on latitude.",
    "Provide proper hydraulic balancing for collector rows.",
    "Install air vent at highest point of collector circuit.",
    "Provide pressure relief valve at hot loop.",
    "Use weatherproof insulation for outdoor piping.",
    "Perform hydrotest before commissioning.",
    "Provide maintenance corridor between collector rows.",
    "Use VFD-controlled pump for flow optimization.",
]

for n in notes:
    st.markdown(f"- {n}")

# ============================================================
# DOWNLOAD REPORT PLACEHOLDER
# ============================================================

st.subheader("Proposal Export")

st.download_button(
    label="Download Proposal Summary",
    data=finance_df.to_csv(index=False),
    file_name="solar_proposal_summary.csv",
    mime="text/csv",
)

# ============================================================
# END OF APPLICATION
# ============================================================

st.success("🚀 Industrial Solar Thermal Engineering Platform Ready")
