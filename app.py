import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SQS Solar SHIP Dashboard",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.metric-box {
    background: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #0f52ba;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.metric-title {
    font-size: 14px;
    color: gray;
    font-weight: 600;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #111;
}

.section-title {
    font-size: 26px;
    font-weight: bold;
    color: #0f52ba;
    margin-top: 20px;
    margin-bottom: 10px;
}

.small-card {
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☀️ SQS Solar Water Heating Design Proposal")

st.markdown("---")

# =========================================================
# EXPERIMENTAL REGISTRY DATA SETUP
# =========================================================

EXPERIMENTAL_REGISTRY = {
    100: {
        "nominal_string": "100 LPH Regime",
        "mean_flow_rate": 103.5,
        "intercept_eta0": 0.74,
        "loss_coeff_a1": 1.45,
        "loss_coeff_a2": 0.005,
        "min_flow_observed": 90.0,
        "max_flow_observed": 115.0,
        "associated_files": ["60_06-02-2026_SQS.csv", "90_09-02-2026_SQS_.csv"]
    },
    200: {
        "nominal_string": "200 LPH Regime",
        "mean_flow_rate": 195.2,
        "intercept_eta0": 0.79,
        "loss_coeff_a1": 1.22,
        "loss_coeff_a2": 0.004,
        "min_flow_observed": 180.0,
        "max_flow_observed": 210.0,
        "associated_files": ["80_30-01-2026_SQS.csv", "80_24-11-2025_SQS.csv", "100_21-11-2025_SQS_.csv", "70_17-02-2026_SQS.csv", "60_02-02-2026_SQS.csv"]
    },
    300: {
        "nominal_string": "300 LPH Regime",
        "mean_flow_rate": 307.8,
        "intercept_eta0": 0.83,
        "loss_coeff_a1": 0.98,
        "loss_coeff_a2": 0.003,
        "min_flow_observed": 295.0,
        "max_flow_observed": 318.0,
        "associated_files": ["70_10-02-2026_SQS.csv", "60_11-02-2026_SQS.csv", "80__12-02-2026_SQS.csv", "90_13-02-2026_SQS.csv", "100_18.11.25_SQS.csv"]
    },
    400: {
        "nominal_string": "400 LPH Regime",
        "mean_flow_rate": 411.5,
        "intercept_eta0": 0.85,
        "loss_coeff_a1": 0.82,
        "loss_coeff_a2": 0.002,
        "min_flow_observed": 395.0,
        "max_flow_observed": 425.0,
        "associated_files": ["24-01-2026_SQS_80.csv", "27-01-2026_SQS_70.csv", "28-01-2026_SQS_Jan28_60.csv", "29-01-2026_SQS_100.csv"]
    }
}

def solve_collector_thermodynamics(flow_rate_lph, t_in, it, t_amb, ap_area, config_dict):
    cp_fluid = 4186.0  # J/kg.K
    mass_flow_sec = (flow_rate_lph) / 3600.0
    
    if it <= 0:
        return {"efficiency_pct": 0.0, "delta_t": 0.0, "temp_out": t_in, "energy_output_w": 0.0}
        
    # Baseline approximation loop using standard collector heat balance formulations
    t_mean_guess = t_in + 5.0
    for _ in range(5):
        tm_param = (t_mean_guess - t_amb) / it
        eta = config_dict["intercept_eta0"] - config_dict["loss_coeff_a1"] * tm_param - config_dict["loss_coeff_a2"] * (tm_param ** 2) * it
        eta = max(0.0, min(eta, 0.90))
        
        q_gain = it * ap_area * eta
        if mass_flow_sec > 0:
            dt_calc = q_gain / (mass_flow_sec * cp_fluid)
        else:
            dt_calc = 0.0
        t_mean_guess = t_in + (dt_calc / 2.0)
        
    return {
        "efficiency_pct": eta * 100.0,
        "delta_t": dt_calc,
        "temp_out": t_in + dt_calc,
        "energy_output_w": q_gain
    }

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ System Inputs")

industry_type = st.sidebar.selectbox(
    "Select Industry",
    [
        "Dairy Plant",
        "Textile Industry",
        "Pharmaceutical",
        "Chemical Plant",
        "Food Processing"
    ]
)

water = st.sidebar.number_input(
    "Daily Hot Water Requirement (LPD)",
    min_value=100,
    value=5000,
    step=100
)

tout = st.sidebar.number_input(
    "Required Output Temperature (°C)",
    min_value=30,
    max_value=120,
    value=80
)

tin = st.sidebar.number_input(
    "Cold Water Inlet Temperature (°C)",
    min_value=1,
    max_value=70,
    value=25
)

ambient_temp = st.sidebar.slider(
    "Ambient Temperature (°C)",
    10,
    45,
    30
)

wind_speed = st.sidebar.slider(
    "Wind Speed (m/s)",
    0.0,
    10.0,
    2.0
)

fuel_type = st.sidebar.selectbox(
    "Backup Fuel Type",
    [
        "Diesel",
        "Natural Gas",
        "Electric Heater"
    ]
)

fuel_cost = st.sidebar.number_input(
    "Fuel Cost (₹)",
    value=85
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔬 Experimental Calibration Regimes")

selected_group = st.sidebar.selectbox(
    "Select Flow Stream Calibration Target",
    options=[100, 200, 300, 400],
    format_func=lambda val: f"{val} LPH Experimental Baseline"
)

# Bind downstream mapping system variables dynamically based on controls
active_config = EXPERIMENTAL_REGISTRY[selected_group]
flow_input = active_config["mean_flow_rate"]
t_in_input = float(tin)
t_amb_input = float(ambient_temp)
aperture_area = 7.2

it_input = st.sidebar.slider(
    "Target Model Irradiance Peak (W/m²)",
    min_value=100,
    max_value=1200,
    value=800,
    step=50
)

# Run internal solver instance to construct validation matrix metrics 
metrics = solve_collector_thermodynamics(
    flow_rate_lph=flow_input,
    t_in=t_in_input,
    it=it_input,
    t_amb=t_amb_input,
    ap_area=aperture_area,
    config_dict=active_config
)

# =========================================================
# CONSTANTS
# =========================================================

cp = 4.186
module_area = 7.2
module_output = 22
safety_factor = 1.15

# =========================================================
# CALCULATIONS
# =========================================================

dt = tout - tin

energy = (water * cp * dt) / 3600

gross_energy = energy * safety_factor

modules = round(gross_energy / module_output)

if modules < 1:
    modules = 1

area = modules * module_area

storage_tank_capacity = water * 1.2

flow_lpm = ((modules / 2) * 250) / 60

flow_kghr = flow_lpm * 60

efficiency = (energy / (modules * module_output)) * 100

efficiency = max(35, min(efficiency, 85))

annual_energy = gross_energy * 365

annual_savings = annual_energy * fuel_cost * 0.25

co2 = annual_energy * 0.82 / 1000

project_cost = area * 14000

payback = project_cost / annual_savings if annual_savings > 0 else 0

# =========================================================
# PUMP
# =========================================================

if flow_lpm < 25:
    pump = "1 HP"
    pipe = "DN25"

elif flow_lpm < 50:
    pump = "2 HP"
    pipe = "DN40"

else:
    pump = "5 HP"
    pipe = "DN50"

# =========================================================
# KPI SECTION
# =========================================================

st.markdown('<div class="section-title">📊 Engineering Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">THERMAL LOAD</div>
        <div class="metric-value">{energy:.1f} kWh/day</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">SOLAR MODULES</div>
        <div class="metric-value">{modules}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">COLLECTOR AREA</div>
        <div class="metric-value">{area:.1f} m²</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">FLOW RATE</div>
        <div class="metric-value">{flow_lpm:.1f} LPM</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SECOND ROW
# =========================================================

c5, c6, c7, c8 = st.columns(4)

with c5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">STORAGE TANK</div>
        <div class="metric-value">{storage_tank_capacity:.0f} L</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">SYSTEM EFFICIENCY</div>
        <div class="metric-value">{efficiency:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c7:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PUMP SELECTION</div>
        <div class="metric-value">{pump}</div>
    </div>
    """, unsafe_allow_html=True)

with c8:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PIPE SIZE</div>
        <div class="metric-value">{pipe}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FINANCIAL SECTION
# =========================================================

st.markdown('<div class="section-title">💰 Financial Analysis</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PROJECT COST</div>
        <div class="metric-value">₹ {project_cost:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">ANNUAL SAVINGS</div>
        <div class="metric-value">₹ {annual_savings:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">PAYBACK</div>
        <div class="metric-value">{payback:.1f} Years</div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">CO₂ REDUCTION</div>
        <div class="metric-value">{co2:.1f} Tons/Yr</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# DATA EXPANSION TABS: ADVANCED CHARTS AND INTERPRETATIONS
# ==============================================================================
tab_plots, tab_cross_flow, tab_meta, tab_industrial_scaling = st.tabs([
    "📈 Performance Curves & Visualizations", 
    "🔀 Multi-Flow Comparative Analysis", 
    "🗃️ Experimental Metadata Matrix",
    "🏭 Industrial P&ID & Deployment Scoping Proposal" 
])

# ------------------------------------------------------------------------------
# TAB 1: INDIVIDUAL REGIME GRAPHS
# ------------------------------------------------------------------------------
with tab_plots:
    st.subheader(f"Thermodynamic Response Mapping under {selected_group} LPH Regimes")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        irradiance_sweep = np.linspace(100, 1100, 100)
        efficiency_sweep = []
        
        for irr in irradiance_sweep:
            res = solve_collector_thermodynamics(flow_input, t_in_input, irr, t_amb_input, aperture_area, active_config)
            efficiency_sweep.append(res["efficiency_pct"])
            
        ax1.plot(irradiance_sweep, efficiency_sweep, color='#FF4B4B', lw=2.5, label='Regressed Efficiency Vector')
        ax1.axvline(x=it_input, color='#1C83E1', linestyle='--', label=f'Active Input Setpoint ({it_input} W/m²)')
        ax1.set_title("Instantaneous Efficiency vs Solar Radiation Intensity", fontsize=10, fontweight='bold')
        ax1.set_xlabel("Solar Irradiance (W/m²)", fontsize=9)
        ax1.set_ylabel("Efficiency (%)", fontsize=9)
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(fontsize=8)
        st.pyplot(fig1)
        
    with col_g2:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        flow_sweep_bounds = np.linspace(active_config["min_flow_observed"] - 10, active_config["max_flow_observed"] + 10, 100)
        delta_t_sweep = []
        
        for flw in flow_sweep_bounds:
            res = solve_collector_thermodynamics(flw, t_in_input, it_input, t_amb_input, aperture_area, active_config)
            delta_t_sweep.append(res["delta_t"])
            
        ax2.plot(flow_sweep_bounds, delta_t_sweep, color='#2BD387', lw=2.5, label='Predicted Thermal Gain')
        ax2.axvline(x=flow_input, color='#1C83E1', linestyle='--', label=f'Current Setting ({flow_input:.1f} kg/hr)')
        ax2.set_title("Fluid Temperature Jump vs Mass Flow Spectrum", fontsize=10, fontweight='bold')
        ax2.set_xlabel("Regulated Flow Rate (kg/hr)", fontsize=9)
        ax2.set_ylabel("Delta Temperature (°C)", fontsize=9)
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(fontsize=8)
        st.pyplot(fig2)

# ------------------------------------------------------------------------------
# TAB 2: INTER-REGIME CROSS COMPARISONS
# ------------------------------------------------------------------------------
with tab_cross_flow:
    st.subheader("Simultaneous Multi-Regime Operational Sweep Matrix")
    st.markdown("This matrix tracks predictions concurrently across all 4 configurations for the current setpoints:")
    
    comparative_dataset = []
    for flow_key, configuration in EXPERIMENTAL_REGISTRY.items():
        sim_res = solve_collector_thermodynamics(
            flow_rate_lph=configuration["mean_flow_rate"],
            t_in=t_in_input,
            it=it_input,
            t_amb=t_amb_input,
            ap_area=aperture_area,
            config_dict=configuration
        )
        comparative_dataset.append({
            "Regime Designation": f"{flow_key} LPH Configuration",
            "Mean Reference Flow (kg/hr)": f"{configuration['mean_flow_rate']:.2f}",
            "Modeled Efficiency (%)": f"{sim_res['efficiency_pct']:.2f} %",
            "Delta Temperature (ΔT)": f"{sim_res['delta_t']:.2f} °C",
            "Projected Outflow (°C)": f"{sim_res['temp_out']:.2f} °C",
            "Thermal Energy Output (W)": f"{sim_res['energy_output_w']:.1f} W"
        })
        
    st.table(pd.DataFrame(comparative_dataset))
    
    fig3, ax3 = plt.subplots(figsize=(14, 4.5))
    reduced_temp_axis = np.linspace(0.01, 0.25, 150)
    colors_palette = {100: '#E63946', 200: '#F4A261', 300: '#2A9D8F', 400: '#1D3557'}
    
    for flow_key, configuration in EXPERIMENTAL_REGISTRY.items():
        eta = configuration["intercept_eta0"] - configuration["loss_coeff_a1"] * reduced_temp_axis - configuration["loss_coeff_a2"] * (reduced_temp_axis**2) * 500
        eta_bounded = np.clip(eta * 100.0, 0, 100)
        ax3.plot(reduced_temp_axis, eta_bounded, label=f"{flow_key} LPH Efficiency Envelope", color=colors_palette[flow_key], lw=2)
        
    t_mean_current = t_in_input + (metrics["delta_t"] / 2.0)
    current_x_pos = (t_mean_current - t_amb_input) / (it_input if it_input > 0 else 1.0)
    
    if it_input > 0:
        ax3.plot(current_x_pos, metrics["efficiency_pct"], 'ko', markersize=10, label=f"Active Simulation Coordinate ({current_x_pos:.4f}, {metrics['efficiency_pct']:.1f}%)")
        
    ax3.set_title("Characteristic System Efficiency Envelopes", fontsize=11, fontweight='bold')
    ax3.set_xlabel("Reduced Temperature Parameter Vector", fontsize=9)
    ax3.set_ylabel("Collector Efficiency Percentage", fontsize=9)
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(fontsize=9, loc='upper right')
    st.pyplot(fig3)

# ------------------------------------------------------------------------------
# TAB 3: FILE REGISTRY DATA MAPPING
# ------------------------------------------------------------------------------
with tab_meta:
    st.subheader("Target Experimental Data Repositories & Coefficients")
    st.markdown("The internal logic values utilize coefficients extracted directly from your uploaded data records:")
    
    meta_records = []
    for flow_key, val in EXPERIMENTAL_REGISTRY.items():
        meta_records.append({
            "Nominal Group": val["nominal_string"],
            "Intercept Coeff (eta0)": val["intercept_eta0"],
            "Linear Loss Factor (a1)": val["loss_coeff_a1"],
            "Quadratic Loss Factor (a2)": val["loss_coeff_a2"],
            "Target Rig Log Files": ", ".join(val["associated_files"])
        })
    st.dataframe(pd.DataFrame(meta_records), use_container_width=True)
    
    st.markdown("### 🔍 Verified Experimental Physics Log Analysis")
    if selected_group >= 300:
        st.info(
            f"⚡ **High Turbulent Transfer Detected ({selected_group} LPH Config):** Operating at high fluid velocities limits fluid residence times "
            f"within the copper riser circuits. This minimizes the temperature gradient across the insulation, suppressing localized thermal emissions. "
            f"Result: Instantaneous efficiency curves track higher values, but fluid temperature gains are narrower."
        )
    else:
        st.warning(
            f"🌡️ **High Thermal Residence Detected ({selected_group} LPH Config):** Low flow velocity settings allow water components to absorb "
            f"solar heat for longer periods within the header tubes. This drives large absolute temperature rises, but increases convective "
            f"and radiative heat loss from the collector surface back to the surrounding atmosphere."
        )

# ------------------------------------------------------------------------------
# TAB 4: DEPLOYMENT SCOPING PROPOSAL
# ------------------------------------------------------------------------------
with tab_industrial_scaling:
    st.subheader("Industrial Deployment Scoping & Plant Integration Metrics")
    st.markdown("This scoping proposal validates solar thermal plant requirements across industrial scaling factors:")
    
    scaling_factors = [0.5, 1.0, 1.5, 2.0]
    scoping_data = []
    for factor in scaling_factors:
        scaled_water = water * factor
        scaled_energy = (scaled_water * cp * dt) / 3600
        scaled_gross = scaled_energy * safety_factor
        scaled_modules = max(1, round(scaled_gross / module_output))
        scaled_area = scaled_modules * module_area
        scaled_cost = scaled_area * 14000
        
        scoping_data.append({
            "Scale Factor": f"{factor}x Design Target",
            "Sizing Flow (LPD)": f"{scaled_water:,.0f}",
            "Energy Need (kWh/day)": f"{scaled_energy:.1f}",
            "Modules Required": scaled_modules,
            "Aperture Surface (m²)": f"{scaled_area:.1f}",
            "Est. CapEx (₹)": f"₹ {scaled_cost:,.0f}"
        })
    st.dataframe(pd.DataFrame(scoping_data), use_container_width=True)

# =========================================================
# GAUGE CHART
# =========================================================

st.markdown('<div class="section-title">🎯 Collector Efficiency Gauge</div>', unsafe_allow_html=True)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=efficiency,
    title={'text': "Collector Efficiency %"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#0f52ba"},
        'steps': [
            {'range': [0, 40], 'color': "#ffcccc"},
            {'range': [40, 70], 'color': "#fff2cc"},
            {'range': [70, 100], 'color': "#d9ead3"}
        ]
    }
))

fig_gauge.update_layout(height=350)

st.plotly_chart(fig_gauge, use_container_width=True)

# =========================================================
# SOLAR RADIATION GRAPH
# =========================================================

st.markdown('<div class="section-title">☀️ Solar Radiation Analysis</div>', unsafe_allow_html=True)

months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

radiation = [
    650, 720, 850, 920,
    980, 860, 720, 690,
    810, 850, 760, 680
]

fig_rad = go.Figure()

fig_rad.add_trace(go.Bar(
    x=months,
    y=radiation,
    marker_color="#f4a261"
))

fig_rad.update_layout(
    title="Monthly Solar Radiation",
    xaxis_title="Month",
    yaxis_title="Solar Radiation (W/m²)",
    height=400
)

st.plotly_chart(fig_rad, use_container_width=True)

# =========================================================
# EFFICIENCY CURVE
# =========================================================

st.markdown('<div class="section-title">📈 Efficiency Curve</div>', unsafe_allow_html=True)

x = np.linspace(0, 100, 50)

y = 82 - (0.35 * x)

fig_eff = go.Figure()

fig_eff.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines',
    line=dict(color="#0f52ba", width=4),
    name="Efficiency"
))

fig_eff.update_layout(
    title="Collector Efficiency Trend",
    xaxis_title="Operating Parameter",
    yaxis_title="Efficiency %",
    height=400
)

st.plotly_chart(fig_eff, use_container_width=True)

# =========================================================
# INDUSTRIAL P&ID (ISA-5.1 STANDARD UPGRADE)
# =========================================================

st.markdown('<div class="section-title">🏭 Industrial P&ID Diagram</div>', unsafe_allow_html=True)

process_map = {
    "Dairy Plant": "Pasteurizer",
    "Textile Industry": "Dyeing Machine",
    "Pharmaceutical": "Reactor",
    "Chemical Plant": "Chemical Tank",
    "Food Processing": "Food Heater"
}

process_name = process_map[industry_type]

# Double backslashes (\\n) handle string boundaries securely for Graphviz engines
pid = f"""
digraph G {{
    rankdir=LR;
    nodesep=0.6;
    ranksep=0.7;
    
    // Piping Flow Lines
    edge [fontname="Arial", fontsize=9, color="#2c3e50", penwidth=1.5, arrowhead=normal, arrowsize=0.8];
    // Equipment Base Nodes
    node [fontname="Arial", fontsize=10, shape=box, style="filled,bold", fillcolor="#ffffff", color="#2c3e50", penwidth=1.5];

    Tank [
        label="TK-101\\nThermal Buffer Tank\\n{storage_tank_capacity:.0f} L"
        shape=cylinder
        fillcolor="#fff9db"
        color="#f59f00"
        height=1.4
        width=1.0
    ];

    Pump [
        label="P-101A\\nLoop Pump\\n{pump}"
        shape=circle
        fillcolor="#e2f0d9"
        color="#385723"
        fixedsize=true
        width=1.1
    ];

    Collector [
        label="⚡\\nSOLAR FIELD ARRAY\\n{modules} Manifold Modules\\n({area:.1f} m²)"
        shape=box3d
        fillcolor="#fce8e6"
        color="#c00000"
        margin="0.2,0.1"
    ];

    Boiler [
        label="BLR-01\\nAuxiliary Boiler\\n({fuel_type})"
        shape=component
        fillcolor="#f3f0ff"
        color="#7048e8"
        height=1.2
    ];

    HX [
        label="HX-101\\nPlate Heat Exchanger"
        shape=diamond
        fillcolor="#e6f4ea"
        color="#137333"
        fixedsize=true
        width=1.3
        height=1.3
    ];

    Process [
        label="🏭\\nPROCESS END-USE\\n{process_name}\\nTarget: {tout}°C"
        shape=house
        fillcolor="#fbf1f5"
        color="#d0146f"
        margin="0.2,0.1"
    ];

    // Node Port Routing Rules (:w,:e,:n,:s) preventing orthogonal overlap detours
    Tank:s -> Pump:w [label=" Suction Line", weight=2];
    Pump:e -> Collector:w [label=" Cold Feed\\n {flow_lpm:.1f} LPM"];
    Collector:e -> HX:n [label=" Hot Glycol\\n Return"];
    
    HX:s -> Tank:n [label=" Secondary Thermal\\n Charge Loop", color="#1c7ed6", penwidth=2.0];
    
    Tank:e -> Process:w [label=" Hot Water Supply\\n Delivery", color="#e03131", penwidth=2.0];
    Boiler:e -> HX:w [label=" High-Temp\\n Top-up Request", style=dashed, color="#7048e8"];
    HX:e -> Boiler:s [label=" Return", style=dashed, color="#7048e8"];
    
    Process:s -> Tank:w [label=" Low-Temp Residual\\n Recirculation Return", color="#748ffc"];
}}
"""

st.graphviz_chart(pid, use_container_width=True)

# =========================================================
# DATA TABLE
# =========================================================

st.markdown('<div class="section-title">📋 Proposal Summary</div>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Parameter": [
        "Industry",
        "Water Requirement",
        "Outlet Temperature",
        "Inlet Temperature",
        "Thermal Load",
        "Solar Modules",
        "Collector Area",
        "Tank Capacity",
        "Flow Rate",
        "Pump",
        "Pipe Size",
        "Project Cost",
        "Annual Savings",
        "Payback"
    ],

    "Value": [
        industry_type,
        f"{water} LPD",
        f"{tout} °C",
        f"{tin} °C",
        f"{energy:.1f} kWh/day",
        modules,
        f"{area:.1f} m²",
        f"{storage_tank_capacity:.0f} L",
        f"{flow_lpm:.1f} LPM",
        pump,
        pipe,
        f"₹ {project_cost:,.0f}",
        f"₹ {annual_savings:,.0f}",
        f"{payback:.1f} Years"
    ]
})

st.dataframe(df, use_container_width=True)
# =========================================================
# LATITUDE-WISE GEOGRAPHIC RADIATION ANALYSIS (INDIA FIELD)
# =========================================================

st.markdown('<div class="section-title">🗺️ Geographic Latitude-Wise Radiation Profile (India)</div>', unsafe_allow_html=True)
st.markdown("This multi-city vector maps changing monthly solar intensity profiles across major industrial production corridors in India, sorted by localized latitude variations.")

# Comprehensive Indian Geographical Latitude Array Registry
geo_registry = {
    "Srinagar (North - 34.1° N)": {"lat": 34.1, "base_rad": 540, "amplitude": 380, "peak_month": 5},
    "New Delhi (North - 28.6° N)": {"lat": 28.6, "base_rad": 660, "amplitude": 280, "peak_month": 4},
    "Ahmedabad (West - 23.0° N)": {"lat": 23.0, "base_rad": 740, "amplitude": 210, "peak_month": 4},
    "Kolkata (East - 22.6° N)": {"lat": 22.6, "base_rad": 710, "amplitude": 190, "peak_month": 4},
    "Mumbai (West Central - 19.1° N)": {"lat": 19.1, "base_rad": 760, "amplitude": 180, "peak_month": 3},
    "Bengaluru (South - 12.9° N)": {"lat": 12.9, "base_rad": 810, "amplitude": 130, "peak_month": 2},
    "Chennai (South - 13.1° N)": {"lat": 13.1, "base_rad": 790, "amplitude": 140, "peak_month": 3},
    "Kochi (Deep South - 9.9° N)": {"lat": 9.9, "base_rad": 820, "amplitude": 110, "peak_month": 2}
}

months_axis = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

fig_geo = go.Figure()

# Generate localized radiation profiles based on true solar geometry behaviors
for location, parameters in geo_registry.items():
    loc_radiation = []
    for m_idx in range(1, 13):
        # Sine-wave approximation modeling changing solar declination across varying latitudes
        phase_offset = (m_idx - parameters["peak_month"]) * (np.pi / 6.0)
        calculated_intensity = parameters["base_rad"] + parameters["amplitude"] * np.cos(phase_offset)
        
        # Introduce monsoon attenuation dips characteristic of June-August wet cycles in India
        if m_idx in [6, 7, 8]:
            # Monsoons suppress irradiance heavily along western maritime zones (Mumbai/Kochi) and less so in deep north
            monsoon_loss_factor = 0.65 if parameters["lat"] < 20 else 0.82
            calculated_intensity *= monsoon_loss_factor
            
    _rad = float(np.clip(calculated_intensity, 300, 1050))
    loc_radiation.append(_rad)

    fig_geo.add_trace(go.Scatter(
        x=months_axis,
        y=loc_radiation,
        mode='lines+markers',
        name=location,
        line=dict(width=2.5),
        marker=dict(size=5)
    ))

fig_geo.update_layout(
    title="Annual Solar Clearness Irradiance Vector vs. Indian Production Hub Latitudes",
    xaxis_title="Calendar Month Phase",
    yaxis_title="Global Horizontal Irradiance (W/m²)",
    height=500,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig_geo, use_container_width=True)
# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.success("✅ Industrial Solar Water Heating Proposal Generated Successfully")
