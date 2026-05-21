import streamlit as st
import plotly.graph_objects as go
import math
import numpy as np

# 🎨 Compact Page Setup & Clean Design Style
st.set_page_config(page_title="Industrial Solar Water Heating Design", layout="wide")

st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 6px;
        border-top: 4px solid #0f52ba;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
        border-left: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        border-bottom: 1px solid #e9ecef;
    }
    .metric-title { font-size: 11px; color: #6c757d; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 2px;}
    .metric-value { font-size: 20px; color: #1c1c1e; font-weight: bold; }
    .section-header { color: #0f52ba; font-weight: bold; border-bottom: 2px solid #0f52ba; padding-bottom: 4px; margin-top: 15px; margin-bottom: 10px;}
    .card-box { background: #ffffff; padding: 15px; border-radius: 6px; box-shadow: 0 1px 5px rgba(0,0,0,0.05); margin-bottom: 10px; border: 1px solid #e9ecef; }
    div.block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 SQS Industrial Solar Water Heating Design & Proposal Engine")
st.markdown("##### Enterprise-Grade Sizing, Balance of Plant (BOP) Configuration & Financial Feasibility")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS
st.sidebar.header("🏭 1. Target Application Profile")
industry_type = st.sidebar.selectbox(
    "Select Industrial Application Sector", 
    ["Dairy Processing", "Textile Dyeing", "Pharmaceutical Synthesis", "Chemical Manufacturing"]
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 2. Water Sizing Inputs")
water = st.sidebar.number_input("Daily Water Required (Liters per Day)", value=8000, step=500, min_value=500)
tout = st.sidebar.number_input("Required Hot Water Output Temp (°C)", value=90, min_value=30, max_value=100)
tin = st.sidebar.number_input("Incoming Cold Water Inlet Temp (°C)", value=25, min_value=5, max_value=50)

st.sidebar.markdown("---")
st.sidebar.header("🌍 3. Geographic & Climate Inputs")
latitude = st.sidebar.number_input("Site Latitude Angle (Degrees N/S)", value=23.5, min_value=0.0, max_value=60.0, step=0.5)
wind_speed = st.sidebar.slider("Average Wind Speed (m/s)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
ambient_temp = st.sidebar.slider("Ambient Air Temperature (°C)", min_value=0, max_value=45, value=25, step=1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 4. System Settings")
pipe_loss_factor = st.sidebar.slider("Piping Heat Loss (%)", min_value=2, max_value=15, value=5, step=1)
tank_safety_margin = st.sidebar.slider("Storage Tank Safety Factor", min_value=1.1, max_value=1.4, value=1.20, step=0.05)
aux_fuel_type = st.sidebar.selectbox("Existing Backup Boiler Fuel", ["Furnace Oil (FO)", "Diesel (HSD)", "Natural Gas", "Electricity"])

st.sidebar.markdown("---")
st.sidebar.header("💰 5. Costs & Rates")
fuel_cost = st.sidebar.number_input("Backup Fuel Cost (₹ per Unit)", value=85.0, step=5.0)
project_cost_per_m2 = st.sidebar.number_input("Solar Project Cost (₹ per m²)", value=14000, step=500)

# 🏭 INDUSTRY SPECIFIC DYNAMIC DICTIONARY CONFIGURATION
industry_specs = {
    "Dairy Processing": {"label": "🍼 PASTEURIZATION & CIP LOAD", "color": "#2196f3", "note": "Sanitary tri-clover connections required."},
    "Textile Dyeing": {"label": "🧵 DYE BATH JET TANKS", "color": "#9c27b0", "note": "High constant fluid volume integration."},
    "Pharmaceutical Synthesis": {"label": "💊 REACTOR JACKET HEATING", "color": "#009688", "note": "FDA-validated clean piping paths."},
    "Chemical Manufacturing": {"label": "⚗️ BATCH WASHING STATIONS", "color": "#ff9800", "note": "Explosion-proof classification requirements."}
}
current_ind = industry_specs[industry_type]

# 🔢 CORE THERMODYNAMIC & HEAT LOSS COEFFICIENT MATH
cp = 4.186            # Specific heat capacity of water (kJ/kg·K)
module_area = 7.2     # m² area per solar module
eta_0 = 0.82          # Optical efficiency intercept

num_covers = 1          
emittance_plate = 0.95  
emittance_glass = 0.88  

t_plate = ((tout + tin) / 2)
t_plate_k = t_plate + 273.15
t_ambient_k = ambient_temp + 273.15
tilt_rad = math.radians(latitude)

# Hottel-Woertz-Klein top loss equations
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

# Reduced Temperature Parameter (X_SD) Calculation
nominal_irradiance = 800.0 # W/m² design reference peak insolation
x_sd_current = (t_plate - ambient_temp) / nominal_irradiance

collector_efficiency = eta_0 - (u_total_loss * x_sd_current)
collector_efficiency = max(0.35, min(collector_efficiency, 0.75)) 
nominal_yield_per_m2 = 4.5 
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
st.markdown('<h3 class="section-header">📋 I. Engineering Sizing Specifications</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">🔥 NET THERMAL LOAD</div><div class="metric-value">⚡ {net_energy_demand:.1f} <span style="font-size:12px;">kWh/Day</span></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">🧩 TOTAL SOLAR MODULES</div><div class="metric-value">🧩 {modules} <span style="font-size:12px;">Units</span></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">📐 TOTAL FIELD AREA</div><div class="metric-value">🗺️ {total_collector_area:.1f} <span style="font-size:12px;">m²</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #457b9d;"><div class="metric-title">💧 LOOP DESIGN FLOW</div><div class="metric-value">🌊 {flow_lpm:.1f} <span style="font-size:12px;">LPM</span></div></div>', unsafe_allow_html=True)

# SECTION 2: BALANCE OF PLANT LAYOUT DETAILS
st.markdown(f'<h3 class="section-header">⚙️ II. Balance of Plant (BOP) & Structural Layout — Profile: {industry_type}</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #fff3cd;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#b58900; font-size:14px;">📦 Tank & Storage Sizing</h4>
        <div style="background-color:#fff3cd; padding:5px; border-radius:4px; font-weight:bold; color:#856404; text-align:center; margin-bottom:8px; font-size:12px;">
            Tank Capacity: {storage_tank_capacity:,.0f} Liters
        </div>
        <span style="font-size:12px;">• <b>Material Spec:</b> SS314 / SS316 L Vessel<br>
        • <b>Insulation:</b> 100mm High-Density Rockwool / PUF<br>
        • <b>Loss Profile:</b> &lt; 2°C standing loss / 24h</span>
    </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #f8d7da;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#d9534f; font-size:14px;">🗺️ Array Field Configuration</h4>
        <div style="background-color:#f8d7da; padding:5px; border-radius:4px; font-weight:bold; color:#721c24; text-align:center; margin-bottom:8px; font-size:12px;">
            Layout: {total_banks} Banks Parallel
        </div>
        <span style="font-size:12px;">• <b>Series Density:</b> {modules_per_bank} Units per Bank<br>
        • <b>Header Piping:</b> DN40 / DN50 Copper Piping<br>
        • <b>Balancing Valves:</b> Needed on parallel returns</span>
    </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #d4edda;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#5cb85c; font-size:14px;">🎛️ Automation & Integration</h4>
        <div style="background-color:#d4edda; padding:5px; border-radius:4px; font-weight:bold; color:#155724; text-align:center; margin-bottom:8px; font-size:12px;">
            Primary Loop Pump: {pump_hp} VFD Pump
        </div>
        <span style="font-size:12px;">• <b>Integration Note:</b> {current_ind['note']}<br>
        • <b>Telemetry:</b> RS485 Modbus plant SCADA link<br>
        • <b>Safety Valve:</b> Integrated Temp & Pressure Relief</span>
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: COMMERCIAL VIABILITY ANALYSIS
st.markdown('<h3 class="section-header">💰 III. Commercial Proposal & Financial Viability Analysis</h3>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #1d3557;"><div class="metric-title">🏗️ TOTAL TURNKEY CAPEX</div><div class="metric-value">₹ {turnkey_capex:,.0f}</div></div>', unsafe_allow_html=True)
with f2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">📉 ANNUAL UTILITY SAVINGS</div><div class="metric-value">₹ {annual_monetary_savings:,.0f}</div></div>', unsafe_allow_html=True)
with f3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e9c46a;"><div class="metric-title">⏳ SIMPLE PAYBACK PERIOD</div><div class="metric-value">{simple_payback_years:.2f} <span style="font-size:12px;">Years</span></div></div>', unsafe_allow_html=True)
with f4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e76f51;"><div class="metric-title">📈 INTERNAL RATE OF RETURN (ROI)</div><div class="metric-value">{roi_percent:.1f} %</div></div>', unsafe_allow_html=True)

# SECTION 4: ADVANCED ENGINEERING CHARTS
st.markdown('<h3 class="section-header">📊 IV. Process Performance Curves & Environmental Modeling</h3>', unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    x_vals = np.linspace(0, 0.12, 100)
    eta_vals = eta_0 - (u_total_loss * x_vals)
    eta_vals = np.clip(eta_vals, 0.10, 0.85) * 100
    
    fig_efficiency = go.Figure()
    fig_efficiency.add_trace(go.Scatter(
        x=x_vals, y=eta_vals, mode='lines',
        name='Collector Efficiency',
        line=dict(color='#0f52ba', width=2.5)
    ))
    fig_efficiency.add_trace(go.Scatter(
        x=[x_sd_current], y=[collector_efficiency * 100],
        mode='markers+text', name='Design Point',
        text=[f"Design Target ({collector_efficiency*100:.1f}%)"],
        textposition="top right",
        marker=dict(color='#e63946', size=10, symbol='diamond', line=dict(color='black', width=1))
    ))
    
    fig_efficiency.update_layout(
        title="🎯 Efficiency Curve vs. Reduced Temperature Diff (X_SD)",
        xaxis_title="Reduced Temp Parameter X_SD [(T_plate - T_amb) / I]",
        yaxis_title="Thermal Capture Efficiency (η %)",
        xaxis=dict(gridcolor='#e9ecef', range=[0, 0.12]),
        yaxis=dict(gridcolor='#e9ecef', range=[0, 90]),
        plot_bgcolor='white', height=240, margin=dict(l=30, r=30, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)

with chart_col2:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_numbers = [17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318, 344]
    
    calculated_radiation_wm2 = []
    for n in day_numbers:
        declination = 23.45 * math.sin(math.radians(360 * (284 + n) / 365))
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        cos_zenith = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad)
        extraterrestrial = 1367 * (1 + 0.033 * math.cos(math.radians(360 * n / 365)))
        
        peak_intensity = extraterrestrial * max(0.1, cos_zenith) * 0.58
        calculated_radiation_wm2.append(min(950.0, max(350.0, peak_intensity)))
        
    fig_radiation = go.Figure()
    fig_radiation.add_trace(go.Bar(
        x=months, y=calculated_radiation_wm2,
        name='Peak Insolation Intensity',
        marker_color='#f4a261', opacity=0.85,
        marker_line=dict(color='#e76f51', width=1)
    ))
    
    fig_radiation.update_layout(
        title=f"☀️ Site Annual Clear-Sky Peak Radiation Profile ({latitude}° N/S)",
        xaxis_title="Calendar Operating Month",
        yaxis_title="Peak Insolation Intensity I (W/m²)",
        yaxis=dict(gridcolor='#e9ecef', range=[0, 1000]), 
        plot_bgcolor='white', height=240, margin=dict(l=30, r=30, t=40, b=30)
    )
    st.plotly_chart(fig_radiation, use_container_width=True)


# SECTION 5: COMPACT P&ID BLUEPRINT DRAWING WITH INLINE BLUEPRINT INDEX
st.markdown('<h3 class="section-header">📐 V. Live Schematic & Process Flow Blueprint (P&ID Based)</h3>', unsafe_allow_html=True)

st.graphviz_chart(f"""
digraph G {{
    size="12,4.2!";
    ratio="fill";
    rankdir=LR;
    splines=ortho;
    nodesep=0.18;
    ranksep=0.28;
    
    node [fontname="Helvetica", fontsize=8, penwidth=1.0];
    edge [fontname="Helvetica-Bold", fontsize=7, penwidth=1.0];

    # Piping Valves & Graphics
    node [shape=triangle, fixedsize=true, width=0.18, height=0.12, style=filled, fillcolor="#b0bec5", color="#37474f"];
    valv_in [label=""]; valv_out [label=""]; valv_ret [label=""]; valv_by [label=""];
    
    node [shape=diamond, fixedsize=true, width=0.18, height=0.18, fillcolor="#eceff1", label="Y"];
    strainer [label=""];

    # Instruments
    node [shape=circle, fixedsize=true, width=0.42, style=filled, fillcolor="#e0f7fa", color="#006064", fontname="Helvetica-Bold", fontsize=7];
    LT_101 [label="LT\\n101"];
    TT_101 [label="TT\\n101"];
    TT_102 [label="TT\\n102"];
    PT_101 [label="PT\\n101"];
    FT_101 [label="FT\\n101"];
    TIC_101 [label="TIC\\n101", fillcolor="#fff9c4", color="#f57f17"];

    # Plant Vessels & Equipment
    node [shape=box, style="filled,rounded", width=1.0, height=0.65, color="#0f52ba", fillcolor="#f8f9fa", fontsize=8];
    Inlet [label="📥 COLD INLET\\n({tin}°C Feed)", shape=cds, fillcolor="#e3f2fd"];
    
    subgraph cluster_solar {{
        label="☀️ SOLAR FIELD ({total_banks} Banks)";
        color="#c62828"; style="dashed,rounded"; bgcolor="#fffde7"; fontsize=7;
        Array_A [label="BANK A\\n({modules_per_bank} Mod)", fillcolor="#ffebee", color="#e53935", width=0.8, height=0.45];
        Array_B [label="BANK B\\n({max(1, modules-modules_per_bank)} Mod)", fillcolor="#ffebee", color="#e53935", width=0.8, height=0.45];
    }}

    Tank [label="🛢 Storage Tank\\nTK-101\\n({storage_tank_capacity:,.0f} L)", shape=cylinder, fillcolor="#fff3cd", color="#f9a825", width=0.8, height=1.3];
    Boiler [label="🔥 BOILER\\n({aux_fuel_type})", fillcolor="#eceff1", color="#37474f"];
    
    # 🌟 Dynamic Target Industrial Destination Node
    Process [label="{current_ind['label']}\\n({tout}°C Hot Load)", shape=cds, fillcolor="{current_ind['color']}", color="#1c1c1e"];

    node [shape=component, width=0.35, height=0.28, fillcolor="#e8f5e9", color="#2e7d32"];
    Pump_P1 [label="P-1\\n({pump_hp})"];
    Pump_P2 [label="P-2"];

    # 📋 INTEGRATED COMPACT SYMBOL INDEX LEGEND MATRIX
    node [shape=plaintext, width=2.0, height=2.5, style=none, color=none];
    LegendIndex [label=<
        <table border="1" cellborder="1" cellspacing="0" cellpadding="2" bgcolor="#fdfefe" color="#2c3e50">
            <tr><td colspan="2" bgcolor="#1d3557"><font color="white" size="1"><b>P&amp;ID SYMBOL INDEX</b></font></td></tr>
            <tr><td bgcolor="#e0f7fa" size="1"><b>LT/TT</b></td><td align="left" size="1">Level / Temp Trans.</td></tr>
            <tr><td bgcolor="#fff9c4" size="1"><b>TIC</b></td><td align="left" size="1">Temp Controller PLC</td></tr>
            <tr><td bgcolor="#b0bec5" size="1"><b>▶◀</b></td><td align="left" size="1">Ball Valve</td></tr>
            <tr><td bgcolor="#fff3cd" size="1"><b>TK101</b></td><td align="left" size="1">Storage Tank</td></tr>
            <tr><td bgcolor="#e8f5e9" size="1"><b>P-1</b></td><td align="left" size="1">Circulation Pump</td></tr>
        </table>
    >];

    # --- FLOW PIPING ---
    Inlet -> strainer [color="#0f52ba"];
    strainer -> valv_in [color="#0f52ba"];
    valv_in -> Tank [color="#0f52ba"];
    Tank -> LT_101 [style=dotted, color="#546e7a", arrowhead=none];

    Tank -> Pump_P1 [color="#0f52ba"];
    Pump_P1 -> Array_A [color="#0f52ba", label=" {flow_kghr:.0f} kg/h"];
    Pump_P1 -> Array_B [color="#0f52ba"];
    
    Array_A -> TT_101 [color="#c62828"];
    Array_B -> TT_101 [color="#c62828"];
    TT_101 -> PT_101 [color="#c62828"];
    PT_101 -> valv_out [color="#c62828"];
    valv_out -> Tank [color="#c62828"];

    Tank -> Pump_P2 [color="#c62828"];
    Pump_P2 -> TT_102 [color="#c62828"];
    TT_102 -> valv_ret [color="#c62828"];
    
    valv_ret -> Boiler [color="#c62828"];
    valv_ret -> valv_by [color="#f9a825"];
    valv_by -> Tank [color="#f9a825"];
    
    Boiler -> FT_101 [color="#c62828"];
    FT_101 -> Process [color="#c62828"];

    # --- CONTROLS ---
    edge [style=dashed, color="#757575", penwidth=0.8, arrowhead=dot];
    TT_101 -> TIC_101;
    TT_102 -> TIC_101;
    TIC_101 -> Pump_P1;
    TIC_101 -> valv_ret;

    {{ rank=same; Process; LegendIndex; }}
}}
""")

# SECTION 6: PLANT OPERATIONS SAVINGS SUMMARY TABLE
st.markdown('<h3 class="section-header">🎛️ VI. Operational Parametric Telemetry Status</h3>', unsafe_allow_html=True)
st.markdown(f"""
| Industrial Flow Management Parameter | Operational Controller Telemetry Status Data |
| :--- | :--- |
| **Active Integration Target Application Profile** | ⚙️ **{industry_type.upper()} FLOW MANIFEST** |
| **Current Controller Target State** | 🔴 **MAX VELOCITY** ({flow_kghr:.1f} kg/hr System Design Limit) |
| **Profile Logic Strategy** | *"Instant Extraction"* (VFD Target Lock Loop) |
| **Calculated Top Loss Coefficient ($U_t$)** | 🌡️ **{u_top:.2f} W/m²·K** (Dynamically responsive via Hottel-Woertz-Klein equations) |
| **Total Thermal Field Loss Rate ($U_L$)** | 📉 **{u_total_loss:.2f} W/m²·K** |
| **Calculated Design-Basis Parameter ($X_{{SD}}$)** | 📏 **{x_sd_current:.5f}** Normalized Reduced Fluid Temperature Drop Metric |
| **Displaced Fuel Utility Consumption** | 🚰 **{fuel_saved_annual:,.1f} {selected_fuel['unit']}/year** of {aux_fuel_type} cut from plant ledger |
| **Annual Carbon Intensity Offset** | 🍃 **{co2_reduction_tons:.1f} Metric Tons of CO₂** mitigated per annum |
""", unsafe_allow_html=True)