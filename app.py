import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import math

# =========================================================
# 1. PAGE CONFIGURATION & THEMING
# =========================================================

st.set_page_config(
    page_title="SQS Solar SHIP Advanced Engineering Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling for Enterprise look
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    
    /* Metric Card Styling */
    .metric-box {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0f52ba;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        transition: transform 0.2s ease-in-out;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.09);
    }
    .metric-title {
        font-size: 13px;
        color: #6c757d;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #212529;
    }
    .metric-subtitle {
        font-size: 11px;
        color: #adb5bd;
        margin-top: 4px;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #0f52ba;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 8px;
    }
    
    /* Status styling */
    .status-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. METEOROLOGICAL & REGIONAL DATABASE
# =========================================================

REGIONAL_WEATHER_DATA = {
    "Gujarat Industrial Zone (Ahmedabad)": {
        "radiation": [550, 640, 720, 780, 810, 620, 480, 450, 580, 630, 590, 525], # W/m2 avg daily peak
        "ambient_temp": [20, 23, 28, 32, 35, 33, 29, 28, 29, 29, 25, 21], # °C
        "latitude": 23.0225
    },
    "Maharashtra Auto Cluster (Pune)": {
        "radiation": [580, 660, 710, 750, 770, 540, 420, 410, 510, 600, 580, 550],
        "ambient_temp": [21, 24, 28, 31, 32, 28, 25, 25, 25, 26, 23, 21],
        "latitude": 18.5204
    },
    "Tamil Nadu Textile Hub (Tiruppur)": {
        "radiation": [610, 690, 740, 730, 680, 550, 510, 530, 590, 560, 530, 570],
        "ambient_temp": [25, 27, 30, 32, 33, 31, 30, 29, 29, 28, 26, 25],
        "latitude": 11.1085
    },
    "NCR Pharma Cluster (Baddi/Gurugram)": {
        "radiation": [420, 510, 630, 720, 760, 710, 530, 490, 580, 610, 510, 400],
        "ambient_temp": [14, 17, 22, 28, 33, 34, 31, 30, 29, 25, 19, 15],
        "latitude": 28.4595
    },
    "South Karnataka Food Parks (Bengaluru)": {
        "radiation": [600, 680, 730, 720, 670, 520, 460, 480, 540, 570, 560, 560],
        "ambient_temp": [21, 24, 27, 29, 29, 26, 24, 24, 24, 24, 22, 21],
        "latitude": 12.9716
    }
}

# =========================================================
# 3. SIDEBAR INTERFACE (SYSTEM INPUTS)
# =========================================================

st.sidebar.image("https://img.icons8.com/fluent/100/000000/solar-panel.png", width=80)
st.sidebar.title("System Configurator")
st.sidebar.markdown("---")

st.sidebar.subheader("📍 Location & Application")
location = st.sidebar.selectbox("Industrial Cluster Location", list(REGIONAL_WEATHER_DATA.keys()))
industry_type = st.sidebar.selectbox(
    "Process Industry Type",
    ["Dairy Plant", "Textile Industry", "Pharmaceutical", "Chemical Plant", "Food Processing"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("💧 Thermodynamic Parameters")
water = st.sidebar.number_input("Daily Hot Water Volume (LPD)", min_value=500, max_value=500000, value=25000, step=500)
tout = st.sidebar.number_input("Target Process Delivery Temp (°C)", min_value=35, max_value=140, value=85, step=5)
tin = st.sidebar.number_input("Inlet Cold Feed Temp (°C)", min_value=5, max_value=60, value=25, step=2)

st.sidebar.markdown("---")
st.sidebar.subheader("☀️ Solar Collector Technology")
collector_type = st.sidebar.selectbox(
    "Collector Type Selection",
    ["Evacuated Tube Collector (ETC) - Industrial High Temp", "Flat Plate Collector (FPC) - Glazed", "Concentrating Parabolic Dish"]
)

# Set performance coefficients based on standard ASHRAE 93-2003 parameters
if "ETC" in collector_type:
    eta_0, a1, a2 = 0.72, 1.5, 0.010
    module_area = 4.5  # m2 per industrial manifold module
    cost_per_m2 = 16500
elif "FPC" in collector_type:
    eta_0, a1, a2 = 0.78, 3.8, 0.015
    module_area = 2.0  # m2 per collector panel
    cost_per_m2 = 13000
else:  # Concentrating
    eta_0, a1, a2 = 0.65, 0.5, 0.004
    module_area = 12.0
    cost_per_m2 = 24000

st.sidebar.markdown("---")
st.sidebar.subheader("⛽ Utilities & Financials")
fuel_type = st.sidebar.selectbox("Displaced Backup Fuel", ["Furnace Oil (Liters)", "Light Diesel Oil (Liters)", "Natural Gas (SCM)", "Coal (Kg)", "Electricity (kWh)"])

fuel_defaults = {
    "Furnace Oil (Liters)": {"cost": 62.0, "cal_val": 10200, "eff": 0.82, "co2": 2.65},
    "Light Diesel Oil (Liters)": {"cost": 88.0, "cal_val": 10400, "eff": 0.84, "co2": 2.68},
    "Natural Gas (SCM)": {"cost": 48.0, "cal_val": 8500, "eff": 0.88, "co2": 1.92},
    "Coal (Kg)": {"cost": 12.0, "cal_val": 4200, "eff": 0.65, "co2": 1.85},
    "Electricity (kWh)": {"cost": 8.5, "cal_val": 860, "eff": 0.98, "co2": 0.82}
}

fuel_cost = st.sidebar.number_input(f"Base Cost of Fuel (₹)", value=float(fuel_defaults[fuel_type]["cost"]), step=0.5)
project_life = st.sidebar.slider("Assessed Project Horizon (Years)", 5, 25, 15)
discount_rate = st.sidebar.slider("Discount Rate / WACC (%)", 6.0, 18.0, 11.5, 0.5) / 100.0

# Fixed Engineering Multipliers
CP_WATER = 4.184  # kJ/kg*K
SAFETY_FACTOR = 1.15 
SYSTEM_LOSSES = 0.12 # Pipe/Radiation losses

# =========================================================
# 4. ADVANCED ENGINEERING CALCULATIONS CORE
# =========================================================

# Get weather maps
weather = REGIONAL_WEATHER_DATA[location]
avg_radiation = np.mean(weather["radiation"])
avg_ambient = np.mean(weather["ambient_temp"])

# Thermal Energy Demand Calculations
delta_t = tout - tin
mass_kg = water # 1 Liter of water ~ 1 kg
daily_energy_kj = mass_kg * CP_WATER * delta_t
daily_energy_kwh = daily_energy_kj / 3600.0
gross_daily_demand_kwh = daily_energy_kwh * SAFETY_FACTOR

# Steady-state Collector Efficiency Curve Calculations Model
# T* = (T_inlet_avg - T_ambient) / G
t_fluid_avg = (tin + tout) / 2.0
t_star = (t_fluid_avg - avg_ambient) / avg_radiation
calculated_efficiency = eta_0 - (a1 * t_star) - (a2 * avg_radiation * (t_star ** 2))
calculated_efficiency = max(0.25, min(calculated_efficiency, eta_0)) # Keep within realistic thresholds

# Module Sizing Logic
# Average effective peak solar hours in India assumed ~ 4.8 hours
peak_solar_hours = 4.8
module_yield_kwh_per_day = (avg_radiation * module_area * calculated_efficiency * peak_solar_hours) / 1000.0
modules_required = math.ceil(gross_daily_demand_kwh / module_yield_kwh_per_day)
total_collector_area = modules_required * module_area

# Storage Hydraulics & Sizing
storage_tank_capacity = water * 1.25 # Buffer rule of thumb for solar thermal industrial systems

# Flow rate optimization loop based on delta T across collector array loops (Target loop delta T = 12C)
loop_delta_t = 12.0
total_flow_kg_hr = (gross_daily_demand_kwh / peak_solar_hours) * 3600.0 / (CP_WATER * loop_delta_t)
flow_lpm = total_flow_kg_hr / (60.0 * 1.0) # Density ~ 1 kg/L

# Pipe Size selection based on maximum fluid velocity constraint (< 1.2 m/s to prevent erosion)
flow_m3_s = (flow_lpm / 1000.0) / 60.0
if flow_lpm < 30:
    pipe_size = "DN25 (1\")"
    inner_dia_m = 0.0272
elif flow_lpm < 80:
    pipe_size = "DN40 (1.5\")"
    inner_dia_m = 0.041b if '0.041' else 0.0419
else:
    pipe_size = "DN50 (2\")"
    inner_dia_m = 0.0539

fluid_velocity = flow_m3_s / (math.pi * (inner_dia_m ** 2) / 4.0)

# Pump Sizing Logic (Calculating head based on estimated equivalent pipe length of 120 meters)
equivalent_length = 120.0
friction_factor = 0.02 # Rough estimation for commercial steel pipes
head_loss_friction = friction_factor * (equivalent_length / inner_dia_m) * (fluid_velocity ** 2) / (2 * 9.81)
static_head = 8.0 # Assumed fixed static lift to roof
total_head_m = head_loss_friction + static_head
hydraulic_power_w = 1000.0 * 9.81 * flow_m3_s * total_head_m
pump_efficiency = 0.55
motor_power_hp = (hydraulic_power_w / pump_efficiency) / 746.0

if motor_power_hp < 1.0:
    pump_rating = "1.0 HP Industrial Single Stage"
elif motor_power_hp < 2.0:
    pump_rating = "2.0 HP Industrial Multi-Stage"
elif motor_power_hp < 3.0:
    pump_rating = "3.0 HP High-Flow Pump"
else:
    pump_rating = "5.0 HP Heavy-Duty Circulator"

# =========================================================
# 5. FINANCIAL & ENVIRONMENTAL CALCULATIONS
# =========================================================

# Annual performance mapping looping through months
monthly_energy_production_kwh = []
for rad in weather["radiation"]:
    m_eff = eta_0 - (a1 * ((t_fluid_avg - avg_ambient)/rad)) - (a2 * rad * (((t_fluid_avg - avg_ambient)/rad)**2))
    m_eff = max(0.20, min(m_eff, eta_0))
    m_yield = (rad * total_collector_area * m_eff * peak_solar_hours * 30.4) / 1000.0
    monthly_energy_production_kwh.append(m_yield)

annual_solar_energy_generated_kwh = sum(monthly_energy_production_kwh)

# Fuel savings translations
fuel_cal_val_kcal = fuel_defaults[fuel_type]["cal_val"]
fuel_cal_val_kwh = fuel_cal_val_kcal / 860.0 # Convert kcal to kWh
fuel_efficiency = fuel_defaults[fuel_type]["eff"]

effective_kwh_per_unit_fuel = fuel_cal_val_kwh * fuel_efficiency
annual_fuel_saved_units = annual_solar_energy_generated_kwh / effective_kwh_per_unit_fuel
annual_financial_savings = annual_fuel_saved_units * fuel_cost

# Project Costs
capex_collectors = total_collector_area * cost_per_m2
capex_storage_tank = storage_tank_capacity * 45 # ₹45 per liter for insulated SS304 industrial tank
capex_pumping_hydraulics = 125000 # Lump sum piping, valves, pump configuration
capex_automation = 85000 # PLC based temperature & logic control system
total_project_cost_capex = capex_collectors + capex_storage_tank + capex_pumping_hydraulics + capex_automation

# Maintenance Costs
annual_om_cost = total_project_cost_capex * 0.025 # 2.5% capex per annum escalation

# Cash flow model vectorization for NPV / IRR calculations
cash_flows = [-total_project_cost_capex]
for year in range(1, project_life + 1):
    # Escalating fuel price by 4% yearly, maintenance by 3% yearly
    inflated_savings = annual_financial_savings * ((1.04) ** year)
    inflated_om = annual_om_cost * ((1.03) ** year)
    net_cash_flow = inflated_savings - inflated_om
    
    # Adding Accelerated Depreciation Tax Shield Benefit in Year 1 & 2 (40% WDV rule in India for Solar)
    if year == 1:
        tax_shield = (total_project_cost_capex * 0.40) * 0.25 # Assumed corporate tax rate 25%
        net_cash_flow += tax_shield
    elif year == 2:
        tax_shield = ((total_project_cost_capex * 0.60) * 0.40) * 0.25
        net_cash_flow += tax_shield
        
    cash_flows.append(net_cash_flow)

# Financial KPI Metrics compute
payback_period_years = total_project_cost_capex / (annual_financial_savings - annual_om_cost)

# NPV Function Calculation
npv_value = sum([cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows)])

# IRR Calculation using numpy financial simulation loop
try:
    irr_value = np.irr(cash_flows) if hasattr(np, 'irr') else np.fsolve(lambda r: sum([cf / ((1 + r) ** i) for i, cf in enumerate(cash_flows)]), 0.1)[0]
    irr_percentage = irr_value * 100
except:
    irr_percentage = 0.0

# Carbon Mitigation mapping
co2_factor = fuel_defaults[fuel_type]["co2"]
annual_co2_saved_tons = (annual_fuel_saved_units * co2_factor) / 1000.0 if fuel_type != "Electricity (kWh)" else (annual_fuel_saved_units * co2_factor)

# =========================================================
# 6. APP DASHBOARD UI VIEW RENDERING
# =========================================================

st.title("☀️ SQS Solar Water Heating Design Proposal")
st.caption(f"⚡ Advanced Techno-Economic Simulation Engine | Current Real-Time Calculation Version: {pd.Timestamp.now().strftime('%d-%m-%Y')}")
st.markdown("---")

# ---------------------------------------------------------
# ENGINEERING KPI SECTION
# ---------------------------------------------------------
st.markdown('<div class="section-title">📊 Process Engineering & Thermal Sizing Summary</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Thermal Load Requirement</div>
        <div class="metric-value">{daily_energy_kwh:.1f} <span style="font-size:14px;">kWh/day</span></div>
        <div class="metric-subtitle">Net Process Energy required to heat water</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Solar Array Size</div>
        <div class="metric-value">{modules_required} <span style="font-size:14px;">Modules</span></div>
        <div class="metric-subtitle">{total_collector_area:.1f} m² Gross Area installed</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Design Array Flow Rate</div>
        <div class="metric-value">{flow_lpm:.1f} <span style="font-size:14px;">LPM</span></div>
        <div class="metric-subtitle">Velocity: {fluid_velocity:.2f} m/s inside lines</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Thermal Storage Sizing</div>
        <div class="metric-value">{storage_tank_capacity:,.0f} <span style="font-size:14px;">Liters</span></div>
        <div class="metric-subtitle">SS304 Insulated Stratified Tank</div>
    </div>
    """, unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Simulated Array Efficiency</div>
        <div class="metric-value">{calculated_efficiency*100:.1f}%</div>
        <div class="metric-subtitle">Calculated at peak steady-state parameters</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Hydraulic Pump Selection</div>
        <div class="metric-value" style="font-size:18px; padding-top:8px; padding-bottom:8px;">{pump_rating}</div>
        <div class="metric-subtitle">Total dynamic head calculated: {total_head_m:.1f} m</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Header Piping Diameters</div>
        <div class="metric-value">{pipe_size}</div>
        <div class="metric-subtitle">Optimized to prevent cavitation & pressure drops</div>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Annual Solar Thermal Yield</div>
        <div class="metric-value" style="font-size:22px; padding-top:4px;">{annual_solar_energy_generated_kwh:,.0f} <span style="font-size:12px;">kWh/Yr</span></div>
        <div class="metric-subtitle">Equivalent total thermal delivery</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# FINANCIAL KPI SECTION
# ---------------------------------------------------------
st.markdown('<div class="section-title">💰 Capital Investment & Financial Analysis</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f"""
    <div class="metric-box" style="border-left-color: #2ecc71;">
        <div class="metric-title">Turnkey Turnaround CAPEX</div>
        <div class="metric-value">₹ {total_project_cost_capex:,.0f}</div>
        <div class="metric-subtitle">Includes mechanical erection, piping, controls</div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class="metric-box" style="border-left-color: #2ecc71;">
        <div class="metric-title">Gross First Year Savings</div>
        <div class="metric-value">₹ {annual_financial_savings:,.0f}</div>
        <div class="metric-subtitle">Saved {annual_fuel_saved_units:,.0f} units of {fuel_type}</div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown(f"""
    <div class="metric-box" style="border-left-color: #2ecc71;">
        <div class="metric-title">Financial Metrics (IRR / NPV)</div>
        <div class="metric-value" style="font-size:20px; padding-top:6px; padding-bottom:6px;">IRR: {irr_percentage:.1f}% | NPV: ₹{npv_value:,.0f}</div>
        <div class="metric-subtitle">Calculated over {project_life} years project horizon</div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div class="metric-box" style="border-left-color: #2ecc71;">
        <div class="metric-title">Simple Payback Framework</div>
        <div class="metric-value">{payback_period_years:.2f} <span style="font-size:14px;">Years</span></div>
        <div class="metric-subtitle">Tax shield impacts pull actual break-even earlier</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# VISUALIZATION CHARTS GRAPHICS
# ---------------------------------------------------------
st.markdown('<div class="section-title">📊 Performance Curves & Solar Radiation Data Analysis</div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)

with g1:
    # Gauge Chart for system efficiency execution
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=calculated_efficiency * 100,
        title={'text': "Operating Collector Efficiency (%)", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#0f52ba"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 35], 'color': '#ffccd5'},
                {'range': [35, 60], 'color': '#ffe3e8'},
                {'range': [60, 100], 'color': '#d8f3dc'}
            ],
        }
    ))
    fig_gauge.update_layout(height=320, margin=dict(t=40, b=10, l=20, r=20))
    st.components.v1.html(f"<div style='background-color:white; border-radius:12px; padding:10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);'>{fig_gauge.to_html(include_plotlyjs='cdn')}</div>", height=340)

with g2:
    # Monthly Energy Yield Production Output Chart
    months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig_yield = go.Figure()
    fig_yield.add_trace(go.Bar(
        x=months_labels,
        y=monthly_energy_production_kwh,
        name="Thermal Energy Produced",
        marker_color="#f4a261",
        hovertemplate='Energy Yield: %{y:,.0f} kWh<extra></extra>'
    ))
    fig_yield.update_layout(
        title="Simulated Monthly Energy Thermal Generation (kWh)",
        xaxis_title="Timeline Months",
        yaxis_title="Energy Transferred (kWh)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=40, b=40, l=40, r=20)
    )
    fig_yield.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig_yield.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    st.components.v1.html(f"<div style='background-color:white; border-radius:12px; padding:10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);'>{fig_yield.to_html(include_plotlyjs='cdn')}</div>", height=340)

st.markdown("<br>", unsafe_allow_html=True)
g3, g4 = st.columns(2)

with g3:
    # Dynamic Efficiency Curve Plotting
    x_curve = np.linspace(0, 0.25, 100)
    y_curve = (eta_0 - (a1 * x_curve) - (a2 * avg_radiation * (x_curve ** 2))) * 100
    
    fig_eff_curve = go.Figure()
    fig_eff_curve.add_trace(go.Scatter(
        x=x_curve, y=y_curve,
        mode='lines',
        line=dict(color='#0f52ba', width=3),
        name="Collector Characteristic"
    ))
    # Point representing current operating condition
    fig_eff_curve.add_trace(go.Scatter(
        x=[t_star], y=[calculated_efficiency * 100],
        mode='markers',
        marker=dict(color='red', size=12, symbol='cross'),
        name="Operating System Target"
    ))
    fig_eff_curve.update_layout(
        title="Collector Thermal Efficiency Characteristic Curve",
        xaxis_title="Reduced Temperature Parameter T* = (Tm - Ta)/G",
        yaxis_title="Instantaneous Efficiency η (%)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=40, b=40, l=40, r=20),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    fig_eff_curve.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig_eff_curve.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    st.components.v1.html(f"<div style='background-color:white; border-radius:12px; padding:10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);'>{fig_eff_curve.to_html(include_plotlyjs='cdn')}</div>", height=340)

with g4:
    # Cash Flow ROI Progression Line Chart across lifecycle
    accumulated_cash_flow = np.cumsum(cash_flows)
    timeline_years = list(range(0, project_life + 1))
    
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=timeline_years, y=accumulated_cash_flow,
        mode='lines+markers',
        line=dict(color='#2ecc71', width=3),
        name="Net Project Equity Valuation"
    ))
    fig_roi.add_hline(y=0, line_dash="dash", line_color="red")
    fig_roi.update_layout(
        title="Lifecycle Cumulative Net Cash Flow Cushion (Break-even Tracker)",
        xaxis_title="Operation Lifecycle (Years)",
        yaxis_title="Cumulative Net Value (₹)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=40, b=40, l=40, r=20)
    )
    fig_roi.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig_roi.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    st.components.v1.html(f"<div style='background-color:white; border-radius:12px; padding:10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);'>{fig_roi.to_html(include_plotlyjs='cdn')}</div>", height=340)

# ---------------------------------------------------------
# GRAPHVIZ INDUSTRIAL P&ID (FIXED SYNTAX EXTRA ESCAPED)
# ---------------------------------------------------------
st.markdown('<div class="section-title">🏭 Engineered Industrial P&ID Architecture Diagram</div>', unsafe_allow_html=True)

process_map = {
    "Dairy Plant": "Pasteurizer Line System",
    "Textile Industry": "Dyeing Jet Machines Vats",
    "Pharmaceutical": "Sanitary Reactor Heating Jacket",
    "Chemical Plant": "Corrosive Chemical Preheating Vat",
    "Food Processing": "Retort Steam / Food Batch Cooker"
}
process_name = process_map[industry_type]

# Using exact 4 backslashes (\\\\n) to survive Streamlit compilation passing raw literals to Graphviz engine
pid_diagram_spec = f"""
digraph G {{
    rankdir=LR;
    node [fontname="Arial", fontsize=11, shape=box, style=filled, fillcolor="#F0F4F8", color="#0F52BA", penwidth=1.5];
    edge [fontname="Arial", fontsize=9, color="#4A5568", penwidth=1.2];

    ColdInlet [label="Cold Make-up Feed\\\\nInlet Water Temp: {tin}°C", shape=invhouse, fillcolor="#EBF8FF"];
    
    Tank [label="Thermal Buffer Tank\\\\nCapacity: {storage_tank_capacity:,.0f} Liters\\\\nStratified Layer Control", shape=cylinder, fillcolor="#FEFCBF", color="#D69E2E"];
    
    Pump [label="Circulation Loop Pump\\\\nRating: {pump_rating}\\\\nVelocity: {fluid_velocity:.2f} m/s", shape=circle, fillcolor="#C6F6D5", color="#38A169"];
    
    CollectorArray [label="Solar Field Array\\\\n{modules_required} Modules ({total_collector_area:.1f} m²)\\\\nTech: {collector_type}", shape=component, fillcolor="#FED7D7", color="#E53E3E"];
    
    HX [label="Primary Isolation\\\\nPlate Heat Exchanger", shape=diamond, fillcolor="#E2E8F0"];
    
    BackupBoiler [label="Auxiliary Backup Boiler\\\\nFuel Source: {fuel_type}\\\\nThermal Efficiency: {fuel_efficiency*100}%", shape=box3d, fillcolor="#E9D8FD", color="#805AD5"];
    
    ProcessDelivery [label="Industrial Application End-use\\\\n{process_name}\\\\nDelivery Heat: {tout}°C", shape=house, fillcolor="#ED64A6", color="#B83280"];

    ColdInlet -> Tank [label="Modulated Level Flow"];
    Tank -> Pump [label="Suction Line"];
    Pump -> CollectorArray [label="Forced Flow {flow_lpm:.1f} LPM"];
    CollectorArray -> HX [label="Solar Thermal Glycol Fluid"];
    HX -> Tank [label="Energy Secondary Exchange Loop"];
    Tank -> BackupBoiler [label="Temperature Top-up Request"];
    BackupBoiler -> ProcessDelivery [label="Guaranteed Temperature Line"];
    ProcessDelivery -> Tank [label="Return Recirculation Residual Warm Fluid"];
}}
"""

with st.container():
    st.graphviz_chart(pid_diagram_spec, use_container_width=True)

# ---------------------------------------------------------
# AUDIT SPECIFICATION DATA TABLE SUMMARY
# ---------------------------------------------------------
st.markdown('<div class="section-title">📋 Consolidated Bill of Materials & Technical Specifications</div>', unsafe_allow_html=True)

proposal_matrix = {
    "Engineering Parameter Description": [
        "Project Design Geographical Zone Cluster",
        "Target Manufacturing End-Use Category",
        "Specified Process Base Consumption Volume",
        "Target Regulated Delivery Temperature",
        "Design Cold Supply Inlet Feed Temperature",
        "Net Process Thermal Energy Demand Load Baseline",
        "Selected Solar Collector Architecture Specification",
        "Calculated Array Module Quantities Requirement",
        "Total Combined Gross Solar Collector Footprint",
        "Calculated Buffer Thermal Balance Storage Capacity",
        "Calculated Loop Hydronic Distribution Flow Rate",
        "Mechanical Pipe Network Dimension Matrix",
        "Total Estimated Infrastructure Turnkey Execution Budget",
        "Displaced Utility Backup Combustion Fuel Source",
        "Calculated Net Displaced Annual Energy Savings Metric",
        "Projected Greenhouse Gas Environmental Carbon Reduction"
    ],
    "Design Optimization Value": [
        str(location),
        str(industry_type),
        f"{water:,.0f} Liters Per Day (LPD)",
        f"{tout:.1f} °C",
        f"{tin:.1f} °C",
        f"{daily_energy_kwh:,.2f} kWh/day",
        str(collector_type),
        f"{modules_required} Standard Manifold Core Units",
        f"{total_collector_area:,.2f} Square Meters (m²)",
        f"{storage_tank_capacity:,.0f} Liters Fluid Medium",
        f"{flow_lpm:,.2f} Liters Per Minute (LPM)",
        f"{pipe_size} Nominal Internal Diameter Schedule",
        f"₹ {total_project_cost_capex:,.2f} INR Total Turnkey Project Cost",
        str(fuel_type),
        f"₹ {annual_financial_savings:,.2f} INR Saved / Annum",
        f"{annual_co2_saved_tons:,.2f} Metric Tons CO₂ Emitted Reduced / Year"
    ]
}

proposal_df = pd.DataFrame(proposal_matrix)
st.dataframe(proposal_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# SYSTEM COMPLIANCE & REASONING FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.success(f"✅ Techno-Economic Modeling Proposal Successfully Built For {industry_type}. System complies with MNRE Solar Thermal System Industrial Process Integration Directives.")
