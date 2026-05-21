import streamlit as st
import plotly.graph_objects as go
import math
import numpy as np
import pandas as pd

# 🎨 Premium Compact Styling & Border Matrix Boundaries
st.set_page_config(layout="wide", page_title="SQS SHIP Analyzer")
st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 6px;
        border-top: 4px solid #0f52ba;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 12px;
        border-left: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef;
        border-bottom: 1px solid #e9ecef;
    }
    .metric-title { font-size: 11px; color: #4a5568; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 4px;}
    .metric-value { font-size: 22px; color: #1a202c; font-weight: bold; }
    .section-header { color: #0f52ba; font-weight: bold; border-bottom: 2px solid #0f52ba; padding-bottom: 4px; margin-top: 20px; margin-bottom: 12px;}
    .card-box { background: #ffffff; padding: 15px; border-radius: 6px; box-shadow: 0 1px 5px rgba(0,0,0,0.05); margin-bottom: 12px; border: 1px solid #e9ecef; }
    div.block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 SQS Industrial Solar Process Heat (SHIP) Sizing & Economic Analyzer")
st.markdown("---")

# 🖥️ SIDEBAR INPUTS (Fully Responsive State Providers)
st.sidebar.header("🏭 1. Application & Industry Type")
industry_type = st.sidebar.selectbox(
    "Select Industrial Sector", 
    ["Dairy Plant (Pasteurization/CIP)", "Textile Dyeing Mills", "Pharmaceutical Synthesis", "Thermal Power Pre-Heating", "Chemical Processing Tank"]
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 2. Process Design Thermal Load")
water = st.sidebar.number_input("Daily Water Consumption (Liters/Day)", value=8000, step=500, min_value=500)
tout = st.sidebar.number_input("Required Process Delivery Temp (Tout °C)", value=90, min_value=30, max_value=100)
tin = st.sidebar.number_input("Initial Water Inlet Temp (Tin °C)", value=25, min_value=5, max_value=50)

st.sidebar.markdown("---")
st.sidebar.header("🌍 3. Site Weather Parameters")
latitude = st.sidebar.number_input("Local Site Latitude (Degrees)", value=18.5, min_value=0.0, max_value=60.0, step=0.1)
wind_speed = st.sidebar.slider("Design Wind Velocity (m/s)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
ambient_temp = st.sidebar.slider("Design Ambient Temp (°C)", min_value=0, max_value=45, value=25, step=1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 4. Balance of Plant (BOP) Constants")
pipe_loss_factor = st.sidebar.slider("Estimated Piping Thermal Loss (%)", min_value=2, max_value=15, value=5, step=1)
tank_safety_margin = st.sidebar.slider("Storage Tank Safety Factor", min_value=1.1, max_value=1.4, value=1.20, step=0.05)
aux_fuel_type = st.sidebar.selectbox("Backup Boiler Fuel Type", ["Furnace Oil (FO)", "Diesel (HSD)", "Natural Gas", "Electricity"])

st.sidebar.markdown("---")
st.sidebar.header("💰 5. Fuel Cost & Investment Rates")
fuel_cost = st.sidebar.number_input("Current Fuel Price (₹ / Unit)", value=85.0, step=5.0)
project_cost_per_m2 = st.sidebar.number_input("Estimated Turnkey Cost (₹ / m²)", value=14000, step=500)

# 📊 6. DATA VALIDATION ENGINE FOR SQS FIELD LOGS
st.sidebar.markdown("---")
st.sidebar.header("📊 6. Operational Log Field Validation")
log_mode = st.sidebar.radio("Validation Data Source", ["Use Pre-loaded SQS Logs", "Upload Custom Log (CSV)", "None (Simulation Only)"])

available_logs = {
    "Log: 60°C Target (Feb 06, 2026)": "60_06-02-2026_SQS.csv",
    "Log: 60°C Target (Feb 11, 2026)": "60_11-02-2026_SQS.csv",
    "Log: 60°C Target (Jan 28, 2026)": "28-01-2026_SQS_Jan28_60.csv",
    "Log: 70°C Target (Feb 10, 2026)": "70_10-02-2026_SQS.csv",
    "Log: 70°C Target (Jan 27, 2026)": "27-01-2026_SQS_70.csv",
    "Log: 80°C Target (Feb 18, 2026)": "80_18-02-2026_SQS.csv",
    "Log: 80°C Target (Feb 12, 2026)": "80__12-02-2026_SQS.csv",
    "Log: 80°C Target (Nov 24, 2025)": "80_24-11-2025_SQS.csv",
    "Log: 80°C Target (Jan 24, 2026)": "24-01-2026_SQS_80.csv",
    "Log: 90°C Target (Feb 09, 2026)": "90_09-02-2026_SQS_.csv",
    "Log: 90°C Target (Feb 13, 2026)": "90_13-02-2026_SQS.csv",
    "Log: 100°C Target (Nov 18, 2025)": "100_18.11.25_SQS.csv",
    "Log: High Flow Dynamic Test (Feb 16, 2026)": "SQS_16-02-2026.csv",
    "Log: Fluid Stability Verification (Feb 05, 2026)": "05-02-2026_SQS.csv"
}

df_log = None
if log_mode == "Use Pre-loaded SQS Logs":
    selected_log_label = st.sidebar.selectbox("Choose Field Test Dataset", list(available_logs.keys()))
    try:
        df_log = pd.read_csv(available_logs[selected_log_label], encoding='utf-8', errors='ignore')
    except Exception as e:
        st.sidebar.warning(f"File log selection idle or unreadable. Error: {e}")
elif log_mode == "Upload Custom Log (CSV)":
    uploaded_file = st.sidebar.file_uploader("Upload SQS Operational Log (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            df_log = pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
        except Exception as e:
            st.sidebar.error(f"Error parsing file: {e}")

# 🏭 INDUSTRY DYNAMIC CONFIGURATION MAPPING
industry_specs = {
    "Dairy Plant (Pasteurization/CIP)": {"label": "🍼 DAIRY PLANT LOAD\\n(Pasteurization & CIP)", "color": "#2196f3", "note": "Uses food-grade sanitary SS316L heat exchangers for product isolation."},
    "Textile Dyeing Mills": {"label": "🧵 TEXTILE DYEING MILLS\\n(Dye Bath Pre-Heating)", "color": "#9c27b0", "note": "High continuous volume process. Ideal for baseline heat recovery integration."},
    "Pharmaceutical Synthesis": {"label": "💊 PHARMACEUTICAL REACTOR\\n(Jacket Heating Loop)", "color": "#009688", "note": "Strict FDA-compliant clean piping layouts with precise temperature control loops."},
    "Thermal Power Pre-Heating": {"label": "⚡ THERMAL POWER PLANT\\n(Deaerator Feedwater Pre-Heat)", "color": "#ff9800", "note": "High-pressure operating design. Demineralized feed water requires specialized alloys."},
    "Chemical Processing Tank": {"label": "⚗️ CHEMICAL PROCESS TANK\\n(Batch Reaction Heating)", "color": "#e53935", "note": "Explosion-proof components and hazardous area classifications are standard."}
}
current_ind = industry_specs[industry_type]

# =========================================================
# 🔢 CALCULATIONS TIER (Completely Dynamic & Interconnected)
# =========================================================
cp = 4.186            # kJ/kg·K
module_area = 7.2     # m² per module
eta_0 = 0.82          

num_covers = 1          
emittance_plate = 0.95  
emittance_glass = 0.88  

t_plate = ((tout + tin) / 2)
t_plate_k = t_plate + 273.15
t_ambient_k = ambient_temp + 273.15

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

nominal_irradiance = 800.0  
x_sd_current = (t_plate - ambient_temp) / nominal_irradiance

collector_efficiency = eta_0 - (u_total_loss * x_sd_current)
collector_efficiency = max(0.35, min(collector_efficiency, 0.75))
nominal_yield_per_m2 = 4.5  
module_energy = nominal_yield_per_m2 * module_area * collector_efficiency

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
    pipe_size_dn = "DN32"
elif flow_lpm < 50:
    pump_hp = "3.0 HP"
    pipe_size_dn = "DN40"
else:
    pump_hp = "5.0 HP"
    pipe_size_dn = "DN50"

# 🌿 ACCURATE MEASURED REGIONAL METEOROLOGICAL RAD PROFILE (kWh/m²/day)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
measured_radiation = [5.33, 6.05, 6.72, 7.14, 7.21, 5.02, 3.84, 3.92, 5.11, 5.45, 5.18, 4.95]

# 🌿 ECONOMIC ANALYSIS CALCS
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
else:
    fuel_saved_annual = (annual_thermal_load_kwh * 860) / (selected_fuel["calorific"] * selected_fuel["eff"])

co2_reduction_tons = (fuel_saved_annual * selected_fuel["co2"]) / 1000
annual_monetary_savings = fuel_saved_annual * fuel_cost
turnkey_capex = total_collector_area * project_cost_per_m2
simple_payback_years = turnkey_capex / annual_monetary_savings if annual_monetary_savings > 0 else 0
roi_percent = (annual_monetary_savings / turnkey_capex) * 100 if turnkey_capex > 0 else 0


# =========================================================
# 🧪 PARSING FIELD DATA (IF PROVIDED)
# =========================================================
log_uploaded = False
reg_x = [0.015, 0.032, 0.048, 0.065, 0.082, 0.098]
reg_y = [74.2, 66.8, 59.1, 51.3, 44.0, 35.6]
log_metrics = {}

def find_flexible_column(col_list, search_keywords):
    for keyword in search_keywords:
        for original_col in col_list:
            if keyword.lower() in original_col.lower():
                return original_col
    return None

if df_log is not None:
    # Stripping hidden characters or ascii encoding artifacts from columns
    clean_columns = [c.encode('ascii', 'ignore').decode('ascii').strip() for c in df_log.columns]
    mapping_dict = dict(zip(clean_columns, df_log.columns))
    
    xsd_target = find_flexible_column(clean_columns, ['xsd', 'x_sd'])
    eff_target = find_flexible_column(clean_columns, ['efficiency', 'eta'])
    irr_target = find_flexible_column(clean_columns, ['it(', 'irradiance', 'radiation'])
    tout_target = find_flexible_column(clean_columns, ['temp out', 'tout'])
    tin_target = find_flexible_column(clean_columns, ['temp in', 'tin'])
    eout_target = find_flexible_column(clean_columns, ['energy output', 'energy_out'])
    time_target = find_flexible_column(clean_columns, ['time'])

    if xsd_target and eff_target:
        real_xsd_col = mapping_dict[xsd_target]
        real_eff_col = mapping_dict[eff_target]
        
        # Filtering transient logs or zero/negative performance metrics
        if irr_target:
            real_irr_col = mapping_dict[irr_target]
            filtered_df = df_log[(df_log[real_irr_col] > 150) & (df_log[real_xsd_col].notna()) & (df_log[real_eff_col].notna())].copy()
        else:
            filtered_df = df_log[(df_log[real_xsd_col].notna()) & (df_log[real_eff_col].notna())].copy()
            
        if not filtered_df.empty:
            reg_x = filtered_df[real_xsd_col].tolist()
            raw_eff_values = filtered_df[real_eff_col].tolist()
            
            # Auto convert fractions to true % metrics
            if max(raw_eff_values) <= 1.0:
                reg_y = [v * 100 for v in raw_eff_values]
                filtered_df['_eff_pct'] = filtered_df[real_eff_col] * 100
            else:
                reg_y = raw_eff_values
                filtered_df['_eff_pct'] = filtered_df[real_eff_col]
                
            log_uploaded = True
            
            # Calculating performance matrix metrics
            log_metrics['avg_eff'] = filtered_df['_eff_pct'].mean()
            if tout_target:
                log_metrics['max_tout'] = filtered_df[mapping_dict[tout_target]].max()
            if eout_target:
                real_eout = mapping_dict[eout_target]
                log_metrics['peak_w'] = filtered_df[real_eout].max() / 1000.0
                
                # Dynamic Integration of harvested power outputs
                if time_target:
                    try:
                        times_parsed = pd.to_datetime(filtered_df[mapping_dict[time_target]], format='%I:%M:%S %p', errors='coerce')
                        if times_parsed.isna().all():
                            times_parsed = pd.to_datetime(filtered_df[mapping_dict[time_target]], errors='coerce')
                        
                        sorted_idx = times_parsed.argsort()
                        sorted_times = times_parsed.iloc[sorted_idx]
                        sorted_e = filtered_df[real_eout].iloc[sorted_idx]
                        
                        delta_hours = sorted_times.diff().dt.total_seconds().fillna(300.0) / 3600.0
                        log_metrics['harvested_kwh'] = (sorted_e * delta_hours).sum() / 1000.0
                    except:
                        log_metrics['harvested_kwh'] = (filtered_df[real_eout].mean() * len(filtered_df) * 5 / 60) / 1000.0
                else:
                    log_metrics['harvested_kwh'] = (filtered_df[real_eout].mean() * len(filtered_df) * 5 / 60) / 1000.0


# =========================================================
# 📋 RENDERING UI SECTIONS
# =========================================================

# SECTION 1: ENGINEERING CALCULATIONS TIER
st.markdown('<h3 class="section-header">🧮 I. Engineering Sizing Specifications</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">NET THERMAL LOAD</div><div class="metric-value">🔥 {net_energy_demand:.1f} <span style="font-size:12px;">kWh/Day</span></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">TOTAL SOLAR MODULES</div><div class="metric-value">🧩 {modules} <span style="font-size:12px;">Units</span></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">TOTAL FIELD AREA</div><div class="metric-value">📐 {total_collector_area:.1f} <span style="font-size:12px;">m²</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #457b9d;"><div class="metric-title">LOOP DESIGN FLOW</div><div class="metric-value">💧 {flow_lpm:.1f} <span style="font-size:12px;">LPM</span></div></div>', unsafe_allow_html=True)

# SECTION 2: HYDRAULIC DESIGN SUGGESTIONS
st.markdown('<h3 class="section-header">⚙️ II. Balance of Plant (BOP) & System Architecture</h3>', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #2196f3;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#2196f3; font-size:14px;">📦 Tank & Storage Sizing</h4>
        <div style="background-color:#e3f2fd; padding:4px; border-radius:4px; font-weight:bold; color:#0d47a1; text-align:center; margin-bottom:8px; font-size:12px;">
            Recommended Tank Capacity: {storage_tank_capacity:,.0f} Liters
        </div>
        <span style="font-size:12px;">
        • <b>Material Spec:</b> SS314 / SS316L Inner Vessel.<br>
        • <b>Insulation:</b> 100mm High-Density Rockwool or PUF Injection.<br>
        • <b>Loss Performance:</b> &lt; 2°C standing loss per 24 hours.
        </span>
    </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #ff9800;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#ff9800; font-size:14px;">🗺️ Array Field Configuration</h4>
        <div style="background-color:#fff3e0; padding:4px; border-radius:4px; font-weight:bold; color:#e65100; text-align:center; margin-bottom:8px; font-size:12px;">
            Hydraulic Array Layout: {total_banks} Banks Parallel
        </div>
        <span style="font-size:12px;">
        • <b>Series Density:</b> Modules per Bank: {modules_per_bank} Units.<br>
        • <b>Interconnecting Header Piping:</b> {pipe_size_dn} Copper or Composite Piping.<br>
        • <b>Balancing Valves:</b> Needed on parallel loops to avoid thermal short-circuits.
        </span>
    </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
    <div class="card-box" style="border-left: 4px solid #4caf50;">
        <h4 style="margin-top:0; margin-bottom:5px; color:#4caf50; font-size:14px;">🎛️ Automation & Controls Integration</h4>
        <div style="background-color:#e8f5e9; padding:4px; border-radius:4px; font-weight:bold; color:#1b5e20; text-align:center; margin-bottom:8px; font-size:12px;">
            Primary Loop Pump: {pump_hp} VFD High-Temp Pump
        </div>
        <span style="font-size:12px;">
        • <b>Differential Temp Controller (DTC):</b> Modulates velocity based on field outputs.<br>
        • <b>Telemetry:</b> RS485 Modbus connectivity matching plant SCADA interfaces.<br>
        • <b>Plant Notes:</b> {current_ind['note']}
        </span>
    </div>
    """, unsafe_allow_html=True)

# SECTION 3: ECONOMIC ANALYSIS
st.markdown('<h3 class="section-header">💰 III. Commercial Proposal & Financial Viability Analysis</h3>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f'<div class="metric-container" style="border-top-color: #1d3557;"><div class="metric-title">TOTAL TURNKEY CAPEX</div><div class="metric-value">₹ {turnkey_capex:,.0f}</div></div>', unsafe_allow_html=True)
with f2:
    st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">ANNUAL UTILITY SAVINGS</div><div class="metric-value">₹ {annual_monetary_savings:,.0f}</div></div>', unsafe_allow_html=True)
with f3:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e9c46a;"><div class="metric-title">SIMPLE PAYBACK PERIOD</div><div class="metric-value">{simple_payback_years:.2f} <span style="font-size:12px;">Years</span></div></div>', unsafe_allow_html=True)
with f4:
    st.markdown(f'<div class="metric-container" style="border-top-color: #e76f51;"><div class="metric-title">INTERNAL RATE OF RETURN (ROI)</div><div class="metric-value">{roi_percent:.1f} %</div></div>', unsafe_allow_html=True)

# SECTION 4: DIAGNOSTIC GRAPHS (WITH DYNAMIC LOG INTEGRATION)
st.markdown('<h3 class="section-header">📊 IV. Performance Curves & Solar Radiation Data</h3>', unsafe_allow_html=True)

tab_curves, tab_diagnostics = st.tabs(["🎯 Sizing & Design Curves", "🔬 Field Log Time-Series Diagnostics"])

with tab_curves:
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        x_vals = np.linspace(0, 0.12, 100)
        eta_vals = (eta_0 - (u_total_loss * x_vals)) * 100
        eta_vals = np.clip(eta_vals, 5.0, 85.0)
        
        fig_efficiency = go.Figure()
        fig_efficiency.add_trace(go.Scatter(x=x_vals, y=eta_vals, mode='lines', name='Theoretical Efficiency Curve', line=dict(color='#0f52ba', width=2.5)))
        fig_efficiency.add_trace(go.Scatter(x=[x_sd_current], y=[collector_efficiency * 100], mode='markers+text', name='Calculated Design Point', text=[f"Design Target ({collector_efficiency*100:.1f}%)"], textposition="top right", marker=dict(color='#e63946', size=11, symbol='diamond', line=dict(color='black', width=1.5))))
        
        marker_name = 'Field Log Points (Active Data)' if log_uploaded else 'Sample Calibration Test Points'
        fig_efficiency.add_trace(go.Scatter(x=reg_x, y=reg_y, mode='markers', name=marker_name, marker=dict(color='#2a9d8f', size=6 if log_uploaded else 7, symbol='circle', opacity=0.6 if log_uploaded else 0.8)))
        
        fig_efficiency.update_layout(
            title="🎯 Collector Thermal Efficiency Tracking Curve",
            xaxis_title="Thermal Parameter X_SD [(T_plate - T_amb) / Irradiance]",
            yaxis_title="Collector Thermal Efficiency (η %)",
            xaxis=dict(gridcolor='#e9ecef', range=[0, 0.12]),
            yaxis=dict(gridcolor='#e9ecef', range=[0, 100]),
            plot_bgcolor='white', height=280, margin=dict(l=30, r=30, t=40, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)

    with chart_col2:
        fig_radiation = go.Figure()
        fig_radiation.add_trace(go.Bar(x=months, y=measured_radiation, name='Ground GHI Profile', marker_color='#f4a261', opacity=0.85, marker_line=dict(color='#e76f51', width=1)))
        fig_radiation.update_layout(
            title="☀️ Accurate Regional Meteorological Daily Solar GHI Profile",
            xaxis_title="Operating Month",
            yaxis_title="Global Horizontal Radiation (kWh/m²/day)",
            yaxis=dict(gridcolor='#e9ecef', range=[0, 9]), 
            plot_bgcolor='white', height=280, margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_radiation, use_container_width=True)

with tab_diagnostics:
    if log_uploaded:
        st.markdown("#### 🚀 Log File Operational Metadata Matrix")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-container" style="border-top-color: #00bcd4;"><div class="metric-title">LOGGED AVG EFFICIENCY</div><div class="metric-value">⏱️ {log_metrics.get("avg_eff", 0):.1f}%</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-container" style="border-top-color: #ff5722;"><div class="metric-title">PEAK DISCHARGE TEMP</div><div class="metric-value">🌡️ {log_metrics.get("max_tout", 0):.1f} °C</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-container" style="border-top-color: #4caf50;"><div class="metric-title">LOGGED HEAT HARVESTED</div><div class="metric-value">🔋 {log_metrics.get("harvested_kwh", 0):.1f} <span style="font-size:12px;">kWh</span></div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-container" style="border-top-color: #9c27b0;"><div class="metric-title">PEAK LOOP THERMAL POWER</div><div class="metric-value">⚡ {log_metrics.get("peak_w", 0):.1f} <span style="font-size:12px;">kW</span></div></div>', unsafe_allow_html=True)
            
        ts1, ts2 = st.columns(2)
        with ts1:
            if time_target and irr_target:
                fig_ts_irr = go.Figure()
                fig_ts_irr.add_trace(go.Scatter(x=df_log[mapping_dict[time_target]], y=df_log[mapping_dict[irr_target]], mode='lines', name='Solar GHI', line=dict(color='#ff9800', width=2)))
                fig_ts_irr.update_layout(title="☀️ Diurnal Solar Radiation Capture Timeline", xaxis_title="Time of Day", yaxis_title="Irradiance (W/m²)", plot_bgcolor='white', height=260, margin=dict(l=30, r=30, t=40, b=30))
                st.plotly_chart(fig_ts_irr, use_container_width=True)
        with ts2:
            if time_target and tout_target and tin_target:
                fig_ts_temp = go.Figure()
                fig_ts_temp.add_trace(go.Scatter(x=df_log[mapping_dict[time_target]], y=df_log[mapping_dict[tin_target]], mode='lines', name='Field Feed Tin', line=dict(color='#2196f3', width=1.5)))
                fig_ts_temp.add_trace(go.Scatter(x=df_log[mapping_dict[time_target]], y=df_log[mapping_dict[tout_target]], mode='lines', name='Field Delivery Tout', line=dict(color='#e53935', width=2)))
                fig_ts_temp.update_layout(title="🌡️ Dynamic Loop Heat Gradient (Tin vs Tout)", xaxis_title="Time of Day", yaxis_title="Temperature (°C)", plot_bgcolor='white', height=260, margin=dict(l=30, r=30, t=40, b=30))
                st.plotly_chart(fig_ts_temp, use_container_width=True)
    else:
        st.info("💡 Field operational metrics are idle. Select a pre-loaded field log dataset or drop a custom CSV into the side panel to dynamically parse operational telemetry.")

# SECTION 5: P&ID BLUEPRINT LAYOUT (Adaptive Array Config Engine)
st.markdown('<h3 class="section-header">📐 V. Schematic P&ID Process Flow Diagram</h3>', unsafe_allow_html=True)

label_text = current_ind['label']
color_hex = current_ind['color']

# Dynamic Graph Builder based on layout size metrics
if modules > modules_per_bank:
    array_nodes = f"""
        Array_A [label="COLLECTOR BANK A\\n({modules_per_bank} Modules)", fillcolor="#ffebee", color="#e53935", width=1.3, height=0.5];
        Array_B [label="COLLECTOR BANK B\\n({modules - modules_per_bank} Modules)", fillcolor="#ffebee", color="#e53935", width=1.3, height=0.5];
    """
    array_edges = f"""
        Pump_P1 -> Array_A [color="#0f52ba", label=" {flow_kghr/2:.0f} kg/h"];
        Pump_P1 -> Array_B [color="#0f52ba", label=" {flow_kghr/2:.0f} kg/h"];
        Array_A -> TT_101 [color="#c62828"];
        Array_B -> TT_101 [color="#c62828"];
    """
else:
    array_nodes = f"""
        Array_A [label="COLLECTOR FIELD LOOP\\n({modules} Modules)", fillcolor="#ffebee", color="#e53935", width=1.3, height=0.5];
    """
    array_edges = f"""
        Pump_P1 -> Array_A [color="#0f52ba", label=" {flow_kghr:.0f} kg/h"];
        Array_A -> TT_101 [color="#c62828"];
    """

st.graphviz_chart(f"""
digraph G {{
    size="12,4.5!";
    ratio="fill";
    rankdir=LR;
    splines=ortho;
    nodesep=0.2;
    ranksep=0.3;
    
    node [fontname="Helvetica", fontsize=9, penwidth=1.2];
    edge [fontname="Helvetica-Bold", fontsize=8, penwidth=1.2];

    node [shape=triangle, fixedsize=true, width=0.22, height=0.15, style=filled, fillcolor="#b0bec5", color="#37474f"];
    valv_in [label=""]; valv_out [label=""]; valv_ret [label=""]; valv_by [label=""];
    
    node [shape=diamond, fixedsize=true, width=0.2, height=0.2, fillcolor="#eceff1", label="Y"];
    strainer [label=""];

    node [shape=circle, fixedsize=true, width=0.48, style=filled, fillcolor="#e0f7fa", color="#006064", fontname="Helvetica-Bold", fontsize=8];
    LT_101 [label="LT\\n101"];
    TT_101 [label="TT\\n101"];
    TT_102 [label="TT\\n102"];
    PT_101 [label="PT\\n101"];
    FT_101 [label="FT\\n101"];
    TIC_101 [label="TIC\\n101", fillcolor="#fff9c4", color="#f57f17"];

    node [shape=box, style="filled,rounded", width=1.4, height=0.8, color="#0f52ba", fillcolor="#f8f9fa", fontsize=9];
    Inlet [label="📥 WATER SUPPLY\\nInlet Feed\\n({tin}°C Supply)", shape=cds, fillcolor="#e3f2fd"];
    
    subgraph cluster_solar {{
        label="☀️ SOLAR COLLECTOR ROW FIELDS";
        color="#c62828"; style="dashed,rounded"; bgcolor="#fffde7"; fontsize=8;
        {array_nodes}
    }}

    Tank [label="🛢 STORAGE TANK\\nTK-101 Buffer\\n({storage_tank_capacity:,.0f} Liters)", shape=cylinder, fillcolor="#fff3cd", color="#f9a825", width=1.3, height=1.4];
    Boiler [label="🔥 AUX BOILER\\nBackup Heating Unit\\n({aux_fuel_type})", fillcolor="#eceff1", color="#37474f"];
    
    Process [label="{label_text}\\n({tout}°C Plant Process Load)", shape=cds, fillcolor="{color_hex}", color="#1c1c1e", width=2.0];

    node [shape=component, width=0.5, height=0.35, fillcolor="#e8f5e9", color="#2e7d32"];
    Pump_P1 [label="Pump P-1\\n(Solar Field)\\n({pump_hp})"];
    Pump_P2 [label="Pump P-2\\n(Utility Load)"];

    node [shape=plaintext, width=2.2, height=2.5, style=none, color=none];
    LegendIndex [label=<
        <table border="1" cellborder="1" cellspacing="0" cellpadding="3" bgcolor="#ffffff" color="#2c3e50">
            <tr><td colspan="2" bgcolor="#1d3557"><font color="white" size="2"><b>P&amp;ID LEGEND INDEX</b></font></td></tr>
            <tr><td bgcolor="#e0f7fa"><b>LT / TT</b></td><td align="left">Level / Temp Transmitter</td></tr>
            <tr><td bgcolor="#fff9c4"><b>TIC</b></td><td align="left">Delta-T Temperature Controller</td></tr>
            <tr><td bgcolor="#b0bec5"><b>▶◀</b></td><td align="left">Flow Isolation Control Valve</td></tr>
            <tr><td bgcolor="#fff3cd"><b>TK101</b></td><td align="left">Hot Water Thermal Storage Tank</td></tr>
            <tr><td bgcolor="#e8f5e9"><b>P-1/2</b></td><td align="left">Centrifugal Circulation Pump</td></tr>
        </table>
    >];

    Inlet -> strainer [color="#0f52ba"];
    strainer -> valv_in [color="#0f52ba"];
    valv_in -> Tank [color="#0f52ba"];
    Tank -> LT_101 [style=dotted, color="#546e7a", arrowhead=none];

    Tank -> Pump_P1 [color="#0f52ba"];
    {array_edges}
    
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

    edge [style=dashed, color="#757575", penwidth=1.0, arrowhead=dot];
    TT_101 -> TIC_101;
    TT_102 -> TIC_101;
    TIC_101 -> Pump_P1;
    TIC_101 -> valv_ret;

    {{ rank=same; Process; LegendIndex; }}
}}
""")

# SECTION 6: PROPOSAL SUMMARY MATRIX
st.markdown('<h3 class="section-header">📋 VI. Engineering Project Proposal Summary Matrix</h3>', unsafe_allow_html=True)
st.markdown(f"""
| System Parameter | Design Values & Target Bounds |
| :--- | :--- |
| **Selected Target Industry** | 🏢 **{industry_type.upper()}** |
| **Solar Field Architecture** | 🔀 `{total_banks} Parallel Rows` with `{modules_per_bank} Modules` connected in series |
| **Primary Optimal Circuit Flow Rate** | 🌊 **{flow_lpm:.1f} LPM** ({flow_kghr:.1f} kg/hour mass circulation) |
| **Turnkey Project Investment (CAPEX)** | 💳 **{f"₹ {turnkey_capex:,.2f}"}** (Complete engineering, procurement, and setup) |
| **Estimated Fuel Savings per Year** | 🚰 **{fuel_saved_annual:,.1f} {selected_fuel['unit']}/year** reduced from utility boiler usage |
| **Financial Payback Period** | ⏳ **{simple_payback_years:.2f} Operating Years** to fully recover investment cost |
| **Annual Carbon Footprint Reduction** | 🍃 **{co2_reduction_tons:.1f} Metric Tons of CO₂** emissions eliminated |
""", unsafe_allow_html=True)
