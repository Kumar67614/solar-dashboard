import streamlit as st
import plotly.graph_objects as go
import numpy as np

# 🎨 Page Configuration & Custom CSS Styling
st.set_page_config(page_title="Industrial Solar Thermal Sizing Engine", layout="wide")

# Custom CSS for industrial enterprise theme
st.markdown("""
    <style>
    .metric-container {
        background-color: #f1f3f5;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0f52ba;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-title { font-size: 13px; color: #495057; font-weight: bold; letter-spacing: 0.5px; }
    .metric-value { font-size: 26px; color: #212529; font-weight: bold; }
    .section-header { color: #0f52ba; border-bottom: 2px solid #0f52ba; padding-bottom: 5px; margin-top: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 SQS Industrial Solar Water Heating Design & Proposal Engine")
st.markdown("##### Enterprise-Grade Sizing, Balance of Plant (BOP) Configuration & Financial Feasibility")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS
st.sidebar.header("🎯 Plant Sizing Basis")
water = st.sidebar.number_input("Design Plant Capacity (LPD)", value=10000, step=1000)
tout = st.sidebar.number_input("Process Delivery Output Temp (°C)", value=80, min_value=30, max_value=95)
tin = st.sidebar.number_input("Industrial Feed Water Inlet Temp (°C)", value=25, min_value=5, max_value=40)

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Balance of Plant (BOP) Variables")
pipe_loss_factor = st.sidebar.slider("Distribution Piping Thermal Loss (%)", min_value=2, max_value=15, value=5, step=1)
tank_safety_margin = st.sidebar.slider("Storage Buffer Multiplier", min_value=1.1, max_value=1.4, value=1.2, step=0.05)
aux_fuel_type = st.sidebar.selectbox("Auxiliary/Backup Fuel Type", ["Furnace Oil (FO)", "Diesel (HSD)", "Natural Gas", "Electricity"])

st.sidebar.markdown("---")
st.sidebar.header("💰 Commercial & Utility Rates")
fuel_cost = st.sidebar.number_input("Backup Fuel/Utility Cost (per Liter or SCM or kWh)", value=85.0, step=5.0)
project_cost_per_m2 = st.sidebar.number_input("Turnkey Project Cost (₹ per m² of collector area)", value=14000, step=500)

# 🔢 CONSTANTS & CORE THERMODYNAMIC MATH
cp = 4.186            # Specific heat capacity of water (kJ/kg·K)
module_energy = 22    # kWh/day per module nominal baseline output
module_area = 7.2     # m² per module area

# 🧮 PROCESS CALCULATIONS
dt = tout - tin
net_energy_demand = (water * cp * dt) / 3600  # Raw thermal energy required (kWh/day)
piping_losses = net_energy_demand * (pipe_loss_factor / 100)
gross_energy_required = net_energy_demand + piping_losses

# Module Sizing
safety_factor = tank_safety_margin  # Combing buffer allocation
modules = round((gross_energy_required * safety_factor) / module_energy)
modules = max(modules, 1)  # Safeguard baseline
total_collector_area = modules * module_area

# Balance of Plant Calculations
storage_tank_capacity = water * tank_safety_margin
flow_lpm = ((modules / 2) * 250) / 60
flow_kghr = flow_lpm * 60

# Array Architecture Config (Max 10 modules per bank in series to prevent vapor lock)
modules_per_bank = 8 if modules >= 8 else modules
total_banks = int(np.ceil(modules / modules_per_bank))

# 🌿 ENVIRONMENTAL & FUEL DISPLACEMENT ANALYSIS
fuel_data = {
    "Furnace Oil (FO)": {"calorific": 10200, "unit": "Liters", "eff": 0.80, "co2": 3.1},
    "Diesel (HSD)": {"calorific": 9200, "unit": "Liters", "eff": 0.82, "co2": 2.68},
    "Natural Gas": {"calorific": 8500, "unit": "SCM", "eff": 0.85, "co2": 1.95},
    "Electricity": {"calorific": 860, "unit": "kWh", "eff": 0.98, "co2": 0.82}
}

selected_fuel = fuel_data[aux_fuel_type]
annual_thermal_load_kwh = gross_energy_required * 300 # Assuming 300 operational sunny days/year
fuel_saved_annual = (annual_thermal_load_kwh * 3600) / (selected_fuel["calorific"] * selected_fuel["eff"])
annual_monetary_savings = fuel_saved_annual * fuel_cost
co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000 if aux_fuel_type != "Electricity" else (annual_thermal_load_kwh * selected_fuel["co2"]) / 1000

# CAPEX & Financial Metrics
turnkey_capex = total_collector_area * project_cost_per_m2
simple_payback_years = turnkey_capex / annual_monetary_savings if annual_monetary_savings > 0 else 0
roi_percent = (annual_monetary_savings / turnkey_capex) * 100 if turnkey_capex > 0 else 0

# ==================== MAIN DASHBOARD DISPLAY ====================

# SECTION 1: ENGINEERING SIZING
st.markdown('<h3 class="section-header">📋 I. Engineering Sizing Specifications</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-container" style="border-left-color: #e63946;"><div class="metric-title">🔥 NET THERMAL LOAD</div><div class="metric-value">{net_energy_demand:.1f} kWh/Day</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-left-color: #2a9d8f;"><div class="metric-title">📦 TOTAL SOLAR MODULES</div><div class="metric-value">{modules} Units</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-left-color: #f4a261;"><div class="metric-title">📐 TOTAL FIELD AREA</div><div class="metric-value">{total_collector_area:.1f} m²</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-left-color: #457b9d;"><div class="metric-title">💧 LOOP DESIGN FLOW</div><div class="metric-value">{flow_lpm:.1f} LPM</div></div>', unsafe_allow_html=True)

# SECTION 2: BALANCE OF PLANT
st.markdown('<h3 class="section-header">⚙️ II. Balance of Plant (BOP) & System Architecture</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.subheader("📦 Tank & Storage Sizing")
    st.info(f"**Recommended Tank Capacity:** {storage_tank_capacity:,.0f} Liters")
    st.markdown(f"""
    * **Material Spec:** SS314 / SS316 L Inner Vessel
    * **Insulation:** 100mm High-Density Rockwool or PUF Injection 
    * **Loss Performance:** < 2°C standing loss per 24 hours
    """)
with b2:
    st.subheader("🗺️ Array Field Configuration")
    st.warning(f"**Hydraulic Array Layout:** {total_banks} Banks Parallel")
    st.markdown(f"""
    * **Modules in Series per Bank:** {modules_per_bank} Units
    * **Interconnecting Header Piping:** DN40 / DN50 Copper or Composite Piping
    * **Balancing Valves:** Needed on each parallel bank return loop to prevent short-circuiting.
    """)
with b3:
    st.subheader("🎛️ Automation & Controls Integration")
    if flow_lpm < 25:
        pump_hp = "1.5 HP"
    elif flow_lpm < 50:
        pump_hp = "3.0 HP"
    else:
        pump_hp = "5.0 HP"
    st.success(f"**Primary Loop Pump:** {pump_hp} VFD High-Temp Pump")
    st.markdown(f"""
    * **Differential Temp Controller (DTC):** Modulating logic loops based on collector manifold outputs.
    * **Telemetry:** RS485 Modbus connectivity matching standard plant SCADA systems.
    """)

# SECTION 3: COMMERCIAL PROPOSAL
st.markdown('<h3 class="section-header">💰 III. Commercial Proposal & Financial Viability Analysis</h3>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f'<div class="metric-container" style="border-left-color: #1d3557;"><div class="metric-title">🏗️ TOTAL TURNKEY CAPEX</div><div class="metric-value">₹ {turnkey_capex:,.0f}</div></div>', unsafe_allow_html=True)
with f2:
    st.markdown(f'<div class="metric-container" style="border-left-color: #52b788;"><div class="metric-title">📉 ANNUAL UTILITY SAVINGS</div><div class="metric-value">₹ {annual_monetary_savings:,.0f}</div></div>', unsafe_allow_html=True)
with f3:
    st.markdown(f'<div class="metric-container" style="border-left-color: #7209b7;"><div class="metric-title">⏳ SIMPLE PAYBACK PERIOD</div><div class="metric-value">{simple_payback_years:.2f} Years</div></div>', unsafe_allow_html=True)
with f4:
    st.markdown(f'<div class="metric-container" style="border-left-color: #ffb703;"><div class="metric-title">📊 INTERNAL RATE OF RETURN (ROI)</div><div class="metric-value">{roi_percent:.1f} %</div></div>', unsafe_allow_html=True)

# SECTION 4: LIVE CONTROLLER MATRIX
st.markdown('<h3 class="section-header">🎛️ IV. Real-Time Flow Controller Strategic Profile</h3>', unsafe_allow_html=True)
col_graph, col_logic = st.columns([1, 1.2])

with col_graph:
    efficiency = min((net_energy_demand / (modules * module_energy)) * 100, 100.0)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=efficiency,
        title={'text': "Calculated Solar Harvest Efficiency (%)", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#0f52ba"},
            'steps': [
                {'range': [0, 50], 'color': '#f8d7da'},
                {'range': [50, 85], 'color': '#fff3cd'},
                {'range': [85, 100], 'color': '#d4edda'}
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_logic:
    if flow_kghr <= 150:
        zone, desc, start, irr, dt_stage, harvest = "🟢 LOW THERMAL MASS", "Fast Temp Response", "09:05 AM", "> 320 W/m²", "+2.8°C to +3.5°C", "High Temperature Gain (Low Power)"
    elif flow_kghr <= 250:
        zone, desc, start, irr, dt_stage, harvest = "🟡 TRANSITIONAL ZONE", "High Thermal Lag", "09:25 AM", "> 370 W/m²", "+0.1°C to +0.5°C", "Sub-Optimal Efficiency"
    elif flow_kghr <= 350:
        zone, desc, start, irr, dt_stage, harvest = "🔵 CONVECTIVE RETENTION", "Low Collector Loss", "09:05 AM", "> 320 W/m²", "+0.5°C to +0.7°C", "High Wattage / Net Energy Yield"
    else:
        zone, desc, start, irr, dt_stage, harvest = "🔴 MAX VELOCITY", "Instant Extraction", "09:00 AM", "> 260 W/m²", "+0.3°C", "Max Mass Net Energy Yield"

    st.markdown(fr"""
    | Industrial Flow Management Parameter | Operational Controller Telemetry Status |
    | :--- | :--- |
    | **Current Controller Target State** | **{zone}** ({flow_kghr:.1f} kg/hr) |
    | **Profile Logic Strategy** | *"{desc}"* |
    | **Calculated Target Start Time** | ⏰ {start} |
    | **Minimum Irradiance Gate Threshold** | ☀️ {irr} |
    | **Design Basis Initial Manifold $\Delta$T** | 🌡️ {dt_stage} |
    | **Energy Harvest Yield Allocation** | 🔋 {harvest} |
    | **Displaced Fuel Utility Consumption** | 📉 Equivalent to {fuel_saved_annual:,.1f} {selected_fuel['unit']}/year of {aux_fuel_type} |
    | **Annual Carbon Intensity Offset** | 🍃 {co2_reduction_tons:.1f} Metric Tons CO₂/annum |
    """, unsafe_allow_html=True)