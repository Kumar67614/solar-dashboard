import streamlit as st
import plotly.graph_objects as go
import math
import numpy as np

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

st.title("🏭 SQS Industrial Solar Water Heating Design & Proposal Engine")
st.markdown("##### Enterprise-Grade Sizing, Balance of Plant (BOP) Configuration & Financial Feasibility")
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
    st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">🔥 NET THERMAL LOAD</div><div class="metric-value">⚡ {net_energy_demand:.1f} <span style="font-size:14px;">kWh/Day</span></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">🧩 TOTAL SOLAR MODULES</div><div class="metric-value">🧩 {modules} <span style="font-size:14px;">Units</span></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">📐 TOTAL FIELD AREA</div><div class="metric-value">🗺️ {total_collector_area:.1f} <span style="font-size:14px;">m²</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #457b9d;"><div class="metric-title">💧 LOOP DESIGN FLOW</div><div class="metric-value">🌊 {flow_lpm:.1f} <span style="font-size:14px;">LPM</span></div></div>', unsafe_allow_html=True)

# SECTION 2: BALANCE OF PLANT LAYOUT DETAILS
st.markdown('<h3 class="section-header">⚙️ II. Balance of Plant (BOP) & System Architecture</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #fff3cd;">
        <h4 style="margin-top:0; color:#b58900;">📦 Tank & Storage Sizing</h4>
        <div style="background-color:#fff3cd; padding:8px; border-radius:5px; font-weight:bold; color:#856404; text-align:center; margin-bottom:10px; font-size:13px;">
            Recommended Tank Capacity: {storage_tank_capacity:,.0f} Liters
        </div>
        • <b>Material Spec:</b> SS314 / SS316 L Inner Vessel<br>
        • <b>Insulation:</b> 100mm High-Density Rockwool or PUF Injection<br>
        • <b>Loss Performance:</b> &lt; 2°C standing loss per 24 hours
    </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #f8d7da;">
        <h4 style="margin-top:0; color:#d9534f;">🗺️ Array Field Configuration</h4>
        <div style="background-color:#f8d7da; padding:8px; border-radius:5px; font-weight:bold; color:#721c24; text-align:center; margin-bottom:10px; font-size:13px;">
            Hydraulic Array Layout: {total_banks} Banks Parallel
        </div>
        • <b>Modules in Series per Bank:</b> {modules_per_bank} Units<br>
        • <b>Interconnecting Header Piping:</b> DN40 / DN50 Copper or Composite Piping<br>
        • <b>Balancing Valves:</b> Needed on each parallel bank return loop to prevent short-circuiting.
    </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #d4edda;">
        <h4 style="margin-top:0; color:#5cb85c;">🎛️ Automation & Controls Integration</h4>
        <div style="background-color:#d4edda; padding:8px; border-radius:5px; font-weight:bold; color:#155724; text-align:center; margin-bottom:10px; font-size:13px;">
            Primary Loop Pump: {pump_hp} VFD High-Temp Pump
        </div>
        • <b>Differential Temp Controller (DTC):</b> Modulating logic loops based on collector manifold outputs.<br>
        • <b>Telemetry:</b> RS485 Modbus connectivity matching standard plant SCADA systems.
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
    st.markdown(f'<div class="metric-container" style="border-top-color: #e9c46a;"><div class="metric-title">⏳ SIMPLE PAYBACK PERIOD</div><div class="metric-value">{simple_payback_years:.2f} <span style="font-size:14px;">Years</span></div></div>', unsafe_allow_html=True)
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
        name='Collector Efficiency Characteristic',
        line=dict(color='#0f52ba', width=3)
    ))
    fig_efficiency.add_trace(go.Scatter(
        x=[x_sd_current], y=[collector_efficiency * 100],
        mode='markers+text', name='Current Plant Design Point',
        text=[f"Design Target ({collector_efficiency*100:.1f}%)"],
        textposition="top right",
        marker=dict(color='#e63946', size=12, symbol='diamond', line=dict(color='black', width=1.5))
    ))
    
    fig_efficiency.update_layout(
        title="🎯 Collector Efficiency Curve vs. Reduced Temperature Diff (X_SD)",
        xaxis_title="Reduced Temperature Difference Parameter X_SD [(T_plate - T_amb) / I]",
        yaxis_title="Thermal Capture Efficiency (η %)",
        xaxis=dict(gridcolor='#e9ecef', range=[0, 0.12]),
        yaxis=dict(gridcolor='#e9ecef', range=[0, 90]),
        plot_bgcolor='white', height=360, margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)

with chart_col2:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_numbers = [17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318, 344]
    
    calculated_radiation = []
    for n in day_numbers:
        declination = 23.45 * math.sin(math.radians(360 * (284 + n) / 365))
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        cos_omega_s = -math.tan(lat_rad) * math.tan(dec_rad)
        cos_omega_s = max(-1.0, min(1.0, cos_omega_s))
        omega_s = math.acos(cos_omega_s)
        
        ho = (24 * 3600 * 1367 / math.pi) * (1 + 0.033 * math.cos(math.radians(360 * n / 365))) * (
            math.cos(lat_rad) * math.cos(dec_rad) * math.sin(omega_s) + omega_s * math.sin(lat_rad) * math.sin(dec_rad)
        )
        ho_kwh_m2 = ho / 3.6e6 
        calculated_radiation.append(ho_kwh_m2 * 0.52) 
        
    fig_radiation = go.Figure()
    fig_radiation.add_trace(go.Bar(
        x=months, y=calculated_radiation,
        name='Global Insolation Profile',
        marker_color='#f4a261', opacity=0.85,
        marker_line=dict(color='#e76f51', width=1.5)
    ))
    
    fig_radiation.update_layout(
        title=f"☀️ Site Annual Clear-Sky Radiation Profile ({latitude}° N/S Coordinates)",
        xaxis_title="Calendar Operating Month",
        yaxis_title="Daily Global Horizontal Insolation Avg (kWh/m²/day)",
        yaxis=dict(gridcolor='#e9ecef', range=[0, 8.5]),
        plot_bgcolor='white', height=360, margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(fig_radiation, use_container_width=True)


# SECTION 5: STANDARD CONSTRAINED P&ID BLUEPRINT DRAWING WITH INLINE BLUEPRINT INDEX
st.markdown('<h3 class="section-header">📐 V. Live Schematic & Process Flow Blueprint (P&ID Based)</h3>', unsafe_allow_html=True)
st.markdown("This schematic matches standard industrial water heating loops. An integrated engineering index is embedded on the far right side of the constrained layout canvas.")

st.graphviz_chart(f"""
digraph G {{
    # Compact Blueprint Canvas Settings (ANSI B Standard Constraint Geometry)
    size="12,6.0!";
    ratio="fill";
    rankdir=LR;
    splines=ortho;
    nodesep=0.22;
    ranksep=0.32;
    
    node [fontname="Helvetica", fontsize=8, penwidth=1.2];
    edge [fontname="Helvetica-Bold", fontsize=7, penwidth=1.2];

    # Inline Piping Components & Valve Graphics
    node [shape=triangle, fixedsize=true, width=0.22, height=0.14, style=filled, fillcolor="#b0bec5", color="#37474f"];
    valv_in [label=""]; valv_out [label=""]; valv_ret [label=""]; valv_by [label=""];
    
    node [shape=diamond, fixedsize=true, width=0.22, height=0.22, fillcolor="#eceff1", label="Y"];
    strainer [label=""];

    # ISA Standard Instrument Circles (Transmitters & Controllers)
    node [shape=circle, fixedsize=true, width=0.48, style=filled, fillcolor="#e0f7fa", color="#006064", fontname="Helvetica-Bold", fontsize=7];
    LT_101 [label="LT\\n101"];
    TT_101 [label="TT\\n101"];
    TT_102 [label="TT\\n102"];
    PT_101 [label="PT\\n101"];
    FT_101 [label="FT\\n101"];
    TIC_101 [label="TIC\\n101", fillcolor="#fff9c4", color="#f57f17"];

    # Plant Vessels & Heavy Equipment Modules
    node [shape=box, style="filled,rounded", width=1.2, height=0.75, color="#0f52ba", fillcolor="#f8f9fa", fontsize=8];
    Inlet [label="📥 COLD INLET\\n({tin}°C Feed)", shape=cds, fillcolor="#e3f2fd"];
    
    subgraph cluster_solar {{
        label="☀️ SOLAR RECOVERY ARRAY FIELD\\n({total_banks} Parallel Banks @ {latitude}° Tilt)";
        color="#c62828"; style="dashed,rounded"; bgcolor="#fffde7"; fontsize=8;
        Array_A [label="BANK A\\n({modules_per_bank} Modules)", fillcolor="#ffebee", color="#e53935", width=1.0, height=0.55];
        Array_B [label="BANK B\\n({max(1, modules-modules_per_bank)} Modules)", fillcolor="#ffebee", color="#e53935", width=1.0, height=0.55];
    }}

    Tank [label="🛢 Storage Tank\\nTK-101\\n({storage_tank_capacity:,.0f} L)", shape=cylinder, fillcolor="#fff3cd", color="#f9a825", width=1.0, height=1.6];
    Boiler [label="🔥 BACKUP BOILER\\n({aux_fuel_type} Trim)", fillcolor="#eceff1", color="#37474f"];
    Process [label="🏭 FACTORY LOAD\\n({tout}°C Hot Demand)", shape=cds, fillcolor="#e8f5e9", color="#2e7d32"];

    node [shape=component, width=0.45, height=0.35, fillcolor="#e8f5e9", color="#2e7d32"];
    Pump_P1 [label="P-1\\n({pump_hp})"];
    Pump_P2 [label="P-2\\n(Boost)"];

    # 📋 INTEGRATED STANDARD BLUEPRINT INDEX LEGEND MATRIX
    node [shape=plaintext, width=2.2, height=3.5, style=none, color=none];
    LegendIndex [label=<
        <table border="1" cellborder="1" cellspacing="0" cellpadding="3" bgcolor="#fdfefe" color="#2c3e50">
            <tr><td colspan="2" bgcolor="#1d3557"><font color="white"><b>P&amp;ID SYMBOL INDEX</b></font></td></tr>
            <tr><td bgcolor="#e0f7fa"><b>LT / TT</b></td><td align="left">Level / Temp Transmitter</td></tr>
            <tr><td bgcolor="#e0f7fa"><b>PT / FT</b></td><td align="left">Pressure / Flow Transmitter</td></tr>
            <tr><td bgcolor="#fff9c4"><b>TIC</b></td><td align="left">Temp Indicator Controller (PLC)</td></tr>
            <tr><td bgcolor="#b0bec5"><b>▶◀</b></td><td align="left">Isolation / Control Ball Valve</td></tr>
            <tr><td bgcolor="#eceff1"><b>❖ (Y)</b></td><td align="left">Inline Mesh Y-Strainer Filter</td></tr>
            <tr><td bgcolor="#ffebee"><b>Array</b></td><td align="left">Glazed Flat Plate Solar Collectors</td></tr>
            <tr><td bgcolor="#fff3cd"><b>TK-101</b></td><td align="left">SS316 Isolated Thermal Storage</td></tr>
            <tr><td bgcolor="#e8f5e9"><b>P-1 / P-2</b></td><td align="left">Centrifugal Mechanical Circulation Pump</td></tr>
            <tr><td colspan="2" bgcolor="#eaeded"><i>System Basis: ISA-S5.1 Standard Instrumentation</i></td></tr>
        </table>
    >];

    # --- PROCESS PIPING AND HYDRAULICS LOOP FLOW ---
    Inlet -> strainer [color="#0f52ba"];
    strainer -> valv_in [color="#0f52ba"];
    valv_in -> Tank [color="#0f52ba", label=" Makeup"];
    Tank -> LT_101 [style=dotted, color="#546e7a", arrowhead=none];

    # Primary Heat Collection Loop
    Tank -> Pump_P1 [color="#0f52ba", label=" Suction"];
    Pump_P1 -> Array_A [color="#0f52ba", label=" Return Loop:\\n{flow_kghr:.0f} kg/hr"];
    Pump_P1 -> Array_B [color="#0f52ba"];
    
    Array_A -> TT_101 [color="#c62828"];
    Array_B -> TT_101 [color="#c62828"];
    TT_101 -> PT_101 [color="#c62828"];
    PT_101 -> valv_out [color="#c62828"];
    valv_out -> Tank [color="#c62828", label=" Thermal Harvest"];

    # Plant Forward Supply Line Loop
    Tank -> Pump_P2 [color="#c62828", label=" Delivery Line"];
    Pump_P2 -> TT_102 [color="#c62828"];
    TT_102 -> valv_ret [color="#c62828"];
    
    valv_ret -> Boiler [color="#c62828", label=" Forward Feed"];
    valv_ret -> valv_by [color="#f9a825", label=" Recirc Loop"];
    valv_by -> Tank [color="#f9a825"];
    
    Boiler -> FT_101 [color="#c62828"];
    FT_101 -> Process [color="#c62828", label=" Production Feed"];

    # --- AUTOMATION CONTROL INTERCONNECTS ---
    edge [style=dashed, color="#757575", penwidth=1, arrowhead=dot];
    TT_101 -> TIC_101 [label=" PV1"];
    TT_102 -> TIC_101 [label=" PV2"];
    TIC_101 -> Pump_P1 [label=" VFD"];
    TIC_101 -> valv_ret [label=" Modulate"];

    # Fix Layout Alignment of Index Block to right boundary edge
    {{ rank=same; Process; LegendIndex; }}
}}
""")

# SECTION 6: PLANT OPERATIONS SAVINGS SUMMARY TABLE
st.markdown('<h3 class="section-header">🎛️ VI. Operational Parametric Telemetry Status</h3>', unsafe_allow_html=True)
st.markdown(f"""
| Industrial Flow Management Parameter | Operational Controller Telemetry Status Data |
| :--- | :--- |
| **Current Controller Target State** | 🔴 **MAX VELOCITY** ({flow_kghr:.1f} kg/hr System Design Limit) |
| **Profile Logic Strategy** | *"Instant Extraction"* (VFD Target Lock Loop) |
| **Calculated Top Loss Coefficient ($U_t$)** | 🌡️ **{u_top:.2f} W/m²·K** (Dynamically responsive via Hottel-Woertz-Klein equations) |
| **Total Thermal Field Loss Rate ($U_L$)** | 📉 **{u_total_loss:.2f} W/m²·K** (Combined top, edge, and rear structural conduction losses) |
| **Calculated Design-Basis Parameter ($X_{{SD}}$)** | 📏 **{x_sd_current:.5f}** Normalized Reduced Fluid Temperature Drop Metric |
| **Displaced Fuel Utility Consumption** | 🚰 **{fuel_saved_annual:,.1f} {selected_fuel['unit']}/year** of {aux_fuel_type} cut from plant ledger |
| **Annual Carbon Intensity Offset** | 🍃 **{co2_reduction_tons:.1f} Metric Tons of CO₂** mitigated per annum |
""", unsafe_allow_html=True)