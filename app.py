import streamlit as st
import plotly.graph_objects as go
import math

# 🎨 Page Setup & Clean Design Style
st.set_page_config(page_title="Industrial Solar Water Heating Design", layout="wide")

st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-top: 4px solid #0f52ba;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 12px; color: #6c757d; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 5px;}
    .metric-value { font-size: 22px; color: #1c1c1e; font-weight: bold; }
    .section-header { color: #0f52ba; font-weight: bold; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; margin-top: 25px; margin-bottom: 15px;}
    .card-box { background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Industrial Solar Water Heating Design & Proposal Engine")
st.markdown("##### System Sizing, Heat Loss Coefficients & Financial Feasibility")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS
st.sidebar.header("🎯 1. Water Sizing Inputs")
water = st.sidebar.number_input("Daily Water Required (Liters per Day)", value=8000, step=500, min_value=500)
tout = st.sidebar.number_input("Required Hot Water Output Temp (°C)", value=90, min_value=30, max_value=100)
tin = st.sidebar.number_input("Incoming Cold Water Inlet Temp (°C)", value=25, min_value=5, max_value=50)

st.sidebar.markdown("---")
st.sidebar.header("🌍 2. Geographic & Climate Inputs")
latitude = st.sidebar.number_input("Site Latitude Angle (Degrees N/S)", value=23.5, min_value=0.0, max_value=60.0, step=0.5)
wind_speed = st.sidebar.slider("Average Wind Speed (m/s)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
ambient_temp = st.sidebar.slider("Ambient Air Temperature (°C)", min_value=0, max_value=45, value=25, step=1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. System Settings")
pipe_loss_factor = st.sidebar.slider("Piping Heat Loss (%)", min_value=2, max_value=15, value=5, step=1)
tank_safety_margin = st.sidebar.slider("Storage Tank Safety Factor", min_value=1.1, max_value=1.4, value=1.20, step=0.05)
aux_fuel_type = st.sidebar.selectbox("Existing Backup Boiler Fuel", ["Furnace Oil (FO)", "Diesel (HSD)", "Natural Gas", "Electricity"])

st.sidebar.markdown("---")
st.sidebar.header("💰 4. Costs & Rates")
fuel_cost = st.sidebar.number_input("Backup Fuel Cost (₹ per Unit)", value=85.0, step=5.0)
project_cost_per_m2 = st.sidebar.number_input("Solar Project Cost (₹ per m²)", value=14000, step=500)

# 🔢 CORE THERMODYNAMIC & HEAT LOSS COEFFICIENT MATH
cp = 4.186            # Specific heat capacity of water (kJ/kg·K)
module_area = 7.2     # m² area per solar module

num_covers = 1          
emittance_plate = 0.95  
emittance_glass = 0.88  

t_plate_k = ((tout + tin) / 2) + 273.15
t_ambient_k = ambient_temp + 273.15
tilt_rad = math.radians(latitude)

# Hottel-Woertz-Klein equations
f_factor = (1 + 0.089 * wind_speed - 0.1166 * 0.089 * wind_speed * emittance_plate) * (1 + 0.07866 * num_covers)
c_factor = 520 * (1 - 0.000051 * (latitude ** 2)) if latitude < 40 else 390
e_factor = 0.430 * (1 - 100 / t_plate_k)

top_loss_denominator_1 = (num_covers / (c_factor / t_plate_k) * ((t_plate_k - t_ambient_k) / (num_covers + f_factor)) ** e_factor) + (1 / wind_speed)
top_loss_radiation = (5.67e-8 * (t_plate_k**2 + t_ambient_k**2) * (t_plate_k + t_ambient_k)) / (
    (1 / (emittance_plate + 0.00591 * num_covers * wind_speed)) + ((2 * num_covers + f_factor - 1 + 0.133 * emittance_plate) / emittance_glass) - num_covers
)

u_top = (1 / top_loss_denominator_1) + top_loss_radiation
u_back = 0.5  
u_edge = 0.2  
u_total_loss = u_top + u_back + u_edge  

nominal_yield_per_m2 = 4.5 
collector_efficiency = 0.82 - (u_total_loss * ((tout + tin)/2 - ambient_temp) / 1000)
collector_efficiency = max(0.35, min(collector_efficiency, 0.75)) 
module_energy = nominal_yield_per_m2 * module_area * collector_efficiency

# 🧮 SYSTEM DESIGN CHAIN REACTION
dt = tout - tin if tout > tin else 1
net_energy_demand = (water * cp * dt) / 3600  
piping_losses = net_energy_demand * (pipe_loss_factor / 100)
gross_energy_required = net_energy_demand + piping_losses

modules = round((gross_energy_required * tank_safety_margin) / module_energy)
modules = max(modules, 1)  
total_collector_area = modules * module_area

storage_tank_capacity = water * tank_safety_margin
flow_lpm = ((modules / 2) * 250) / 60
flow_kghr = flow_lpm * 60

modules_per_bank = 8 if modules >= 8 else modules
total_banks = int(max(1, round(modules / modules_per_bank)))

if flow_lpm < 25:
    pump_hp = "1.5 HP"
elif flow_lpm < 50:
    pump_hp = "3.0 HP"
else:
    pump_hp = "5.0 HP"

# 🌿 FUEL SAVINGS & CARBON MATH
fuel_data = {
    "Furnace Oil (FO)": {"calorific": 10200, "unit": "Liters", "eff": 0.80, "co2": 3.1},
    "Diesel (HSD)": {"calorific": 9200, "unit": "Liters", "eff": 0.82, "co2": 2.68},
    "Natural Gas": {"calorific": 8500, "unit": "SCM", "eff": 0.85, "co2": 1.95},
    "Electricity": {"calorific": 860, "unit": "kWh", "eff": 0.98, "co2": 0.82}
}

selected_fuel = fuel_data[aux_fuel_type]
annual_thermal_load_kwh = gross_energy_required * 300 

if aux_fuel_type == "Electricity":
    fuel_saved_annual = annual_thermal_load_kwh / selected_fuel["eff"]
    co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000
else:
    fuel_saved_annual = (annual_thermal_load_kwh * 860) / (selected_fuel["calorific"] * selected_fuel["eff"])
    co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000

annual_monetary_savings = fuel_saved_annual * fuel_cost
turnkey_capex = total_collector_area * project_cost_per_m2
simple_payback_years = turnkey_capex / annual_monetary_savings if annual_monetary_savings > 0 else 0
roi_percent = (annual_monetary_savings / turnkey_capex) * 100 if turnkey_capex > 0 else 0

# ==================== MAIN PAGE VIEW ====================

# SECTION 1: SYSTEM SIZING
st.markdown('<h3 class="section-header">📋 I. System Sizing & Thermal Specifications</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">🔥 DAILY HEAT REQUIRED</div><div class="metric-value">⚡ {net_energy_demand:.1f} <span style="font-size:14px;">kWh/Day</span></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">🧩 TOTAL SOLAR COLLECTORS</div><div class="metric-value">🧩 {modules} <span style="font-size:14px;">Units</span></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">📐 TOTAL SOLAR FIELD AREA</div><div class="metric-value">🗺️ {total_collector_area:.1f} <span style="font-size:14px;">m²</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #457b9d;"><div class="metric-title">💧 WATER LOOP FLOW RATE</div><div class="metric-value">🌊 {flow_lpm:.1f} <span style="font-size:14px;">LPM</span></div></div>', unsafe_allow_html=True)

# SECTION 2: EQUIPMENT LAYOUT DETAILS
st.markdown('<h3 class="section-header">⚙️ II. Main Equipment Layout & Heat Loss Details</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #fff3cd;">
        <h4 style="margin-top:0;">📦 Hot Water Storage Tank</h4>
        <div style="background-color:#fff3cd; padding:10px; border-radius:5px; font-weight:bold; color:#856404; text-align:center; margin-bottom:10px;">
            Tank Size: {storage_tank_capacity:,.0f} Liters
        </div>
        • <b>Material:</b> Stainless Steel (SS316L)<br>
        • <b>Insulation:</b> 100mm Rockwool Layer<br>
        • <b>Heat Loss:</b> Less than 2°C drop per day
    </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #f8d7da;">
        <h4 style="margin-top:0;">🗺️ Solar Collector Sizing</h4>
        <div style="background-color:#f8d7da; padding:10px; border-radius:5px; font-weight:bold; color:#721c24; text-align:center; margin-bottom:10px;">
            Piping Layout: {total_banks} Parallel Banks
        </div>
        • <b>Optimal Mounting Tilt:</b> {latitude}° (Latitude Aligned)<br>
        • <b>Calculated Loss ($U_L$):</b> {u_total_loss:.2f} W/m²·K<br>
        • <b>Field Efficiency:</b> {collector_efficiency*100:.1f} % under climate variables
    </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #d4edda;">
        <h4 style="margin-top:0;">🎛️ Pumps & Automation</h4>
        <div style="background-color:#d4edda; padding:10px; border-radius:5px; font-weight:bold; color:#155724; text-align:center; margin-bottom:10px;">
            Water Pump: {pump_hp} Motor (VFD)
        </div>
        • <b>Control Logic:</b> Automated Temperature Controller<br>
        • <b>Data Connection:</b> RS485 Modbus for Factory SCADA<br>
        • <b>Safety Features:</b> Temperature & Pressure Relief Valves
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: STANDARD CONSTRAINED P&ID BLUEPRINT DRAWING
st.markdown('<h3 class="section-header">📐 III. Factory Process & Instrumentation Diagram (P&ID)</h3>', unsafe_allow_html=True)
st.markdown("This schematic matches standard industrial water heating loops using regular factory design symbols compressed to standard blueprint dimensions.")

st.graphviz_chart(f"""
digraph G {{
    # Compact Blueprint Canvas Settings
    size="11,6.5!";
    ratio="fill";
    rankdir=LR;
    splines=ortho;
    nodesep=0.3;
    ranksep=0.4;
    
    node [fontname="Helvetica", fontsize=8, penwidth=1.2];
    edge [fontname="Helvetica-Bold", fontsize=7, penwidth=1.2];

    # Inline Piping Components & Valve Graphics
    node [shape=triangle, fixedsize=true, width=0.25, height=0.15, style=filled, fillcolor="#b0bec5", color="#37474f"];
    valv_in [label=""]; valv_out [label=""]; valv_ret [label=""]; valv_by [label=""];
    
    node [shape=diamond, fixedsize=true, width=0.25, height=0.25, fillcolor="#eceff1", label="Y"];
    strainer [label=""];

    # ISA Standard Instrument Circles (Transmitters & Controllers)
    node [shape=circle, fixedsize=true, width=0.5, style=filled, fillcolor="#e0f7fa", color="#006064", fontname="Helvetica-Bold", fontsize=8];
    LT_101 [label="LT\\n101"];
    TT_101 [label="TT\\n101"];
    TT_102 [label="TT\\n102"];
    PT_101 [label="PT\\n101"];
    FT_101 [label="FT\\n101"];
    TIC_101 [label="TIC\\n101", fillcolor="#fff9c4", color="#f57f17"];

    # Plant Vessels & Heavy Equipment Modules
    node [shape=box, style="filled,rounded", width=1.3, height=0.8, color="#0f52ba", fillcolor="#f8f9fa", fontsize=9];
    Inlet [label="📥 COLD INLET\\n({tin}°C Feed)", shape=cds, fillcolor="#e3f2fd"];
    
    subgraph cluster_solar {{
        label="☀️ SOLAR RECOVERY ARRAY FIELD\\n({total_banks} Parallel Banks @ {latitude}° Tilt)";
        color="#c62828"; style="dashed,rounded"; bgcolor="#fffde7"; fontsize=8;
        Array_A [label="BANK A\\n({modules_per_bank} Modules)", fillcolor="#ffebee", color="#e53935", width=1.1, height=0.6];
        Array_B [label="BANK B\\n({max(1, modules-modules_per_bank)} Modules)", fillcolor="#ffebee", color="#e53935", width=1.1, height=0.6];
    }}

    Tank [label="🛢️ STORAGE TANK\\nTK-101\\n({storage_tank_capacity:,.0f} L)", shape=cylinder, fillcolor="#fff3cd", color="#f9a825", width=1.1, height=1.8];
    Boiler [label="🔥 BACKUP BOILER\\n({aux_fuel_type} Trim)", fillcolor="#eceff1", color="#37474f"];
    Process [label="🏭 FACTORY LOAD\\n({tout}°C Hot Demand)", shape=cds, fillcolor="#e8f5e9", color="#2e7d32"];

    node [shape=component, width=0.5, height=0.4, fillcolor="#e8f5e9", color="#2e7d32"];
    Pump_P1 [label="P-1\\n({pump_hp})"];
    Pump_P2 [label="P-2\\n(Boost)"];

    # --- PROCESS PIPING AND HYDRAULICS LOOP FLOW ---

    # Fresh Cold Makeup Water Supply
    Inlet -> strainer [color="#0f52ba"];
    strainer -> valv_in [color="#0f52ba"];
    valv_in -> Tank [color="#0f52ba", label=" Makeup Line"];
    Tank -> LT_101 [style=dotted, color="#546e7a", arrowhead=none];

    # Primary Heat Collection Loop (Bottom Tank Water pumped to Solar array)
    Tank -> Pump_P1 [color="#0f52ba", label=" Suction"];
    Pump_P1 -> Array_A [color="#0f52ba", label=" Loop Flow:\\n{flow_kghr:.0f} kg/hr"];
    Pump_P1 -> Array_B [color="#0f52ba"];
    
    # Solar array thermal harvesting return loop back to top of tank
    Array_A -> TT_101 [color="#c62828"];
    Array_B -> TT_101 [color="#c62828"];
    TT_101 -> PT_101 [color="#c62828"];
    PT_101 -> valv_out [color="#c62828"];
    valv_out -> Tank [color="#c62828", label=" Harvest Return"];

    # Plant Forward Supply Line Loop
    Tank -> Pump_P2 [color="#c62828", label=" Delivery Line"];
    Pump_P2 -> TT_102 [color="#c62828"];
    TT_102 -> valv_ret [color="#c62828"];
    
    valv_ret -> Boiler [color="#c62828", label=" Forward Feed"];
    valv_ret -> valv_by [color="#f9a825", label=" Recirc Loop"];
    valv_by -> Tank [color="#f9a825"];
    
    Boiler -> FT_101 [color="#c62828"];
    FT_101 -> Process [color="#c62828", label=" Delivery"];

    # --- AUTOMATION LOOP LOGIC ---
    edge [style=dashed, color="#757575", penwidth=1, arrowhead=dot];
    TT_101 -> TIC_101 [label=" PV1"];
    TT_102 -> TIC_101 [label=" PV2"];
    TIC_101 -> Pump_P1 [label=" VFD"];
    TIC_101 -> valv_ret [label=" Control"];
}}
""")

# SECTION 4: FINANCIAL PROJECT ANALYSIS
st.markdown('<h3 class="section-header">📊 IV. Project Financial Analysis</h3>', unsafe_allow_html=True)
col_f1, col_f2 = st.columns(2)

with col_f1:
    fig_capex = go.Figure(go.Indicator(
        mode="gauge+number",
        value=turnkey_capex,
        number={'prefix': "₹ ", 'font': {'size': 24}},
        title={'text': "🏗️ Total Solar Project Investment Cost", 'font': {'size': 14, 'color': '#495057'}},
        gauge={'axis': {'range': [0, 15000000], 'tickformat': ','}, 'bar': {'color': "#1d3557"}, 'bgcolor': "#f8f9fa"}
    ))
    fig_capex.update_layout(height=180, margin=dict(l=30, r=30, t=40, b=20))
    st.plotly_chart(fig_capex, use_container_width=True)

with col_f2:
    fig_roi = go.Figure(go.Indicator(
        mode="gauge+number",
        value=roi_percent,
        number={'suffix': " %", 'font': {'size': 24}},
        title={'text': "📈 Annual Return on Investment (ROI)", 'font': {'size': 14, 'color': '#495057'}},
        gauge={
            'axis': {'range': [0, 300]}, 'bar': {'color': "#2a9d8f"},
            'steps': [{'range': [0, 30], 'color': '#f8d7da'}, {'range': [30, 100], 'color': '#fff3cd'}, {'range': [100, 300], 'color': '#d4edda'}],
        }
    ))
    fig_roi.update_layout(height=180, margin=dict(l=30, r=30, t=40, b=20))
    st.plotly_chart(fig_roi, use_container_width=True)

# SECTION 5: PLANT OPERATIONS SAVINGS SUMMARY
st.markdown('<h3 class="section-header">🎛️ V. Plant Operations & Savings Summary</h3>', unsafe_allow_html=True)
col_graph, col_logic = st.columns([1, 1.2])

with col_graph:
    fig_eff = go.Figure(go.Indicator(
        mode="gauge+number",
        value=collector_efficiency * 100,
        number={'suffix': "%", 'font': {'size': 28}},
        title={'text': "🎯 Net Collector Efficiency Under Load", 'font': {'size': 14, 'color': '#495057'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1}, 'bar': {'color': "#0f52ba"},
            'steps': [{'range': [0, 40], 'color': '#f8d7da'}, {'range': [40, 65], 'color': '#fff3cd'}, {'range': [65, 100], 'color': '#d4edda'}],
        }
    ))
    fig_eff.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_eff, use_container_width=True)

with col_logic:
    st.markdown(f"""
    | Factory Metric Parameter | Operational Value Summary Data |
    | :--- | :--- |
    | **Calculated Top Loss Coefficient ($U_t$)** | 🌡️ **{u_top:.2f} W/m²·K** (Driven by wind, tilt & latitude) |
    | **Total Loss Coefficient ($U_L$)** | 📉 **{u_total_loss:.2f} W/m²·K** (Total system thermal loss rate) |
    | **Estimated System Payback Period** | ⏳ **{simple_payback_years:.2f} Years** to recover investment |
    | **Annual Utility Savings Amount** | 💰 **₹ {annual_monetary_savings:,.0f} per year** saved |
    | **Yearly Backup Fuel Saved** | 🚰 **{fuel_saved_annual:,.0f} {selected_fuel['unit']} per year** of {aux_fuel_type} |
    | **Factory Carbon Footprint Reduction** | 🍃 **{co2_reduction_tons:.1f} Tons of CO₂ cut per year** |
    """, unsafe_allow_html=True)