import streamlit as st
import plotly.graph_objects as go

# 🎨 Page Configuration & Custom CSS Styling
st.set_page_config(page_title="SQS Industrial Solar Design Engine", layout="wide")

# Custom CSS for high-impact visual dashboard
st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border-top: 4px solid #0f52ba;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 12px; color: #6c757d; font-weight: bold; letter-spacing: 0.8px; margin-bottom: 5px;}
    .metric-value { font-size: 24px; color: #1c1c1e; font-weight: bold; }
    .section-header { color: #0f52ba; font-weight: bold; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; margin-top: 30px; margin-bottom: 15px;}
    .card-box { background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

st.title("☀️ SQS Industrial Solar Water Heating Design & Proposal Engine")
st.markdown("##### Enterprise-Grade Sizing, Balance of Plant (BOP) Configuration & Financial Feasibility")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS
st.sidebar.header("🎯 1. Plant Sizing Basis")
water = st.sidebar.number_input("Design Plant Capacity (LPD)", value=8000, step=500, min_value=500)
# Updated ranges to match your process specifications (Up to 100°C delivery and 50°C ambient)
tout = st.sidebar.number_input("Process Delivery Output Temp (°C)", value=90, min_value=30, max_value=100)
tin = st.sidebar.number_input("Industrial Feed Water Inlet Temp (°C)", value=25, min_value=5, max_value=50)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Balance of Plant (BOP)")
pipe_loss_factor = st.sidebar.slider("Distribution Piping Loss (%)", min_value=2, max_value=15, value=5, step=1)
tank_safety_margin = st.sidebar.slider("Storage Buffer Multiplier", min_value=1.1, max_value=1.4, value=1.20, step=0.05)
aux_fuel_type = st.sidebar.selectbox("Auxiliary/Backup Fuel Type", ["Furnace Oil (FO)", "Diesel (HSD)", "Natural Gas", "Electricity"])

st.sidebar.markdown("---")
st.sidebar.header("💰 3. Commercial & Utility Rates")
fuel_cost = st.sidebar.number_input("Backup Fuel Cost (₹/Unit)", value=85.0, step=5.0)
project_cost_per_m2 = st.sidebar.number_input("Turnkey Cost (₹ per m²)", value=14000, step=500)

# 🔢 CONSTANTS & CORE THERMODYNAMIC MATH
cp = 4.186            # Specific heat capacity of water (kJ/kg·K)
module_energy = 22    # kWh/day per module nominal baseline output
module_area = 7.2     # m² per module area

# 🧮 PROCESS CALCULATIONS (THERMODYNAMIC DRIVEN CHAIN REACTION)
dt = tout - tin if tout > tin else 1
net_energy_demand = (water * cp * dt) / 3600  # Raw thermal energy required (kWh/day)
piping_losses = net_energy_demand * (pipe_loss_factor / 100)
gross_energy_required = net_energy_demand + piping_losses

# Module Sizing
safety_factor = tank_safety_margin  
modules = round((gross_energy_required * safety_factor) / module_energy)
modules = max(modules, 1)  
total_collector_area = modules * module_area

# Balance of Plant Calculations
storage_tank_capacity = water * tank_safety_margin
flow_lpm = ((modules / 2) * 250) / 60
flow_kghr = flow_lpm * 60

# Array Architecture Config
modules_per_bank = 8 if modules >= 8 else modules
total_banks = int(max(1, round(modules / modules_per_bank)))

# Dynamic Pump Hardware Selection based on real-time volumetric flow rate
if flow_lpm < 25:
    pump_hp = "1.5 HP"
elif flow_lpm < 50:
    pump_hp = "3.0 HP"
else:
    pump_hp = "5.0 HP"

# 🌿 DYNAMIC ENVIRONMENTAL & FUEL DISPLACEMENT ANALYSIS
fuel_data = {
    "Furnace Oil (FO)": {"calorific": 10200, "unit": "Liters", "eff": 0.80, "co2": 3.1},
    "Diesel (HSD)": {"calorific": 9200, "unit": "Liters", "eff": 0.82, "co2": 2.68},
    "Natural Gas": {"calorific": 8500, "unit": "SCM", "eff": 0.85, "co2": 1.95},
    "Electricity": {"calorific": 860, "unit": "kWh", "eff": 0.98, "co2": 0.82}
}

selected_fuel = fuel_data[aux_fuel_type]

# CRITICAL FIX: Annual savings are now fundamentally tied to the changing gross energy calculation
annual_thermal_load_kwh = gross_energy_required * 300 # Assuming 300 operational sunny days/year

if aux_fuel_type == "Electricity":
    fuel_saved_annual = annual_thermal_load_kwh / selected_fuel["eff"]
    co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000
else:
    # 1 kWh = 860 kcal. Converts thermal load to kcal to balance fuel density values
    fuel_saved_annual = (annual_thermal_load_kwh * 860) / (selected_fuel["calorific"] * selected_fuel["eff"])
    co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000

annual_monetary_savings = fuel_saved_annual * fuel_cost

# CAPEX & Financial Metrics (Now dynamic across fuel displacements)
turnkey_capex = total_collector_area * project_cost_per_m2
simple_payback_years = turnkey_capex / annual_monetary_savings if annual_monetary_savings > 0 else 0
roi_percent = (annual_monetary_savings / turnkey_capex) * 100 if turnkey_capex > 0 else 0

# ==================== MAIN DASHBOARD DISPLAY ====================

# SECTION 1: ENGINEERING SIZING (PICTORIAL BLOCKS)
st.markdown('<h3 class="section-header">📋 I. Engineering Sizing Specifications</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">🔥 NET THERMAL LOAD</div><div class="metric-value">⚡ {net_energy_demand:.1f} <span style="font-size:14px;">kWh/Day</span></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">📦 TOTAL SOLAR MODULES</div><div class="metric-value">🧩 {modules} <span style="font-size:14px;">Units</span></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">📐 TOTAL FIELD AREA</div><div class="metric-value">🗺️ {total_collector_area:.1f} <span style="font-size:14px;">m²</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #457b9d;"><div class="metric-title">💧 LOOP DESIGN FLOW</div><div class="metric-value">🌊 {flow_lpm:.1f} <span style="font-size:14px;">LPM</span></div></div>', unsafe_allow_html=True)

# SECTION 2: BALANCE OF PLANT (VISUAL INFO CARDS)
st.markdown('<h3 class="section-header">⚙️ II. Balance of Plant (BOP) & Structural Layout</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #fff3cd;">
        <h4 style="margin-top:0;">📦 Tank & Storage</h4>
        <div style="background-color:#fff3cd; padding:10px; border-radius:5px; font-weight:bold; color:#856404; text-align:center; margin-bottom:10px;">
            Capacity: {storage_tank_capacity:,.0f} Liters
        </div>
        • <b>Spec:</b> Double-wall SS316L Vessel<br>
        • <b>Thermal Shield:</b> 100mm PUF Layer<br>
        • <b>Loss Performance:</b> &lt; 2°C per 24 hours
    </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #f8d7da;">
        <h4 style="margin-top:0;">🗺️ Field Arrangement</h4>
        <div style="background-color:#f8d7da; padding:10px; border-radius:5px; font-weight:bold; color:#721c24; text-align:center; margin-bottom:10px;">
            Hydraulic Layout: {total_banks} Banks Parallel
        </div>
        • <b>Series Density:</b> {modules_per_bank} Modules / Bank<br>
        • <b>Manifolds:</b> Pre-insulated DN50 Copper<br>
        • <b>Balance:</b> Reverse-Return Flow Circuitry
    </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #d4edda;">
        <h4 style="margin-top:0;">🎛️ Flow Automation</h4>
        <div style="background-color:#d4edda; padding:10px; border-radius:5px; font-weight:bold; color:#155724; text-align:center; margin-bottom:10px;">
            Primary Pump: {pump_hp} VFD Drive
        </div>
        • <b>Logic Control:</b> Proportional Solar DTC Tracker<br>
        • <b>Telemetry Protocol:</b> RS485 Modbus SCADA<br>
        • <b>Safety Valve:</b> Integrated Temp & Pressure Relief
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: LIVE SCHEMATIC & PROCESS FLOW BLUEPRINT (P&ID)
st.markdown('<h3 class="section-header">📐 III. Input-Driven Architectural P&ID Layout</h3>', unsafe_allow_html=True)

st.graphviz_chart(f"""
digraph G {{
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Helvetica-Bold", color="#0f52ba", fillcolor="#f8f9fa", fontsize=11, penwidth=2];
    edge [fontname="Helvetica-Bold", fontsize=10, color="#457b9d", penwidth=2];
    
    Inlet [label="📥 Cold Water Feed\\n({tin}°C)", fillcolor="#e3f2fd", shape=cds];
    Tank [label="🛢️ Storage Tank\\n({storage_tank_capacity:,.0f} L)", shape=cylinder, fillcolor="#fff3cd"];
    Pump [label="⚡ Circulation Pump\\n({pump_hp} VFD Loop)", shape=component, fillcolor="#e8f5e9"];
    Array [label="☀️ SQS Solar Field\\n({modules} Modules in {total_banks} Banks)\\n{total_collector_area:.1f} m² Area", fillcolor="#ffebee"];
    Process [label="🏭 Factory Process Load\\n({tout}°C @ {flow_lpm:.1f} LPM)", fillcolor="#e8f5e9", shape=cds];

    Inlet -> Tank [label=" Makeup"];
    Tank -> Pump [label=" Suction"];
    Pump -> Array [label=" Loop Flow:\\n{flow_kghr:.1f} kg/hr"];
    Array -> Tank [label=" Hot Return\\n(+ΔT Thermal Harvest)"];
    Tank -> Process [label=" Delivery Line"];
}}
""")

# SECTION 4: FINANCIAL & REVENUE GAUGES (DYNAMICALLY FLUCTUATES WITH INPUTS)
st.markdown('<h3 class="section-header">📊 IV. Investment Financial Analytics</h3>', unsafe_allow_html=True)
col_f1, col_f2 = st.columns(2)

with col_f1:
    fig_capex = go.Figure(go.Indicator(
        mode="gauge+number",
        value=turnkey_capex,
        number={'prefix': "₹ ", 'font': {'size': 24}},
        title={'text': "🏗️ Total System Turnkey CAPEX Budget", 'font': {'size': 14, 'color': '#495057'}},
        gauge={
            'axis': {'range': [0, 15000000], 'tickformat': ',', 'tickfont': {'size': 10}},
            'bar': {'color': "#1d3557"},
            'bgcolor': "#f8f9fa"
        }
    ))
    fig_capex.update_layout(height=200, margin=dict(l=30, r=30, t=40, b=20))
    st.plotly_chart(fig_capex, use_container_width=True)

with col_f2:
    fig_roi = go.Figure(go.Indicator(
        mode="gauge+number",
        value=roi_percent,
        number={'suffix': " %", 'font': {'size': 24}},
        title={'text': "📈 Internal Rate of Return (Annual ROI)", 'font': {'size': 14, 'color': '#495057'}},
        gauge={
            'axis': {'range': [0, 300]},
            'bar': {'color': "#2a9d8f"},
            'steps': [
                {'range': [0, 30], 'color': '#f8d7da'},
                {'range': [30, 100], 'color': '#fff3cd'},
                {'range': [100, 300], 'color': '#d4edda'}
            ],
        }
    ))
    fig_roi.update_layout(height=200, margin=dict(l=30, r=30, t=40, b=20))
    st.plotly_chart(fig_roi, use_container_width=True)

# SECTION 5: REAL-TIME OPERATION MANAGEMENT STRATEGY
st.markdown('<h3 class="section-header">🎛️ V. Real-Time Flow Controller Strategic Profile</h3>', unsafe_allow_html=True)
col_graph, col_logic = st.columns([1, 1.2])

with col_graph:
    # Efficiency logic scales relative to energy transfer limitations
    efficiency = min((net_energy_demand / (modules * module_energy)) * 100, 100.0) if modules > 0 else 0
    fig_eff = go.Figure(go.Indicator(
        mode="gauge+number",
        value=efficiency,
        number={'suffix': "%", 'font': {'size': 28}},
        title={'text': "🎯 Net Solar Collection Harvest Efficiency", 'font': {'size': 14, 'color': '#495057'}},
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
    fig_eff.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_eff, use_container_width=True)

with col_logic:
    # Classification gates change seamlessly as the mass weight shifts
    if flow_kghr <= 147:
        zone, desc, start, irr, dt_stage, harvest = "🟢 LOW THERMAL MASS", "Fast Temp Response", "09:05 AM", "> 320 W/m²", "+2.8°C to +3.5°C", "High Temperature Gain"
    elif flow_kghr <= 250:
        zone, desc, start, irr, dt_stage, harvest = "🟡 TRANSITIONAL ZONE", "High Thermal Lag", "09:25 AM", "> 370 W/m²", "+0.1°C to +0.5°C", "Sub-Optimal Yield"
    elif flow_kghr <= 357:
        zone, desc, start, irr, dt_stage, harvest = "🔵 CONVECTIVE RETENTION", "Low Collector Loss", "09:05 AM", "> 320 W/m²", "+0.5°C to +0.7°C", "High Net Energy Yield"
    else:
        zone, desc, start, irr, dt_stage, harvest = "🔴 MAX VELOCITY", "Instant Extraction", "09:00 AM", "> 260 W/m²", "+0.3°C", "Peak Mass Net Yield"

    st.markdown(fr"""
    | Industrial Performance Parameter | Automation Controller Telemetry Profile Data |
    | :--- | :--- |
    | **Current Controller State** | **{zone}** (Calculated Loop Mass: {flow_kghr:.1f} kg/hr) |
    | **Profile Strategy Engine** | ⚙️ *"{desc}"* |
    | **Target Optimal Start Time** | ⏰ {start} |
    | **Solar Irradiance Gate** | ☀️ {irr} |
    | **Manifold Boundary Expected $\Delta$T** | 🌡️ {dt_stage} |
    | **Displaced Annual Fuel Utility Energy** | 📉 **{fuel_saved_annual:,.1f} {selected_fuel['unit']}/year** of {aux_fuel_type} |
    | **Carbon Offset Intensity Reduction** | 🍃 **{co2_reduction_tons:.1f} Metric Tons CO₂/year** |
    | **Simple Payback Period Estimate** | ⏳ **{simple_payback_years:.2f} Years** |
    """, unsafe_allow_html=True)