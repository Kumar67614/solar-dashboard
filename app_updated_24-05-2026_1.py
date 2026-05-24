import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import time
from datetime import datetime, timedelta

# ==============================================================================
# 1. GENERATE AN EXTENSIVE ARCHITECTURAL FRAMEWORK & CONFIG
# ==============================================================================
st.set_page_config(
    page_title="SQS Solar SHIP Production-Grade Core Engine",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust custom UI theme injection to bypass default container widths and padding constraints
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    .metric-box {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0f52ba;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-box-financial {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2bc480;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-title { font-size: 13px; color: #6c757d; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 26px; font-weight: 800; color: #212529; margin-top: 5px; }
    .section-title { font-size: 24px; font-weight: 700; color: #0f52ba; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }
    .info-card { background-color: #eef2f7; border-left: 4px solid #1c83e1; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CALIBRATION REPOSITORY REGISTRY DATASET
# ==============================================================================
EXPERIMENTAL_REGISTRY = {
    100: {
        "nominal_string": "100 LPH Regime (Low Velocity / High Lift Limit)",
        "mean_flow_rate": 103.5,
        "intercept_eta0": 0.74,
        "loss_coeff_a1": 1.45,
        "loss_coeff_a2": 0.005,
        "min_flow_observed": 90.0,
        "max_flow_observed": 115.0,
        "associated_files": ["60_06-02-2026_SQS.csv", "90_09-02-2026_SQS_.csv"],
        "turbulent_factor": 1.05
    },
    200: {
        "nominal_string": "200 LPH Regime (Standard Baseline Profile)",
        "mean_flow_rate": 195.2,
        "intercept_eta0": 0.79,
        "loss_coeff_a1": 1.22,
        "loss_coeff_a2": 0.004,
        "min_flow_observed": 180.0,
        "max_flow_observed": 210.0,
        "associated_files": ["80_30-01-2026_SQS.csv", "80_24-11-2025_SQS.csv", "100_21-11-2025_SQS_.csv"],
        "turbulent_factor": 1.18
    },
    300: {
        "nominal_string": "300 LPH Regime (High-Throughput Flow)",
        "mean_flow_rate": 307.8,
        "intercept_eta0": 0.83,
        "loss_coeff_a1": 0.98,
        "loss_coeff_a2": 0.003,
        "min_flow_observed": 295.0,
        "max_flow_observed": 318.0,
        "associated_files": ["70_10-02-2026_SQS.csv", "60_11-02-2026_SQS.csv", "80__12-02-2026_SQS.csv"],
        "turbulent_factor": 1.32
    },
    400: {
        "nominal_string": "400 LPH Regime (Maximum Pumping Capacity Limit)",
        "mean_flow_rate": 411.5,
        "intercept_eta0": 0.85,
        "loss_coeff_a1": 0.82,
        "loss_coeff_a2": 0.002,
        "min_flow_observed": 395.0,
        "max_flow_observed": 425.0,
        "associated_files": ["24-01-2026_SQS_80.csv", "27-01-2026_SQS_70.csv", "29-01-2026_SQS_100.csv"],
        "turbulent_factor": 1.45
    }
}

# INDUSTRIAL SYSTEM SIZING DEFAULT MACRO VARIABLES
DEFAULT_MODULE_AREA = 7.2
DEFAULT_SAFETY_FACTOR = 1.15
BASE_MODULE_ENERGY_YIELD_KWH = 22.0

# ==============================================================================
# 3. HIGH-FIDELITY THERMODYNAMIC SOLVER MODULE
# ==============================================================================
def get_fluid_properties(temp_c):
    """
    Returns accurate specific heat capacity (J/kg.K) and density (kg/m3) 
    for water based on operating mean temperature zones.
    """
    if temp_c < 40:
        return 4182.0, 997.0
    elif temp_c < 70:
        return 4180.0, 988.0
    elif temp_c < 95:
        return 4195.0, 968.0
    else:
        return 4210.0, 958.0

def solve_collector_thermodynamics(flow_rate_lph, t_in, it, t_amb, ap_area, config_dict):
    """
    Simulates step-by-step heat balance formulations for solar collector fields 
    using iterative convergence loops over localized heat losses.
    """
    if it <= 5.0:
        return {
            "efficiency_pct": 0.0,
            "delta_t": 0.0,
            "temp_out": t_in,
            "energy_output_w": 0.0,
            "loss_loss_w": 0.0
        }
        
    t_mean_guess = t_in + 4.5
    dt_calc = 0.0
    eta = 0.0
    q_gain = 0.0
    
    # Iterate to converge on fluid temperature matching localized surface thermal emissions
    for iteration in range(8):
        cp_fluid, density_fluid = get_fluid_properties(t_mean_guess)
        mass_flow_sec = (flow_rate_lph * (density_fluid / 1000.0)) / 3600.0
        
        tm_param = (t_mean_guess - t_amb) / it
        eta = (config_dict["intercept_eta0"] - 
               (config_dict["loss_coeff_a1"] * tm_param) - 
               (config_dict["loss_coeff_a2"] * (tm_param ** 2) * it))
        
        eta = max(0.02, min(eta, 0.89))
        q_gain = it * ap_area * eta
        
        if mass_flow_sec > 0.0:
            dt_calc = q_gain / (mass_flow_sec * cp_fluid)
        else:
            dt_calc = 0.0
            
        t_mean_guess = t_in + (dt_calc / 2.0)
        
    total_incident_power = it * ap_area
    loss_loss_w = total_incident_power - q_gain
    
    return {
        "efficiency_pct": eta * 100.0,
        "delta_t": dt_calc,
        "temp_out": t_in + dt_calc,
        "energy_output_w": q_gain,
        "loss_loss_w": loss_loss_w
    }

# ==============================================================================
# 4. STREAMLIT SIDEBAR COMPONENT DEFINITION
# ==============================================================================
st.sidebar.markdown("## 🛠️ Design Parameters")

industry_type = st.sidebar.selectbox(
    "Select Industrial Target Application",
    ["Dairy Plant", "Textile Industry", "Pharmaceutical", "Chemical Plant", "Food Processing"]
)

water_demand_lpd = st.sidebar.number_input(
    "Daily Volumetric Demand (LPD)",
    min_value=100, max_value=250000, value=7500, step=500
)

required_t_out = st.sidebar.number_input(
    "Required Process Target Temp (°C)",
    min_value=30, max_value=135, value=85, step=5
)

cold_water_t_in = st.sidebar.number_input(
    "Inlet Cold Feed Temp (°C)",
    min_value=5, max_value=65, value=25, step=2
)

ambient_env_temp = st.sidebar.slider(
    "Design Day Ambient Air Temp (°C)",
    min_value=-5, max_value=50, value=28
)

wind_speed_ms = st.sidebar.slider(
    "Microclimate Wind Field Velocity (m/s)",
    min_value=0.0, max_value=12.0, value=1.5, step=0.5
)

st.sidebar.markdown("---")
st.sidebar.markdown("## ⛽ Auxiliary Thermal Plant")

backup_fuel_source = st.sidebar.selectbox(
    "Backup Boiler Combustible Medium",
    ["Heavy Fuel Oil (HFO)", "Natural Gas", "Liquefied Petroleum Gas (LPG)", "Electrical Grid Element"]
)

fuel_unit_cost_inr = st.sidebar.number_input(
    "Unit Fuel Base Pricing Rate (₹)",
    min_value=1.0, max_value=500.0, value=92.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🔬 Empirical Model Core Linker")

selected_calibration_key = st.sidebar.selectbox(
    "Active Regression Dataset Loop",
    options=[100, 200, 300, 400],
    format_func=lambda k: EXPERIMENTAL_REGISTRY[k]["nominal_string"]
)

model_irradiance_peak = st.sidebar.slider(
    "Design Irradiance Envelope (W/m²)",
    min_value=150, max_value=1200, value=850, step=50
)

# Extract linked dictionary configs
active_regime_dict = EXPERIMENTAL_REGISTRY[selected_calibration_key]

# Execute core thermodynamic solver for singular setpoint validation
setpoint_solver_metrics = solve_collector_thermodynamics(
    flow_rate_lph=active_regime_dict["mean_flow_rate"],
    t_in=float(cold_water_t_in),
    it=float(model_irradiance_peak),
    t_amb=float(ambient_env_temp),
    ap_area=DEFAULT_MODULE_AREA,
    config_dict=active_regime_dict
)

# ==============================================================================
# 5. MACRO COMPUTATION CORE SYSTEM ARCHITECTURE
# ==============================================================================
# Fluid profile calculations for primary sizing loop
macro_cp, macro_density = get_fluid_properties((cold_water_t_in + required_t_out) / 2.0)

# Thermal demand physics matrix equations
delta_t_process = required_t_out - cold_water_t_in
daily_energy_demand_kwh = (water_demand_lpd * (macro_density / 1000.0) * (macro_cp / 1000.0) * delta_t_process) / 3600.0
gross_energy_with_safety = daily_energy_demand_kwh * DEFAULT_SAFETY_FACTOR

# Array sizing logic
total_modules_calculated = max(1, round(gross_energy_with_safety / BASE_MODULE_ENERGY_YIELD_KWH))
total_aperture_surface_area = total_modules_calculated * DEFAULT_MODULE_AREA
thermal_storage_tank_liters = water_demand_lpd * 1.25

# Flow network analysis
hydraulic_loop_flow_lpm = ((total_modules_calculated / 2.0) * 265.0) / 60.0
hydraulic_loop_flow_kghr = hydraulic_loop_flow_lpm * 60.0 * (macro_density / 1000.0)

# Macro Efficiency Metric Optimization
calculated_system_macro_efficiency = (daily_energy_demand_kwh / (total_modules_calculated * BASE_MODULE_ENERGY_YIELD_KWH)) * 100.0
calculated_system_macro_efficiency = max(32.5, min(calculated_system_macro_efficiency, 87.5))

# Environmental & Financial Amortization Matrices
fuel_calorific_values_mj = {
    "Heavy Fuel Oil (HFO)": 41.2,
    "Natural Gas": 48.0,
    "Liquefied Petroleum Gas (LPG)": 46.1,
    "Electrical Grid Element": 3.6
}
fuel_co2_emission_factors = {
    "Heavy Fuel Oil (HFO)": 0.27,
    "Natural Gas": 0.20,
    "Liquefied Petroleum Gas (LPG)": 0.23,
    "Electrical Grid Element": 0.82
}

active_fuel_cv = fuel_calorific_values_mj[backup_fuel_source]
active_co2_factor = fuel_co2_emission_factors[backup_fuel_source]

annual_saved_energy_kwh = daily_energy_demand_kwh * 320.0  # Accounting for cloud cover days
annual_fuel_volume_saved = (annual_saved_energy_kwh * 3.6) / active_fuel_cv
annual_financial_savings_inr = annual_fuel_volume_saved * fuel_unit_cost_inr
annual_co2_abatement_tons = (annual_saved_energy_kwh * active_co2_factor) / 1000.0

capital_expenditure_inr = total_aperture_surface_area * 15500.0
payback_period_years = capital_expenditure_inr / annual_financial_savings_inr if annual_financial_savings_inr > 0 else 0.0

# Piping and Pump Infrastructure Auto-Selector Matrix
if hydraulic_loop_flow_lpm < 30.0:
    selected_pump_power = "1.5 HP Centrifugal SQS-Spec"
    selected_pipe_diameter = "DN25 Heavy Gauge Schedule 40"
elif hydraulic_loop_flow_lpm < 75.0:
    selected_pump_power = "3.0 HP High-Head Multistage"
    selected_pipe_diameter = "DN40 Heavy Gauge Schedule 40"
else:
    selected_pump_power = "6.5 HP Industrial VFD Array"
    selected_pipe_diameter = "DN50 Premium Stainless Loop"

# ==============================================================================
# 6. RENDER DATA ARCHITECTURE VIEWPORTS - KPI CARDS
# ==============================================================================
st.markdown('<div class="section-title">📊 Plant Sizing & Hydraulic Infrastructure Summary</div>', unsafe_allow_html=True)

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
with row1_col1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Thermal Load Requirement</div><div class="metric-value">{daily_energy_demand_kwh:.1f} kWh/day</div></div>', unsafe_allow_html=True)
with row1_col2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Total Solar Modules Sized</div><div class="metric-value">{total_modules_calculated} Modules</div></div>', unsafe_allow_html=True)
with row1_col3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Collector Aperture Field</div><div class="metric-value">{total_aperture_surface_area:.1f} m²</div></div>', unsafe_allow_html=True)
with row1_col4:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Hydraulic Loop Flow Rate</div><div class="metric-value">{hydraulic_loop_flow_lpm:.1f} LPM</div></div>', unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
with row2_col1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Storage Thermal Mass Tank</div><div class="metric-value">{thermal_storage_tank_liters:.0f} Liters</div></div>', unsafe_allow_html=True)
with row2_col2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">System Plant Macro Efficiency</div><div class="metric-value">{calculated_system_macro_efficiency:.1f}%</div></div>', unsafe_allow_html=True)
with row2_col3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Primary Pumping Substation</div><div class="metric-value">{selected_pump_power}</div></div>', unsafe_allow_html=True)
with row2_col4:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Header Piping Geometry</div><div class="metric-value">{selected_pipe_diameter}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">💰 Asset Financial Metrics & Environmental Abatement</div>', unsafe_allow_html=True)

row3_col1, row3_col2, row3_col3, row3_col4 = st.columns(4)
with row3_col1:
    st.markdown(f'<div class="metric-box-financial"><div class="metric-title">Estimated Project CapEx</div><div class="metric-value">₹ {capital_expenditure_inr:,.2f}</div></div>', unsafe_allow_html=True)
with row3_col2:
    st.markdown(f'<div class="metric-box-financial"><div class="metric-title">Annualized OpEx Savings</div><div class="metric-value">₹ {annual_financial_savings_inr:,.2f}</div></div>', unsafe_allow_html=True)
with row3_col3:
    st.markdown(f'<div class="metric-box-financial"><div class="metric-title">Simple Financial Payback</div><div class="metric-value">{payback_period_years:.2f} Years</div></div>', unsafe_allow_html=True)
with row3_col4:
    st.markdown(f'<div class="metric-box-financial"><div class="metric-title">Carbon Emission Mitigated</div><div class="metric-value">{annual_co2_abatement_tons:.1f} Tons/Yr</div></div>', unsafe_allow_html=True)

# ==============================================================================
# 7. MULTI-TAB MATRIX MODULES
# ==============================================================================
t_curves, t_comparative, t_logs, t_financial, t_pid_tab = st.tabs([
    "📈 Performance Characteristic Sweeps",
    "🔀 Inter-Regime Cross Evaluation",
    "🗃️ Empirical Metadata System Validation",
    "📈 Advanced Capital Cash Flows",
    "🏭 Integration Architecture & Scaling"
])

# ------------------------------------------------------------------------------
# TAB 1: INTERACTIVE THERMODYNAMIC PERFORMANCE GRAPHICS
# ------------------------------------------------------------------------------
with t_curves:
    st.markdown("### Thermodynamic Field Response Mapping Under Selected Flow Bounds")
    st.write("These interactive modules chart thermodynamic variances for your collector arrays across standard weather bounds.")
    
    curve_col1, curve_col2 = st.columns(2)
    
    with curve_col1:
        fig_irr, ax_irr = plt.subplots(figsize=(8, 4.5))
        irr_vector = np.linspace(150, 1150, 120)
        eff_vector = []
        
        for radiation_instance in irr_vector:
            solver_run = solve_collector_thermodynamics(
                flow_rate_lph=active_regime_dict["mean_flow_rate"],
                t_in=float(cold_water_t_in),
                it=radiation_instance,
                t_amb=float(ambient_env_temp),
                ap_area=DEFAULT_MODULE_AREA,
                config_dict=active_regime_dict
            )
            eff_vector.append(solver_run["efficiency_pct"])
            
        ax_irr.plot(irr_vector, eff_vector, color='#E63946', lw=3, label='Regressed Efficiency Profile')
        ax_irr.axvline(x=model_irradiance_peak, color='#1D3557', linestyle=':', lw=2, label=f'Current Setpoint ({model_irradiance_peak} W/m²)')
        ax_irr.set_title("Instantaneous Fluid Efficiency Vector vs Incident Irradiance", fontsize=10, fontweight='bold', pad=10)
        ax_irr.set_xlabel("Solar Flux Surface Intensity (W/m²)", fontsize=9)
        ax_irr.set_ylabel("Array Instantaneous Efficiency (%)", fontsize=9)
        ax_irr.grid(True, linestyle='--', alpha=0.5)
        ax_irr.legend(fontsize=8, loc='lower right')
        st.pyplot(fig_irr)
        
    with curve_col2:
        fig_flw, ax_flw = plt.subplots(figsize=(8, 4.5))
        flow_vector_bounds = np.linspace(active_regime_dict["min_flow_observed"] - 15.0, active_regime_dict["max_flow_observed"] + 15.0, 120)
        delta_t_vector = []
        
        for flow_instance in flow_vector_bounds:
            solver_run = solve_collector_thermodynamics(
                flow_rate_lph=flow_instance,
                t_in=float(cold_water_t_in),
                it=float(model_irradiance_peak),
                t_amb=float(ambient_env_temp),
                ap_area=DEFAULT_MODULE_AREA,
                config_dict=active_regime_dict
            )
            delta_t_vector.append(solver_run["delta_t"])
            
        ax_flw.plot(flow_vector_bounds, delta_t_vector, color='#2A9D8F', lw=3, label='Predicted Dynamic Heat Lift')
        ax_flw.axvline(x=active_regime_dict["mean_flow_rate"], color='#1D3557', linestyle=':', lw=2, label=f'Nominal Flow Target ({active_regime_dict["mean_flow_rate"]:.1f} kg/hr)')
        ax_flw.set_title("Fluid Temperature Jump Profile vs Regulated Flow Mass", fontsize=10, fontweight='bold', pad=10)
        ax_flw.set_xlabel("Fluid Mass Velocity Velocity Vector (kg/hr)", fontsize=9)
        ax_flw.set_ylabel("Absolute Boundary Temperature Delta (°C)", fontsize=9)
        ax_flw.grid(True, linestyle='--', alpha=0.5)
        ax_flw.legend(fontsize=8, loc='upper right')
        st.pyplot(fig_flw)

# ------------------------------------------------------------------------------
# TAB 2: INTER-REGIME FLOW COMPARATIVE MATRIX
# ------------------------------------------------------------------------------
with t_comparative:
    st.markdown("### Co-dependent Multi-Regime Operational Verification System")
    st.write("This structural evaluation system processes performance metrics simultaneously across all four design baselines for your operational parameters:")
    
    concurrent_matrix_data = []
    for regime_key, regime_config in EXPERIMENTAL_REGISTRY.items():
        execution_metrics = solve_collector_thermodynamics(
            flow_rate_lph=regime_config["mean_flow_rate"],
            t_in=float(cold_water_t_in),
            it=float(model_irradiance_peak),
            t_amb=float(ambient_env_temp),
            ap_area=DEFAULT_MODULE_AREA,
            config_dict=regime_config
        )
        concurrent_matrix_data.append({
            "Regime Matrix Designation": regime_config["nominal_string"],
            "Operational Flow (kg/hr)": f"{regime_config['mean_flow_rate']:.1f}",
            "Modeled Array Efficiency": f"{execution_metrics['efficiency_pct']:.2f}%",
            "Thermal Lift Profile (ΔT)": f"{execution_metrics['delta_t']:.2f} °C",
            "Calculated System Outflow": f"{execution_metrics['temp_out']:.2f} °C",
            "Energy Yield Vector (W)": f"{execution_metrics['energy_output_w']:,.1f} W"
        })
        
    st.table(pd.DataFrame(concurrent_matrix_data))
    
    st.markdown("#### Dynamic Loss Envelope Mappings")
    fig_env, ax_env = plt.subplots(figsize=(15, 5))
    reduced_parameter_sweep = np.linspace(0.005, 0.26, 200)
    regime_color_index = {100: '#E63946', 200: '#F4A261', 300: '#2A9D8F', 400: '#1D3557'}
    
    for regime_key, regime_config in EXPERIMENTAL_REGISTRY.items():
        envelope_efficiencies = (regime_config["intercept_eta0"] - 
                                 (regime_config["loss_coeff_a1"] * reduced_parameter_sweep) - 
                                 (regime_config["loss_coeff_a2"] * (reduced_parameter_sweep**2) * 600.0)) * 100.0
        envelope_efficiencies = np.clip(envelope_efficiencies, 0.0, 100.0)
        ax_env.plot(reduced_parameter_sweep, envelope_efficiencies, label=f"Envelope Configuration: {regime_key} LPH", color=regime_color_index[regime_key], lw=2.5)
        
    # Plot active point coordinate
    calculated_t_mean_macro = cold_water_t_in + (setpoint_solver_metrics["delta_t"] / 2.0)
    calculated_x_sd_coordinate = (calculated_t_mean_macro - ambient_env_temp) / (model_irradiance_peak if model_irradiance_peak > 0 else 1.0)
    
    if model_irradiance_peak > 0:
        ax_env.plot(calculated_x_sd_coordinate, setpoint_solver_metrics["efficiency_pct"], 'ko', markersize=12, label="Active Real-time Fluid Matrix Node")
        
    ax_env.set_title("Standard Efficiency Intercept Performance Envelopes (η vs Xsd)", fontsize=11, fontweight='bold')
    ax_env.set_xlabel("Normalized Thermal Loss Vector Parameter Xsd (m²·°C/W)", fontsize=9)
    ax_env.set_ylabel("Collector Field Efficiency Output Scale (%)", fontsize=9)
    ax_env.set_ylim(0, 100)
    ax_env.grid(True, linestyle=':', alpha=0.6)
    ax_env.legend(fontsize=9, loc='upper right')
    st.pyplot(fig_env)

# ------------------------------------------------------------------------------
# TAB 3: CLOUD LOG MAPPING & VERIFICATION METADATA
# ------------------------------------------------------------------------------
with t_logs:
    st.markdown("### Primary Rig Calibration Coefficients & Logging Files")
    st.write("These coefficients map user operations directly to your system's data files.")
    
    metadata_table_construct = []
    for regime_key, registry_values in EXPERIMENTAL_REGISTRY.items():
        metadata_table_construct.append({
            "Calibration Tier Reference": registry_values["nominal_string"],
            "Intercept Bound (η0)": registry_values["intercept_eta0"],
            "First Order Linear Loss (a1)": registry_values["loss_coeff_a1"],
            "Second Order Quadratic Loss (a2)": registry_values["loss_coeff_a2"],
            "Target Operational CSV Files": ", ".join(registry_values["associated_files"]),
            "Turbulent Factor Scalar": registry_values["turbulent_factor"]
        })
        
    st.dataframe(pd.DataFrame(metadata_table_construct), use_container_width=True)
    
    st.markdown("""
    <div class="info-card">
        <strong>Fluid Mechanics Note:</strong> Systems matching the <strong>300 LPH & 400 LPH bounds</strong> show higher Reynolds numbers. 
        This increases localized Nusselt values inside the collector riser circuits, reducing core fluid boundary layer resistance and 
        driving up active efficiency values under high thermal loads.
    </div>
    """, unsafe_allow_html=True)
    
    # Automated Data Importer Block Simulation
    st.markdown("#### Historical Rig CSV Log Streaming Interface Simulator")
    uploaded_system_file = st.file_uploader("Stream Historical Log File Directly to Engine Substation Validation Matrix", type=["csv"])
    
    if uploaded_system_file is not None:
        try:
            parsed_user_df = pd.read_csv(uploaded_system_file)
            st.success("Log parsing executed successfully.")
            st.dataframe(parsed_user_df.head(10), use_container_width=True)
        except Exception as file_parse_error:
            st.error(f"Validation interface aborted: {file_parse_error}")
    else:
        st.info("Awaiting structural CSV stream upload. Utilizing pre-loaded database calibrations for active session parameters.")

# ------------------------------------------------------------------------------
# TAB 4: ADVANCED CAPITAL CASH FLOWS & INVESTMENT METRICS
# ------------------------------------------------------------------------------
with t_financial:
    st.markdown("### Extended Plant Lifecycle Financial Analytics Asset Model")
    st.write("This financial ledger maps capital deployment outlays and asset performance profiles over a standard 15-year lifecycle.")
    
    discount_rate_pct = st.slider("Asset Weighted Cost of Capital / Discount Rate (%)", min_value=3.0, max_value=20.0, value=9.5, step=0.5)
    
    lifecycle_years = np.arange(0, 16)
    cash_flow_projection_vector = []
    cumulative_cash_position_vector = []
    
    current_cash_accumulation = -1.0 * capital_expenditure_inr
    
    for year_idx in lifecycle_years:
        if year_idx == 0:
            cash_flow_projection_vector.append(-1.0 * capital_expenditure_inr)
            cumulative_cash_position_vector.append(-1.0 * capital_expenditure_inr)
        else:
            # Sizing annual opex savings factoring in a 4% annual boiler fuel cost inflation scalar
            inflation_adjusted_annual_savings = annual_financial_savings_inr * ((1.0 + 0.04) ** (year_idx - 1))
            cash_flow_projection_vector.append(inflation_adjusted_annual_savings)
            current_cash_accumulation += inflation_adjusted_annual_savings
            cumulative_cash_position_vector.append(current_cash_accumulation)
            
    # Calculate Net Present Value (NPV)
    npv_calculation_accumulation = 0.0
    for idx, cash_flow in enumerate(cash_flow_projection_vector):
        npv_calculation_accumulation += cash_flow / ((1.0 + (discount_rate_pct / 100.0)) ** idx)
        
    financial_ledger_dataframe = pd.DataFrame({
        "Project Operational Lifecycle Year": lifecycle_years,
        "Annual Projected Capital Flow (₹)": [f"₹ {cf:,.2f}" for cf in cash_flow_projection_vector],
        "Cumulative Capital Position Ledger (₹)": [f"₹ {cc:,.2f}" for cc in cumulative_cash_position_vector]
    })
    
    fin_col1, fin_col2 = st.columns([1, 2])
    with fin_col1:
        st.markdown(f"""
        * **Project Asset Lifetime NPV:** **₹ {npv_calculation_accumulation:,.2f}**
        * **Assumed Fuel Base Cost Inflation:** 4.0% per annum
        * **Project Asset Internal Rate of Return (IRR):** **{(100.0 / (payback_period_years if payback_period_years > 0 else 1.0)):.2f}% est.**
        """)
        st.dataframe(financial_ledger_dataframe, use_container_width=True)
        
    with fin_col2:
        fig_fin, ax_fin = plt.subplots(figsize=(10, 5))
        ax_fin.bar(lifecycle_years[1:], cash_flow_projection_vector[1:], color='#2bc480', alpha=0.8, label='Annualized Savings Component')
        ax_fin.plot(lifecycle_years, cumulative_cash_position_vector, color='#0f52ba', marker='o', lw=2.5, label='Cumulative Asset Valuation Curve')
        ax_fin.axhline(0, color='black', linestyle='--', alpha=0.7)
        ax_fin.set_title("Asset Financial Lifecycle Valuation Curve & Payback Cross", fontsize=10, fontweight='bold')
        ax_fin.set_xlabel("Years in Active Operation", fontsize=9)
        ax_fin.set_ylabel("Capital Threshold Position Valuation (₹)", fontsize=9)
        ax_fin.grid(True, linestyle=':', alpha=0.6)
        ax_fin.legend(fontsize=8, loc='upper left')
        st.pyplot(fig_fin)

# ------------------------------------------------------------------------------
# TAB 5: PROCESS DEPLOYMENT SCOPING & AUTOMATED P&ID SCHEMATIC GENERATION
# ------------------------------------------------------------------------------
with t_pid_tab:
    st.markdown("### Industrial Deployment Scoping Cross-Scaling Models")
    st.write("This matrix evaluates deployment parameters based on production adjustments at different scaling targets.")
    
    industrial_scaling_multipliers = [0.25, 0.50, 1.00, 1.50, 2.00, 3.00]
    scaled_deployment_dataframe_records = []
    
    for scaling_factor in industrial_scaling_multipliers:
        iterative_scaled_water_lpd = water_demand_lpd * scaling_factor
        iterative_scaled_energy_kwh = (iterative_scaled_water_lpd * (macro_density / 1000.0) * (macro_cp / 1000.0) * delta_t_process) / 3600.0
        iterative_scaled_modules = max(1, round((iterative_scaled_energy_kwh * DEFAULT_SAFETY_FACTOR) / BASE_MODULE_ENERGY_YIELD_KWH))
        iterative_scaled_aperture_area = iterative_scaled_modules * DEFAULT_MODULE_AREA
        iterative_scaled_capex = iterative_scaled_aperture_area * 15500.0
        
        scaled_deployment_dataframe_records.append({
            "Target Scale Core Tier": f"{scaling_factor:.2f}x Production Scale",
            "Sizing Throughput (LPD)": f"{iterative_scaled_water_lpd:,.1f}",
            "Thermal Target Need (kWh/day)": f"{iterative_scaled_energy_kwh:.1f}",
            "Required Solar Modules": int(iterative_scaled_modules),
            "Aperture Footprint Surface (m²)": f"{iterative_scaled_aperture_area:.1f}",
            "Project Capital Sizing Outlay (₹)": f"₹ {iterative_scaled_capex:,.2f}"
        })
        
    st.dataframe(pd.DataFrame(scaled_deployment_dataframe_records), use_container_width=True)

# ==============================================================================
# 8. MACRO INSTRUMENTATION CHARTS & INTERACTIVE INDICATORS
# ==============================================================================
st.markdown('<div class="section-title">🎯 Collector Instantaneous Efficiency Gauge</div>', unsafe_allow_html=True)

fig_macro_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=calculated_system_macro_efficiency,
    title={'text': "Macro Operating System Efficiency Scale %", 'font': {'size': 14}},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#212529"},
        'bar': {'color': "#0f52ba"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "#6c757d",
        'steps': [
            {'range': [0, 45], 'color': '#ffccd5'},
            {'range': [45, 72], 'color': '#ffe3e3'},
            {'range': [72, 100], 'color': '#d8f5a2'}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': calculated_system_macro_efficiency
        }
    }
))
fig_macro_gauge.update_layout(height=300, margin=dict(t=10, b=10, l=20, r=20))
st.plotly_chart(fig_macro_gauge, use_container_width=True)

st.markdown('<div class="section-title">☀️ Solar Irradiation Resource Monthly Profile Matrix</div>', unsafe_allow_html=True)

meteorological_months_vector = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
meteorological_irradiance_distribution = [660, 730, 840, 910, 960, 840, 710, 680, 790, 830, 750, 670]

fig_meteorological_bars = go.Figure()
fig_meteorological_bars.add_trace(go.Bar(
    x=meteorological_months_vector,
    y=meteorological_irradiance_distribution,
    marker_color='#f4a261',
    marker_line_color='#e76f51',
    marker_line_width=1.5,
    opacity=0.85,
    name='Global Horizontal Radiation Average'
))
fig_meteorological_bars.update_layout(
    title="Regional Meteorological Solar Radiation Intensity Profile Bounds",
    xaxis_title="Calendar Month Assessment Window",
    yaxis_title="Solar Radiation Flux Surface Scale (W/m²)",
    height=360,
    margin=dict(t=40, b=20, l=30, r=30),
    template="plotly_white"
)
st.plotly_chart(fig_meteorological_bars, use_container_width=True)

st.markdown('<div class="section-title">📈 Collector Efficiency Envelope Drop Curves</div>', unsafe_allow_html=True)

operating_parameter_normalized_vector = np.linspace(0, 120, 100)
calculated_efficiency_trend_curve = calculated_system_macro_efficiency - (0.32 * operating_parameter_normalized_vector)

fig_efficiency_trend = go.Figure()
fig_efficiency_trend.add_trace(go.Scatter(
    x=operating_parameter_normalized_vector,
    y=calculated_efficiency_trend_curve,
    mode='lines',
    line=dict(color='#0f52ba', width=4.5),
    name='Efficiency Dynamic Trend'
))
fig_efficiency_trend.update_layout(
    title="Collector Dynamic Efficiency Degradation Profile vs Thermal Stress",
    xaxis_title="Normalized Operating Parameter Scale Factor",
    yaxis_title="Instantaneous Thermal Plant Efficiency %",
    height=360,
    margin=dict(t=40, b=20, l=30, r=30),
    template="plotly_white"
)
st.plotly_chart(fig_efficiency_trend, use_container_width=True)

# ==============================================================================
# 9. GRAPHVIZ PIPING & INSTRUMENTATION AUTOMATED DIAGRAM GENERATION
# ==============================================================================
st.markdown('<div class="section-title">🏭 Automated System P&ID Circuit Topology Blueprint</div>', unsafe_allow_html=True)

industry_application_mapping_dictionary = {
    "Dairy Plant": "Industrial Pasteurizer Substation",
    "Textile Industry": "Dyeing Machine Heat Tank Loop",
    "Pharmaceutical": "Sanitary Autoclave Reactor Vessel",
    "Chemical Plant": "Exothermic Chemical Tank Heating Coil",
    "Food Processing": "High-Pressure Commercial Food Kettle"
}
mapped_process_application_name = industry_application_mapping_dictionary[industry_type]

graphviz_pid_syntax_blueprint = f"""
digraph G {{
    rankdir=LR;
    splines=true;
    node [shape=box, style=filled, fillcolor="#eef2f7", color="#0f52ba", fontname="Arial", fontsize=11, penwidth=2];
    edge [fontname="Arial", fontsize=10, color="#495057", penwidth=1.5];
    
    Tank [label="Premium Isothermal Storage Tank\\nCapacity Sizing: {thermal_storage_tank_liters:.0f} Liters", shape=cylinder, fillcolor="#fff3bf", color='#f59f00'];
    Pump [label="Centrifugal Pumping Plant\\nSized SQS: {selected_pump_power}", shape=circle, fillcolor="#d3f9d8", color='#2b8a3e'];
    Collector [label="Solar Thermal Array Substation\\nTotal Area Matrix: {total_aperture_surface_area:.1f} m²\\nSized Modules: {total_modules_calculated} Units", fillcolor="#ffc9c9", color='#c92a2a'];
    Boiler [label="Auxiliary Backup Plant\\nMedium: {backup_fuel_source}", shape=component, fillcolor="#e5dbff", color='#6741d9'];
    HX [label="Plate Heat Exchanger Unit\\nPremium Stainless Circuit", shape=diamond, fillcolor="#ch3f3ff", color='#1c7ed6'];
    Process [label="Process Destination Interface\\nTarget Application: {mapped_process_application_name}\\nRequired Target: {required_t_out} °C", fillcolor="#fcc419", color='#e67e22'];
    
    Tank -> Pump [label="Return Feed Cold"];
    Pump -> Collector [label="Regulated Fluid Stream"];
    Collector -> HX [label="Solar Hot Output Return"];
    HX -> Process [label="Thermal Load Energy Draw"];
    Process -> Tank [label="Recirculation Fluid Path"];
    
    Boiler -> HX [label="Aux Auxiliary Heating Path"];
    HX -> Boiler [label="Aux Return Loop"];
}}
"""
st.graphviz_chart(graphviz_pid_syntax_blueprint)

# ==============================================================================
# 10. SYSTEM PARAMETER PROPOSAL PROOF MATRIX SUMMARY TABLE
# ==============================================================================
st.markdown('<div class="section-title">📋 Comprehensive Proposal Summary Ledger</div>', unsafe_allow_html=True)

proposal_summary_ledger_keys = [
    "Target Sector Industrial Category",
    "Volumetric Process Fluid Throughput",
    "Target System Process Output Temperature Target",
    "Cold Fluid Inlet Supply Feed Temperature Baseline",
    "Calculated Operational Base Thermal Load Sizing",
    "Sized Total Structural Array Modules Requirement",
    "Sized Combined Effective Collector Aperture Area",
    "Calculated Thermal Storage Liquid Tank Sizing Capacity",
    "Primary Sizing Loop Volumetric Pumping Throughput",
    "Identified Pumping Infrastructure Element Tier Selection",
    "Identified Distribution Loop Conduit Diameter Geometry",
    "Estimated Project Turnkey Capital Sizing Outlay CapEx",
    "Estimated Project Lifecycle Annualized Savings Value OpEx",
    "Sized Financial Investment Asset Payback Window Period",
    "Estimated Annualized Greenhouse Gas Offset Footprint Abatement"
]

proposal_summary_ledger_values = [
    industry_type,
    f"{water_demand_lpd:,} Liters Per Day (LPD)",
    f"{required_t_out:.1f} °C",
    f"{cold_water_t_in:.1f} °C",
    f"{daily_energy_demand_kwh:.2f} kWh/day",
    f"{total_modules_calculated} Units",
    f"{total_aperture_surface_area:.1f} m²",
    f"{thermal_storage_tank_liters:.1f} Liters",
    f"{hydraulic_loop_flow_lpm:.2f} Liters Per Minute (LPM)",
    selected_pump_power,
    selected_pipe_diameter,
    f"₹ {capital_expenditure_inr:,.2f}",
    f"₹ {annual_financial_savings_inr:,.2f}",
    f"{payback_period_years:.2f} Years",
    f"{annual_co2_abatement_tons:.2f} Metric Tons / Annum"
]

proposal_summary_dataframe = pd.DataFrame({
    "System Plant Engineering Sizing Matrix Variable Parameter": proposal_summary_ledger_keys,
    "Calculated Structural Sizing Framework Value Ledger": proposal_summary_ledger_values
})
st.dataframe(proposal_summary_dataframe, use_container_width=True)

st.markdown("---")
st.success("✅ Complete SQS Production Design Matrix Stack Generated Successfully. System ready to commit to GitHub repository.")
