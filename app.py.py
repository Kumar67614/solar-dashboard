import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import csv

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SQS Solar SHIP Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.main { background-color: #f5f7fa; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

.metric-box {
    background: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #0f52ba;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}
.metric-box-orange { border-left-color: #E8650A !important; }
.metric-box-green  { border-left-color: #3B6D11 !important; }
.metric-box-amber  { border-left-color: #BA7517 !important; }
.metric-box-red    { border-left-color: #A32D2D !important; }

.metric-title { font-size: 13px; color: gray; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.metric-value { font-size: 26px; font-weight: bold; color: #111; }
.metric-sub   { font-size: 11px; color: #999; margin-top: 2px; }

.section-title {
    font-size: 22px;
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
.info-box-blue   { background:#E6F1FB; color:#185FA5; padding:10px 14px; border-radius:8px; font-size:12px; }
.info-box-amber  { background:#FAEEDA; color:#BA7517; padding:10px 14px; border-radius:8px; font-size:12px; }
.info-box-green  { background:#EAF3DE; color:#3B6D11; padding:10px 14px; border-radius:8px; font-size:12px; }
.badge-green  { background:#EAF3DE; color:#3B6D11; padding:3px 10px; border-radius:6px; font-size:12px; }
.badge-amber  { background:#FAEEDA; color:#BA7517; padding:3px 10px; border-radius:6px; font-size:12px; }
.badge-red    { background:#FCEBEB; color:#A32D2D; padding:3px 10px; border-radius:6px; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☀️ SQS Solar SHIP — Industrial Design Workbench")
st.markdown("**Solar Hot Industrial Process · Thermal Engineering Suite · ISO 9806 Compliant**")
st.markdown("---")

# =========================================================
# EXPERIMENTAL REGISTRY
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
        "associated_files": ["80_30-01-2026_SQS.csv","80_24-11-2025_SQS.csv","100_21-11-2025_SQS_.csv","70_17-02-2026_SQS.csv","60_02-02-2026_SQS.csv"]
    },
    300: {
        "nominal_string": "300 LPH Regime",
        "mean_flow_rate": 307.8,
        "intercept_eta0": 0.83,
        "loss_coeff_a1": 0.98,
        "loss_coeff_a2": 0.003,
        "min_flow_observed": 295.0,
        "max_flow_observed": 318.0,
        "associated_files": ["70_10-02-2026_SQS.csv","60_11-02-2026_SQS.csv","80__12-02-2026_SQS.csv","90_13-02-2026_SQS.csv","100_18.11.25_SQS.csv"]
    },
    400: {
        "nominal_string": "400 LPH Regime",
        "mean_flow_rate": 411.5,
        "intercept_eta0": 0.85,
        "loss_coeff_a1": 0.82,
        "loss_coeff_a2": 0.002,
        "min_flow_observed": 395.0,
        "max_flow_observed": 425.0,
        "associated_files": ["24-01-2026_SQS_80.csv","27-01-2026_SQS_70.csv","28-01-2026_SQS_Jan28_60.csv","29-01-2026_SQS_100.csv"]
    }
}

# =========================================================
# GEOGRAPHIC REGISTRY (EXPANDED — 12 CITIES)
# =========================================================

geo_registry = {
    "Srinagar (34.1°N)":        {"lat": 34.1, "base_rad": 540, "amplitude": 380, "peak_month": 5},
    "New Delhi (28.6°N)":       {"lat": 28.6, "base_rad": 660, "amplitude": 280, "peak_month": 4},
    "Jaipur (26.9°N)":          {"lat": 26.9, "base_rad": 700, "amplitude": 260, "peak_month": 4},
    "Ahmedabad (23.0°N)":       {"lat": 23.0, "base_rad": 740, "amplitude": 210, "peak_month": 4},
    "Nagpur (21.1°N)":          {"lat": 21.1, "base_rad": 720, "amplitude": 200, "peak_month": 4},
    "Kolkata (22.6°N)":         {"lat": 22.6, "base_rad": 710, "amplitude": 190, "peak_month": 4},
    "Mumbai (19.1°N)":          {"lat": 19.1, "base_rad": 760, "amplitude": 180, "peak_month": 3},
    "Pune (18.5°N)":            {"lat": 18.5, "base_rad": 775, "amplitude": 165, "peak_month": 3},
    "Hyderabad (17.4°N)":       {"lat": 17.4, "base_rad": 765, "amplitude": 155, "peak_month": 3},
    "Bengaluru (12.9°N)":       {"lat": 12.9, "base_rad": 810, "amplitude": 130, "peak_month": 2},
    "Chennai (13.1°N)":         {"lat": 13.1, "base_rad": 790, "amplitude": 140, "peak_month": 3},
    "Kochi (9.9°N)":            {"lat":  9.9, "base_rad": 820, "amplitude": 110, "peak_month": 2},
}

INDUSTRY_MAP = {
    "Dairy Plant":      {"process": "Pasteurizer",       "default_tout": 72},
    "Textile Industry": {"process": "Dyeing Machine",    "default_tout": 95},
    "Pharmaceutical":   {"process": "Reactor Vessel",    "default_tout": 60},
    "Chemical Plant":   {"process": "Chemical Reactor",  "default_tout": 90},
    "Food Processing":  {"process": "Food Heater",       "default_tout": 80},
    "Brewery":          {"process": "Mash Tun",          "default_tout": 78},
    "Paper & Pulp":     {"process": "Pulp Digester",     "default_tout": 85},
    "Rubber Plant":     {"process": "Vulcaniser",        "default_tout": 100},
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# =========================================================
# CORE PHYSICS SOLVER (HWB — ISO 9806)
# =========================================================

def solve_collector_thermodynamics(flow_rate_lph, t_in, it, t_amb, ap_area, config_dict):
    """
    Hottel-Whillier-Bliss collector model (ISO 9806):
      η = η₀ - a₁·(Tm-Ta)/G - a₂·(Tm-Ta)²/G
      Q = G · Ap · η
      ΔT = Q / (ṁ·Cp)
      Tm = Tin + ΔT/2   (iterated 8× for convergence)
    """
    cp_fluid = 4186.0
    mass_flow_sec = flow_rate_lph / 3600.0
    if it <= 0:
        return {"efficiency_pct": 0.0, "delta_t": 0.0, "temp_out": t_in, "energy_output_w": 0.0}
    t_mean_guess = t_in + 5.0
    eta = 0.0
    dt_calc = 0.0
    for _ in range(8):
        tm_param = (t_mean_guess - t_amb) / it
        eta = config_dict["intercept_eta0"] \
            - config_dict["loss_coeff_a1"] * tm_param \
            - config_dict["loss_coeff_a2"] * (tm_param ** 2) * it
        eta = max(0.0, min(eta, 0.90))
        q_gain = it * ap_area * eta
        dt_calc = q_gain / (mass_flow_sec * cp_fluid) if mass_flow_sec > 0 else 0.0
        t_mean_guess = t_in + dt_calc / 2.0
    return {
        "efficiency_pct":   eta * 100.0,
        "delta_t":          dt_calc,
        "temp_out":         t_in + dt_calc,
        "energy_output_w":  it * ap_area * eta,
    }

# =========================================================
# FINANCIAL HELPERS
# =========================================================

def calc_npv(capex, annual_savings, fuel_esc_rate, degradation_rate, lifetime_yr, discount_rate=0.08):
    """NPV with compounding fuel escalation and panel degradation."""
    cashflows = [
        annual_savings * (1 + fuel_esc_rate) ** i * (1 - degradation_rate) ** i
        for i in range(lifetime_yr)
    ]
    pv = sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(cashflows))
    return pv - capex, cashflows

def calc_irr(capex, annual_savings, lifetime_yr, fuel_esc_rate, degradation_rate):
    """Binary-search IRR — internal rate of return."""
    lo, hi = 0.0, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        pv = sum(
            annual_savings * (1 + fuel_esc_rate) ** i * (1 - degradation_rate) ** i
            / (1 + mid) ** (i + 1)
            for i in range(lifetime_yr)
        )
        if pv > capex:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0 * 100.0

def get_radiation_curve(site_meta):
    """Sinusoidal seasonal solar radiation model with monsoon correction."""
    curve = []
    for m in range(1, 13):
        ph = (m - site_meta["peak_month"]) * (np.pi / 6.0)
        val = site_meta["base_rad"] + site_meta["amplitude"] * np.cos(ph)
        if m in [6, 7, 8]:
            val *= 0.65 if site_meta["lat"] < 20 else 0.82
        curve.append(float(np.clip(val, 300, 1050)))
    return curve

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ System Configuration")

tab_proc, tab_geo, tab_adv = st.sidebar.tabs(["🏭 Process", "🗺️ Location", "📐 Advanced"])

with tab_proc:
    industry_type = st.selectbox("Industry Type", list(INDUSTRY_MAP.keys()))
    water = st.number_input("Daily Hot Water (LPD)", min_value=100, value=5000, step=100)

    auto_tout = INDUSTRY_MAP[industry_type]["default_tout"]
    tout = st.number_input("Required Outlet Temp (°C)", min_value=30, max_value=120, value=auto_tout)
    tin  = st.number_input("Cold Inlet Temp (°C)",      min_value=1,  max_value=70,  value=25)

    ambient_temp = st.slider("Ambient Temperature (°C)", 10, 45, 30)
    wind_speed   = st.slider("Wind Speed (m/s)", 0.0, 10.0, 2.0, step=0.5)

    fuel_type = st.selectbox("Backup Fuel Type", ["Diesel","Natural Gas","Electric Heater","LPG","Biomass"])
    fuel_defaults = {"Diesel":85,"Natural Gas":45,"Electric Heater":7,"LPG":60,"Biomass":30}
    fuel_cost = st.number_input("Fuel Cost (₹/unit)", value=fuel_defaults[fuel_type], min_value=1)

with tab_geo:
    selected_city = st.selectbox("Installation Site", list(geo_registry.keys()))
    tilt_angle    = st.slider("Collector Tilt Angle (°)", 0, 45, 15)
    st.caption(f"Optimal tilt ≈ site latitude ({geo_registry[selected_city]['lat']:.1f}°)")

with tab_adv:
    st.markdown("**System Lifetime & Economics**")
    lifetime_yr   = st.slider("System Lifetime (years)",       5,  30, 20)
    degradation   = st.slider("Annual Degradation (%/yr)",   0.0,  3.0, 0.5, step=0.1) / 100.0
    fuel_esc_rate = st.slider("Fuel Escalation (%/yr)",        0,   15,  5)  / 100.0
    discount_rate = st.slider("Discount Rate for NPV (%)",     4,   15,  8)  / 100.0
    st.markdown("**Collector Parameters**")
    ap_area_override = st.number_input("Aperture Area per Module (m²)", value=2.5, min_value=1.0, step=0.1)
    capex_per_m2     = st.number_input("Installed Cost (₹/m²)",         value=14000, step=500)
    st.markdown("**Calibration**")
    it_input = st.slider("Irradiance Setpoint (W/m²)", 100, 1200, 800, step=50)

st.sidebar.markdown("---")
st.sidebar.subheader("🔬 Experimental Regime")
selected_group = st.sidebar.selectbox(
    "Flow Calibration Target",
    options=[100, 200, 300, 400],
    index=2,
    format_func=lambda v: f"{v} LPH Baseline"
)

# =========================================================
# CORE CALCULATIONS
# =========================================================

active_config  = EXPERIMENTAL_REGISTRY[selected_group]
flow_input     = active_config["mean_flow_rate"]
t_in_input     = float(tin)
t_amb_input    = float(ambient_temp)
aperture_area  = float(ap_area_override)
site_meta      = geo_registry[selected_city]
cp             = 4.186          # kJ/kg·°C
safety_factor  = 1.15
module_output_base = 22.0       # kWh/day at 800 W/m² standard

# 1. Radiation curve for selected city
computed_radiation_curve = get_radiation_curve(site_meta)
average_annual_irradiance = np.mean(computed_radiation_curve)

# 2. Tilt correction factor (cosine law approximation)
tilt_factor = 1.0 + 0.02 * np.sin(np.radians(tilt_angle))  # ~2% gain at optimum tilt
regional_module_output = module_output_base * (average_annual_irradiance / 800.0) * tilt_factor

# 3. Base energy requirement
dt_proc = tout - tin
energy  = (water * cp * dt_proc) / 3600.0   # kWh/day

# 4. Sizing
gross_energy = energy * safety_factor
modules      = max(1, round(gross_energy / regional_module_output))
area         = modules * aperture_area
storage_tank = water * 1.2

# 5. Flow & hydraulics
flow_lpm   = ((modules / 2) * 250) / 60.0
flow_kghr  = flow_lpm * 60.0

# 6. HWB solver at setpoint
metrics = solve_collector_thermodynamics(
    flow_rate_lph=flow_input,
    t_in=t_in_input,
    it=it_input,
    t_amb=t_amb_input,
    ap_area=aperture_area,
    config_dict=active_config
)

# 7. System efficiency & solar fraction
efficiency   = (energy / (modules * regional_module_output)) * 100.0
efficiency   = max(35.0, min(efficiency, 85.0))
solar_fraction = min(95.0, efficiency * 1.05)

# 8. Pump / pipe
if flow_lpm < 25:   pump, pipe = "1 HP",  "DN25"
elif flow_lpm < 50: pump, pipe = "2 HP",  "DN40"
else:               pump, pipe = "5 HP",  "DN50"

# 9. Financials
annual_energy  = gross_energy * 365.0
annual_savings = annual_energy * fuel_cost * 0.25
project_cost   = area * capex_per_m2
payback        = project_cost / annual_savings if annual_savings > 0 else 0

npv_val, cashflows = calc_npv(
    project_cost, annual_savings, fuel_esc_rate, degradation, lifetime_yr, discount_rate
)
irr_val = calc_irr(project_cost, annual_savings, lifetime_yr, fuel_esc_rate, degradation)

# 10. CO₂
co2_annual   = annual_energy * 0.82 / 1000.0
co2_lifetime = co2_annual * lifetime_yr

# =========================================================
# HELPER: FORMAT INR
# =========================================================

def fmt_inr(val):
    if val >= 1e7:   return f"₹{val/1e7:.2f} Cr"
    if val >= 1e5:   return f"₹{val/1e5:.1f} L"
    return f"₹{val:,.0f}"

# =========================================================
# KPI — ROW 1: ENGINEERING
# =========================================================

st.markdown('<div class="section-title">📊 Engineering Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

kpi_data_eng = [
    (c1, "THERMAL LOAD",      f"{energy:.1f} kWh/day",       "kWh required daily",          "metric-box"),
    (c2, "SOLAR MODULES",     str(modules),                   f"× {aperture_area} m² each",  "metric-box"),
    (c3, "COLLECTOR AREA",    f"{area:.1f} m²",               "aperture area",               "metric-box"),
    (c4, "SYSTEM EFFICIENCY", f"{efficiency:.1f}%",           "ISO 9806 rated",              "metric-box metric-box-green"),
    (c5, "SOLAR FRACTION",    f"{solar_fraction:.1f}%",       "% load met by solar",         "metric-box metric-box-green"),
]
for col, title, val, sub, cls in kpi_data_eng:
    with col:
        st.markdown(f"""
        <div class="{cls}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

c6, c7, c8, c9, c10 = st.columns(5)

kpi_data_eng2 = [
    (c6,  "STORAGE TANK",     f"{storage_tank:.0f} L",        "1.2× daily demand",           "metric-box"),
    (c7,  "FLOW RATE",        f"{flow_lpm:.1f} LPM",          "circulation loop",            "metric-box"),
    (c8,  "PUMP",             pump,                           f"Pipe: {pipe}",               "metric-box"),
    (c9,  "COLLECTOR ΔT",     f"{metrics['delta_t']:.2f}°C",  "temperature rise",            "metric-box"),
    (c10, "ACTUAL OUTLET",    f"{metrics['temp_out']:.1f}°C", "from HWB solver",             "metric-box metric-box-orange"),
]
for col, title, val, sub, cls in kpi_data_eng2:
    with col:
        st.markdown(f"""
        <div class="{cls}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# =========================================================
# KPI — ROW 2: FINANCIAL
# =========================================================

st.markdown('<div class="section-title">💰 Financial Analysis</div>', unsafe_allow_html=True)

f1, f2, f3, f4, f5, f6 = st.columns(6)

kpi_fin = [
    (f1, "PROJECT CAPEX",    fmt_inr(project_cost),      "installed cost",           "metric-box metric-box-orange"),
    (f2, "ANNUAL SAVINGS",   fmt_inr(annual_savings),    "vs backup fuel",           "metric-box metric-box-green"),
    (f3, "SIMPLE PAYBACK",   f"{payback:.1f} Years",     "CapEx / Annual Savings",   "metric-box metric-box-amber"),
    (f4, "LIFETIME NPV",     fmt_inr(npv_val),           f"@ {discount_rate*100:.0f}% discount rate", "metric-box metric-box-green" if npv_val > 0 else "metric-box metric-box-red"),
    (f5, "IRR",              f"{irr_val:.1f}%",          "internal rate of return",  "metric-box metric-box-green" if irr_val > 12 else "metric-box metric-box-amber"),
    (f6, "CO₂ AVOIDED",     f"{co2_annual:.1f} T/yr",   f"{co2_lifetime:.0f} T over {lifetime_yr} yr", "metric-box metric-box-green"),
]
for col, title, val, sub, cls in kpi_fin:
    with col:
        st.markdown(f"""
        <div class="{cls}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# MAIN TABS
# =========================================================

(tab_perf, tab_finance, tab_radiation,
 tab_compare, tab_pid, tab_scaling,
 tab_meta, tab_report) = st.tabs([
    "📈 Performance Curves",
    "💹 Financial Analysis",
    "☀️ Solar Radiation",
    "🔀 Regime Comparison",
    "🏭 P&ID Diagram",
    "📏 Scaling Matrix",
    "🗃️ Experimental Metadata",
    "📋 Full Report"
])

# ==============================================================================
# TAB 1 — PERFORMANCE CURVES
# ==============================================================================

with tab_perf:

    st.subheader(f"Thermodynamic Response — {selected_group} LPH Regime")

    col1, col2 = st.columns(2)

    # ---- Efficiency vs Irradiance ----
    with col1:
        st.markdown("**Collector Efficiency vs Solar Irradiance (HWB Curve)**")
        irr_sweep  = np.linspace(100, 1200, 150)
        eff_sweep  = [solve_collector_thermodynamics(flow_input, t_in_input, G,
                        t_amb_input, aperture_area, active_config)["efficiency_pct"]
                      for G in irr_sweep]

        fig1, ax1 = plt.subplots(figsize=(7, 4))
        ax1.fill_between(irr_sweep, eff_sweep, alpha=0.15, color='#E8650A')
        ax1.plot(irr_sweep, eff_sweep, color='#E8650A', lw=2.5, label='η(G) — HWB regression')
        ax1.axvline(x=it_input, color='#185FA5', linestyle='--', lw=1.5,
                    label=f'Setpoint: {it_input} W/m²')
        ax1.axhline(y=metrics["efficiency_pct"], color='#3B6D11', linestyle=':', lw=1.2,
                    label=f'Active η: {metrics["efficiency_pct"]:.1f}%')
        ax1.set_xlabel("Solar Irradiance G (W/m²)", fontsize=9)
        ax1.set_ylabel("Collector Efficiency η (%)", fontsize=9)
        ax1.set_title("η vs G — ISO 9806 HWB Model", fontsize=10, fontweight='bold')
        ax1.grid(True, linestyle=':', alpha=0.5)
        ax1.legend(fontsize=8)
        st.pyplot(fig1)

    # ---- ΔT vs Flow Rate ----
    with col2:
        st.markdown("**Fluid Temperature Rise vs Mass Flow Rate**")
        f_min = active_config["min_flow_observed"] - 15
        f_max = active_config["max_flow_observed"] + 15
        flow_sweep = np.linspace(f_min, f_max, 100)
        dt_sweep   = [solve_collector_thermodynamics(f, t_in_input, it_input,
                        t_amb_input, aperture_area, active_config)["delta_t"]
                      for f in flow_sweep]

        fig2, ax2 = plt.subplots(figsize=(7, 4))
        ax2.fill_between(flow_sweep, dt_sweep, alpha=0.15, color='#2A9D8F')
        ax2.plot(flow_sweep, dt_sweep, color='#2A9D8F', lw=2.5, label='ΔT = Q/(ṁ·Cp)')
        ax2.axvline(x=flow_input, color='#185FA5', linestyle='--', lw=1.5,
                    label=f'Regime mean: {flow_input:.0f} LPH')
        ax2.set_xlabel("Flow Rate (LPH)", fontsize=9)
        ax2.set_ylabel("Temperature Rise ΔT (°C)", fontsize=9)
        ax2.set_title("ΔT vs Flow — Trade-off: Residence Time vs Heat Loss", fontsize=10, fontweight='bold')
        ax2.grid(True, linestyle=':', alpha=0.5)
        ax2.legend(fontsize=8)
        st.pyplot(fig2)

    col3, col4 = st.columns(2)

    # ---- Hourly Energy Profile ----
    with col3:
        st.markdown("**Hourly Solar Energy Profile (Typical Day)**")
        hours     = np.arange(24)
        hourly_kw = [max(0.0, np.sin(np.pi * (h - 6) / 12) * it_input * aperture_area / 1000.0)
                     if 6 <= h <= 18 else 0.0 for h in hours]

        fig3, ax3 = plt.subplots(figsize=(7, 3.5))
        ax3.bar(hours, hourly_kw, color='#E8650A', alpha=0.75, width=0.8, label='Solar Power (kW)')
        ax3.set_xlabel("Hour of Day", fontsize=9)
        ax3.set_ylabel("Power Output (kW)", fontsize=9)
        ax3.set_title("Diurnal Energy Profile", fontsize=10, fontweight='bold')
        ax3.set_xticks(range(0, 24, 2))
        ax3.grid(True, axis='y', linestyle=':', alpha=0.5)
        ax3.legend(fontsize=8)
        st.pyplot(fig3)

    # ---- Thermal Gain vs Ambient ----
    with col4:
        st.markdown("**Thermal Gain Sensitivity vs Ambient Temperature**")
        amb_sweep = np.linspace(10, 45, 50)
        q_sweep   = [solve_collector_thermodynamics(flow_input, t_in_input, it_input,
                        float(ta), aperture_area, active_config)["energy_output_w"] / 1000.0
                     for ta in amb_sweep]

        fig4, ax4 = plt.subplots(figsize=(7, 3.5))
        ax4.fill_between(amb_sweep, q_sweep, alpha=0.15, color='#1D3557')
        ax4.plot(amb_sweep, q_sweep, color='#1D3557', lw=2.5, label='Q_gain (kW)')
        ax4.axvline(x=ambient_temp, color='#E8650A', linestyle='--', lw=1.5,
                    label=f'Active: {ambient_temp}°C')
        ax4.set_xlabel("Ambient Temperature Ta (°C)", fontsize=9)
        ax4.set_ylabel("Thermal Power Q (kW)", fontsize=9)
        ax4.set_title("Q_gain vs Ambient — Loss Coefficient Effect", fontsize=10, fontweight='bold')
        ax4.grid(True, linestyle=':', alpha=0.5)
        ax4.legend(fontsize=8)
        st.pyplot(fig4)

    # ---- Gauge ----
    st.markdown("---")
    col_g, col_info = st.columns([1, 1])

    with col_g:
        gauge_color = ("#3B6D11" if efficiency >= 60 else "#BA7517" if efficiency >= 40 else "#A32D2D")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=efficiency,
            delta={'reference': 65, 'valueformat': '.1f'},
            title={'text': "Collector System Efficiency (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': gauge_color},
                'steps': [
                    {'range': [0,  40], 'color': "#FCEBEB"},
                    {'range': [40, 65], 'color': "#FAEEDA"},
                    {'range': [65,100], 'color': "#EAF3DE"},
                ],
                'threshold': {'line': {'color': "#185FA5", 'width': 3}, 'value': 65}
            }
        ))
        fig_gauge.update_layout(height=320, margin=dict(t=40, b=10, l=20, r=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_info:
        st.markdown("**Current Operating Point**")
        st.markdown(f"""
        | Parameter | Value |
        |---|---|
        | η₀ (Intercept) | {active_config['intercept_eta0']} |
        | a₁ (Linear loss) | {active_config['loss_coeff_a1']} W/m²K |
        | a₂ (Quadratic loss) | {active_config['loss_coeff_a2']} W/m²K² |
        | Irradiance setpoint | {it_input} W/m² |
        | Reduced temp param | {(metrics['delta_t']/2 + t_in_input - t_amb_input)/it_input:.4f} m²K/W |
        | Solver ΔT | {metrics['delta_t']:.2f} °C |
        | Outlet temperature | {metrics['temp_out']:.1f} °C |
        | Thermal power | {metrics['energy_output_w']:.0f} W |
        | Efficiency | {metrics['efficiency_pct']:.1f} % |
        """)

# ==============================================================================
# TAB 2 — FINANCIAL ANALYSIS
# ==============================================================================

with tab_finance:
    st.subheader("Lifecycle Financial Model")

    col_f1, col_f2 = st.columns(2)

    # ---- Cumulative Cash Flow ----
    with col_f1:
        st.markdown("**Cumulative Cash Flow (₹ Lakhs)**")
        cumulative = [-project_cost / 1e5]
        running    = -project_cost / 1e5
        for cf in cashflows:
            running += cf / 1e5
            cumulative.append(round(running, 2))

        years_axis  = list(range(0, lifetime_yr + 1))
        colors_cf   = ['#3B6D11' if v >= 0 else '#A32D2D' for v in cumulative]
        fig_cf = go.Figure()
        fig_cf.add_trace(go.Bar(x=years_axis, y=cumulative, marker_color=colors_cf,
                                name="Cumulative CF"))
        fig_cf.add_hline(y=0, line_dash="dash", line_color="#185FA5", line_width=1.5)
        if payback <= lifetime_yr:
            fig_cf.add_vline(x=payback, line_dash="dot", line_color="#E8650A", line_width=1.5,
                             annotation_text=f"Payback: {payback:.1f}yr")
        fig_cf.update_layout(
            xaxis_title="Year", yaxis_title="₹ Lakhs",
            height=340, margin=dict(t=20, b=40),
            showlegend=False
        )
        st.plotly_chart(fig_cf, use_container_width=True)

    # ---- Annual Savings Growth ----
    with col_f2:
        st.markdown("**Annual Savings Growth (Fuel Escalation + Degradation)**")
        annual_s_arr = [cf / 1e5 for cf in cashflows]
        fig_sv = go.Figure()
        fig_sv.add_trace(go.Bar(
            x=list(range(1, lifetime_yr + 1)),
            y=[round(v, 2) for v in annual_s_arr],
            marker_color='#3B6D11',
            name="Annual Savings"
        ))
        fig_sv.update_layout(
            xaxis_title="Year", yaxis_title="₹ Lakhs",
            height=340, margin=dict(t=20, b=40),
            showlegend=False
        )
        st.plotly_chart(fig_sv, use_container_width=True)

    # ---- IRR Sensitivity Table ----
    st.markdown("**IRR Sensitivity — Fuel Cost Scenarios**")
    fuel_pts = [30, 45, 60, 75, 85, 100, 120, 150]
    irr_rows = []
    for fc in fuel_pts:
        a_s   = annual_energy * fc * 0.25
        pb    = project_cost / a_s if a_s > 0 else 0
        npv_s, _ = calc_npv(project_cost, a_s, fuel_esc_rate, degradation, lifetime_yr, discount_rate)
        irr_s = calc_irr(project_cost, a_s, lifetime_yr, fuel_esc_rate, degradation)
        irr_rows.append({
            "Fuel Cost (₹)": fc,
            "Annual Saving (₹L)": f"{a_s/1e5:.1f}",
            "Payback (yr)":       f"{pb:.1f}",
            "Lifetime NPV (₹L)":  f"{npv_s/1e5:.1f}",
            "IRR (%)":            f"{irr_s:.1f}",
            "Viability":          "✅ Excellent" if pb <= 5 else "✅ Good" if pb <= 7 else "⚠️ Marginal" if pb <= 12 else "❌ Poor"
        })
    st.dataframe(pd.DataFrame(irr_rows), use_container_width=True)

    # ---- ROI Progress Bars ----
    st.markdown("**ROI Health Indicators**")
    r1, r2, r3, r4 = st.columns(4)
    indicators = [
        (r1, "CapEx Recovery",    min(100, 100 / payback * lifetime_yr if payback > 0 else 100), "#3B6D11"),
        (r2, "CO₂ Payback",       min(100, co2_lifetime / 50 * 10),                              "#2A9D8F"),
        (r3, "NPV Positivity",    100.0 if npv_val > 0 else 50.0,                                "#185FA5"),
        (r4, "Solar Fraction",    solar_fraction,                                                 "#E8650A"),
    ]
    for col, lbl, pct, clr in indicators:
        with col:
            st.markdown(f"**{lbl}**")
            st.progress(int(pct) / 100, text=f"{pct:.0f}%")

# ==============================================================================
# TAB 3 — SOLAR RADIATION
# ==============================================================================

with tab_radiation:
    st.subheader(f"Solar Resource Analysis — {selected_city}")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("**Monthly Solar Irradiance (W/m²)**")
        fig_rad = go.Figure(go.Bar(
            x=MONTHS, y=[round(v) for v in computed_radiation_curve],
            marker_color='#E8650A', marker_opacity=0.8
        ))
        fig_rad.update_layout(
            xaxis_title="Month", yaxis_title="W/m²",
            height=300, margin=dict(t=10, b=40)
        )
        st.plotly_chart(fig_rad, use_container_width=True)

    with col_r2:
        st.markdown("**Monthly Energy Yield Estimate (kWh)**")
        days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        monthly_yield  = []
        for i, G in enumerate(computed_radiation_curve):
            tm_est = (t_in_input + 5 - t_amb_input) / G if G > 0 else 0
            eta_m  = max(0, active_config["intercept_eta0"]
                         - active_config["loss_coeff_a1"] * tm_est
                         - active_config["loss_coeff_a2"] * tm_est ** 2 * G)
            monthly_yield.append(round(G * aperture_area * modules * eta_m * 5.5
                                       * days_per_month[i] / 1000.0))

        fig_yield = go.Figure(go.Bar(
            x=MONTHS, y=monthly_yield,
            marker_color='#185FA5', marker_opacity=0.8
        ))
        fig_yield.update_layout(
            xaxis_title="Month", yaxis_title="kWh",
            height=300, margin=dict(t=10, b=40)
        )
        st.plotly_chart(fig_yield, use_container_width=True)

    st.markdown("**City-wise Annual Average Irradiance Comparison**")
    city_names = list(geo_registry.keys())
    city_avgs  = [round(np.mean(get_radiation_curve(geo_registry[c]))) for c in city_names]
    city_colors = ['#E8650A' if c == selected_city else '#185FA5' for c in city_names]

    fig_cities = go.Figure(go.Bar(
        x=city_names, y=city_avgs,
        marker_color=city_colors, text=city_avgs, textposition='outside'
    ))
    fig_cities.update_layout(
        xaxis_title="City", yaxis_title="Average W/m²",
        height=360, margin=dict(t=10, b=80),
        xaxis_tickangle=-35
    )
    st.plotly_chart(fig_cities, use_container_width=True)

    # Radiation stats
    st.markdown("**Site Statistics**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Annual Average", f"{average_annual_irradiance:.0f} W/m²")
    sc2.metric("Peak Month",     MONTHS[np.argmax(computed_radiation_curve)])
    sc3.metric("Minimum Month",  MONTHS[np.argmin(computed_radiation_curve)])
    sc4.metric("Annual Yield",   f"{sum(monthly_yield):,} kWh")

# ==============================================================================
# TAB 4 — REGIME COMPARISON
# ==============================================================================

with tab_compare:
    st.subheader("Multi-Regime Characteristic Efficiency Envelopes")

    regime_colors = {100: '#E63946', 200: '#F4A261', 300: '#2A9D8F', 400: '#1D3557'}
    rtp_axis      = np.linspace(0.001, 0.30, 200)

    fig_env = go.Figure()
    for rk, rcfg in EXPERIMENTAL_REGISTRY.items():
        eta_env = np.clip(
            rcfg["intercept_eta0"] - rcfg["loss_coeff_a1"] * rtp_axis
            - rcfg["loss_coeff_a2"] * rtp_axis ** 2 * 500,
            0, 100
        ) * 100.0
        fig_env.add_trace(go.Scatter(
            x=rtp_axis, y=[round(v, 2) for v in eta_env],
            mode='lines', name=f'{rk} LPH',
            line=dict(color=regime_colors[rk], width=2.5)
        ))

    # Mark active operating point
    tm_cur  = t_in_input + metrics["delta_t"] / 2.0
    x_cur   = (tm_cur - t_amb_input) / it_input if it_input > 0 else 0
    fig_env.add_trace(go.Scatter(
        x=[round(x_cur, 4)], y=[round(metrics["efficiency_pct"], 1)],
        mode='markers', name='Active Point',
        marker=dict(color='black', size=12, symbol='x')
    ))
    fig_env.update_layout(
        xaxis_title="Reduced Temperature Parameter (Tm−Ta)/G  [m²K/W]",
        yaxis_title="Collector Efficiency (%)",
        yaxis_range=[0, 100],
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_env, use_container_width=True)

    # Comparative table
    st.markdown("**Simultaneous Multi-Regime Simulation at Current Setpoints**")
    cmp_rows = []
    for rk, rcfg in EXPERIMENTAL_REGISTRY.items():
        r = solve_collector_thermodynamics(
            rcfg["mean_flow_rate"], t_in_input, it_input, t_amb_input, aperture_area, rcfg
        )
        cmp_rows.append({
            "Regime":            f"{rk} LPH" + (" ◀ active" if rk == selected_group else ""),
            "η₀":                rcfg["intercept_eta0"],
            "a₁ (W/m²K)":       rcfg["loss_coeff_a1"],
            "a₂ (W/m²K²)":      rcfg["loss_coeff_a2"],
            "Mean Flow (LPH)":   rcfg["mean_flow_rate"],
            "Efficiency (%)":    f"{r['efficiency_pct']:.2f}",
            "ΔT (°C)":           f"{r['delta_t']:.2f}",
            "Outlet (°C)":       f"{r['temp_out']:.1f}",
            "Power (W)":         f"{r['energy_output_w']:.1f}",
        })
    st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True)

    # Physics insight
    if selected_group >= 300:
        st.markdown("""
        <div class="info-box-blue">
        ⚡ <strong>High Turbulent Transfer ({} LPH):</strong> High velocity → short residence time
        → lower mean temperature → reduced thermal losses → higher instantaneous efficiency.
        Trade-off: narrower ΔT across the manifold.
        </div>""".format(selected_group), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box-amber">
        🌡️ <strong>High Thermal Residence ({} LPH):</strong> Low velocity → long residence time
        → large ΔT → increased convective/radiative losses from collector surface.
        Trade-off: higher absolute temperature gain per pass.
        </div>""".format(selected_group), unsafe_allow_html=True)

# ==============================================================================
# TAB 5 — P&ID DIAGRAM
# ==============================================================================

with tab_pid:
    st.subheader(f"Industrial P&ID — {industry_type} · {INDUSTRY_MAP[industry_type]['process']}")

    process_name = INDUSTRY_MAP[industry_type]["process"]
    pid_src = f"""
digraph G {{
    rankdir=LR;
    nodesep=0.7;
    ranksep=0.85;
    graph [bgcolor="#f5f7fa" fontname="Arial"];
    edge [fontname="Arial", fontsize=9, color="#555", penwidth=1.5, arrowhead=normal, arrowsize=0.8];
    node [fontname="Arial", fontsize=10, shape=box, style="filled,bold",
          fillcolor="#ffffff", color="#2c3e50", penwidth=1.5];

    Solar [
        label="⚡  SOLAR FIELD\\n{modules} ETC Modules\\n({area:.1f} m²)\\nTilt: {tilt_angle}°"
        shape=box3d fillcolor="#FEF0E6" color="#E8650A" margin="0.2,0.1"
    ];
    Tank [
        label="TK-101\\nBuffer Tank\\n{storage_tank:.0f} L"
        shape=cylinder fillcolor="#FFF9DB" color="#F59F00" height=1.5 width=1.1
    ];
    Pump [
        label="P-101A\\n{pump}\\n{flow_lpm:.1f} LPM"
        shape=circle fillcolor="#E2F0D9" color="#385723" fixedsize=true width=1.2
    ];
    HX [
        label="HX-101\\nPlate HX\\nSolar↔Process"
        shape=diamond fillcolor="#E6F1FB" color="#185FA5" fixedsize=true width=1.4 height=1.4
    ];
    Boiler [
        label="BLR-01\\n{fuel_type}\\nAux. Boiler"
        shape=component fillcolor="#F3F0FF" color="#7048e8" height=1.3
    ];
    Process [
        label="🏭  {process_name}\\n{industry_type}\\nTarget: {tout}°C"
        shape=house fillcolor="#FBF1F5" color="#D0146F" margin="0.2,0.1"
    ];
    Makeup [
        label="FT-101\\nMakeup Water\\n{tin}°C"
        shape=parallelogram fillcolor="#F1EFE8" color="#888" width=1.0
    ];

    Tank:s  -> Pump:w  [label=" Suction\\n (gravity)" weight=2];
    Pump:e  -> Solar:w [label=" Cold Feed\\n {flow_lpm:.1f} LPM" color="#185FA5"];
    Solar:e -> HX:n    [label=" Hot Glycol\\n Return" color="#E8650A" penwidth=2.0];
    HX:s    -> Tank:n  [label=" Secondary\\n Charge Loop" color="#185FA5" penwidth=2.0];
    Tank:e  -> Process:w [label=" Hot Water\\n {tout}°C" color="#E8650A" penwidth=2.5];
    Boiler:e -> HX:w   [label=" Top-up" style=dashed color="#7048e8"];
    HX:e    -> Boiler:s [label=" Return" style=dashed color="#7048e8"];
    Process:s -> Tank:w [label=" Recirculation\\n Return" color="#748ffc"];
    Makeup:e -> Tank:w  [label=" Fresh Water\\n Inlet" color="#888" style=dashed];
}}
"""
    st.graphviz_chart(pid_src, use_container_width=True)

    st.markdown("**Component Legend**")
    leg1, leg2, leg3 = st.columns(3)
    with leg1:
        st.markdown("""
        | Tag | Component | Spec |
        |---|---|---|
        | Solar Field | ETC Array | {modules} modules, {area:.1f} m² |
        | TK-101 | Buffer Tank | {tank:.0f} L insulated |
        """.format(modules=modules, area=area, tank=storage_tank))
    with leg2:
        st.markdown("""
        | Tag | Component | Spec |
        |---|---|---|
        | P-101A | Loop Pump | {pump}, {pipe} |
        | HX-101 | Plate HX | Solar ↔ Process |
        """.format(pump=pump, pipe=pipe))
    with leg3:
        st.markdown("""
        | Tag | Component | Spec |
        |---|---|---|
        | BLR-01 | Aux. Boiler | {fuel} backup |
        | FT-101 | Makeup Water | {tin}°C supply |
        """.format(fuel=fuel_type, tin=tin))

# ==============================================================================
# TAB 6 — SCALING MATRIX
# ==============================================================================

with tab_scaling:
    st.subheader("Industrial Deployment Scaling Matrix")

    scale_factors = [0.25, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
    scaling_rows  = []
    for sf in scale_factors:
        sw    = water * sf
        se    = (sw * cp * dt_proc) / 3600.0
        sg    = se * safety_factor
        sm    = max(1, round(sg / regional_module_output))
        sa    = sm * aperture_area
        sc    = sa * capex_per_m2
        ss    = sg * 365.0 * fuel_cost * 0.25
        sp    = sc / ss if ss > 0 else 0
        snpv, _ = calc_npv(sc, ss, fuel_esc_rate, degradation, lifetime_yr, discount_rate)
        scaling_rows.append({
            "Scale":             f"{sf}×",
            "LPD":               f"{sw:,.0f}",
            "Load (kWh/d)":      f"{se:.1f}",
            "Modules":           sm,
            "Area (m²)":         f"{sa:.1f}",
            "CapEx":             fmt_inr(sc),
            "Annual Saving":     fmt_inr(ss),
            "Payback (yr)":      f"{sp:.1f}",
            "NPV":               fmt_inr(snpv),
        })

    st.dataframe(pd.DataFrame(scaling_rows), use_container_width=True)

    # Scale chart
    st.markdown("**Roof Area & CapEx vs Scale Factor**")
    fig_sc, ax_sc = plt.subplots(1, 2, figsize=(12, 4))

    areas_all   = [float(r["Area (m²)"]) for r in scaling_rows]
    capex_all   = [r["CapEx"] for r in scaling_rows]
    sf_labels   = [r["Scale"] for r in scaling_rows]
    raw_capex   = [float(r["Area (m²)"]) * capex_per_m2 for r in scaling_rows]

    ax_sc[0].bar(sf_labels, areas_all, color='#3B6D11', alpha=0.8)
    ax_sc[0].set_xlabel("Scale Factor"); ax_sc[0].set_ylabel("Collector Area (m²)")
    ax_sc[0].set_title("Required Roof Area", fontweight='bold')
    ax_sc[0].grid(True, axis='y', linestyle=':', alpha=0.5)

    ax_sc[1].bar(sf_labels, [v/1e5 for v in raw_capex], color='#E8650A', alpha=0.8)
    ax_sc[1].set_xlabel("Scale Factor"); ax_sc[1].set_ylabel("CapEx (₹ Lakhs)")
    ax_sc[1].set_title("Project CapEx", fontweight='bold')
    ax_sc[1].grid(True, axis='y', linestyle=':', alpha=0.5)

    st.pyplot(fig_sc)

# ==============================================================================
# TAB 7 — EXPERIMENTAL METADATA
# ==============================================================================

with tab_meta:
    st.subheader("Experimental Data Repository & Coefficient Matrix")

    meta_rows = []
    for rk, val in EXPERIMENTAL_REGISTRY.items():
        meta_rows.append({
            "Regime":               val["nominal_string"],
            "η₀":                   val["intercept_eta0"],
            "a₁ (W/m²K)":          val["loss_coeff_a1"],
            "a₂ (W/m²K²)":         val["loss_coeff_a2"],
            "Flow Range (LPH)":     f"{val['min_flow_observed']}–{val['max_flow_observed']}",
            "Mean Flow (LPH)":      val["mean_flow_rate"],
            "Test Sessions":        len(val["associated_files"]),
            "Log Files":            ", ".join(val["associated_files"]),
        })
    st.dataframe(pd.DataFrame(meta_rows), use_container_width=True)

    st.markdown("---")
    st.markdown("**Coefficient Comparison Radar / Bar**")

    fig_coef, axes = plt.subplots(1, 3, figsize=(13, 4))
    regimes = list(EXPERIMENTAL_REGISTRY.keys())
    cols_bar = ['#E63946','#F4A261','#2A9D8F','#1D3557']

    for ax, key, label in zip(axes, ["intercept_eta0","loss_coeff_a1","loss_coeff_a2"],
                               ["η₀ — Optical Efficiency","a₁ — Linear Loss Coeff","a₂ — Quadratic Loss Coeff"]):
        vals = [EXPERIMENTAL_REGISTRY[r][key] for r in regimes]
        ax.bar([str(r) for r in regimes], vals, color=cols_bar)
        ax.set_title(label, fontsize=9, fontweight='bold')
        ax.set_xlabel("LPH Regime"); ax.grid(True, axis='y', linestyle=':', alpha=0.5)

    st.pyplot(fig_coef)

# ==============================================================================
# TAB 8 — FULL REPORT + CSV EXPORT
# ==============================================================================

with tab_report:
    st.subheader("Design Proposal — Full Engineering Report")

    col_rn1, col_rn2 = st.columns(2)
    with col_rn1:
        st.markdown(f"""
        <div class="info-box-blue">
        ℹ️ <strong>Engineering Summary:</strong> {modules} modules covering {area:.1f} m² at
        {selected_city} (avg {average_annual_irradiance:.0f} W/m²). Simple payback {payback:.1f} yr.
        IRR {irr_val:.1f}% | NPV {fmt_inr(npv_val)}.
        </div>""", unsafe_allow_html=True)
    with col_rn2:
        equiv_trees = int(co2_annual * 50)
        st.markdown(f"""
        <div class="info-box-green">
        🌱 <strong>Environmental Impact:</strong> System avoids {co2_annual:.1f} T CO₂/yr —
        equivalent to planting ~{equiv_trees:,} trees annually.
        Lifetime reduction: {co2_lifetime:.1f} tonnes over {lifetime_yr} years.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    report_rows = [
        ("Industry",                industry_type,                          "—",          "Selected industry"),
        ("Process Equipment",       INDUSTRY_MAP[industry_type]["process"], "—",          "End-use"),
        ("City / Site",             selected_city,                          "—",          f"Lat {site_meta['lat']}°N"),
        ("Daily Water Demand",      f"{water:,}",                           "LPD",        "Input requirement"),
        ("Outlet Temperature",      tout,                                   "°C",         "Required Tout"),
        ("Inlet Temperature",       tin,                                    "°C",         "Cold supply Tin"),
        ("Temperature Rise ΔT",     dt_proc,                                "°C",         "Tout − Tin"),
        ("Thermal Load",            f"{energy:.1f}",                        "kWh/day",    "Q = V·Cp·ΔT / 3600"),
        ("Gross Energy (×1.15)",    f"{gross_energy:.1f}",                  "kWh/day",    "With safety factor"),
        ("Avg Irradiance",          f"{average_annual_irradiance:.0f}",     "W/m²",       "Annual average at site"),
        ("Tilt Angle",              tilt_angle,                             "°",          "Collector inclination"),
        ("Solar Modules",           modules,                                "units",      "Based on regional output"),
        ("Aperture Area/Module",    aperture_area,                          "m²",         "Collector spec"),
        ("Total Collector Area",    f"{area:.1f}",                          "m²",         "Modules × aperture"),
        ("Storage Tank",            f"{storage_tank:.0f}",                  "L",          "1.2× daily demand"),
        ("Flow Rate",               f"{flow_lpm:.1f}",                      "LPM",        "Circulation loop"),
        ("Pump Rating",             pump,                                   "—",          "Selected for flow+head"),
        ("Pipe Nominal",            pipe,                                   "—",          "DN sizing"),
        ("System Efficiency",       f"{efficiency:.1f}",                    "%",          "HWB + system losses"),
        ("Solar Fraction",          f"{solar_fraction:.1f}",                "%",          "% load covered"),
        ("Calibration Regime",      f"{selected_group} LPH",                "—",          f"η₀={active_config['intercept_eta0']}"),
        ("HWB Solver ΔT",           f"{metrics['delta_t']:.2f}",            "°C",         "At irradiance setpoint"),
        ("HWB Outlet Temp",         f"{metrics['temp_out']:.1f}",           "°C",         "From collector"),
        ("Thermal Power (solver)",  f"{metrics['energy_output_w']:.0f}",    "W",          "Single module"),
        ("Project CapEx",           f"{project_cost:,.0f}",                 "₹",          f"Area × ₹{capex_per_m2}/m²"),
        ("Annual Savings (Yr 1)",   f"{annual_savings:,.0f}",               "₹/yr",       "Energy × fuel × 0.25"),
        ("Fuel Type",               fuel_type,                              "—",          f"₹{fuel_cost}/unit"),
        ("Fuel Escalation",         f"{fuel_esc_rate*100:.0f}",             "%/yr",       "Price rise assumption"),
        ("Annual Degradation",      f"{degradation*100:.1f}",               "%/yr",       "Collector decay"),
        ("System Lifetime",         lifetime_yr,                            "years",      "Design horizon"),
        ("Simple Payback",          f"{payback:.1f}",                       "years",      "CapEx / Annual Savings"),
        ("Lifetime NPV",            f"{npv_val:,.0f}",                      "₹",          f"@ {discount_rate*100:.0f}% discount"),
        ("IRR",                     f"{irr_val:.1f}",                       "%",          "Internal rate of return"),
        ("CO₂ Avoided/yr",          f"{co2_annual:.1f}",                    "T/yr",       "× 0.82 kg CO₂/kWh"),
        ("Lifetime CO₂ Saving",     f"{co2_lifetime:.1f}",                  "tonnes",     f"Over {lifetime_yr} yr"),
        ("Equiv. Trees Planted",    f"{int(co2_annual*50):,}",              "/yr",        "Approximate"),
    ]

    df_report = pd.DataFrame(report_rows, columns=["Parameter", "Value", "Unit", "Notes"])
    st.dataframe(df_report, use_container_width=True, height=600)

    # ---- CSV Export ----
    st.markdown("---")
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["SQS Solar SHIP — Design Report"])
    writer.writerow([f"Generated for: {industry_type} | Site: {selected_city}"])
    writer.writerow([])
    writer.writerow(["Parameter", "Value", "Unit", "Notes"])
    for row in report_rows:
        writer.writerow(row)
    csv_data = buf.getvalue()

    st.download_button(
        label="⬇️ Download Full Report as CSV",
        data=csv_data,
        file_name="SQS_Solar_SHIP_Report.csv",
        mime="text/csv"
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.success(
    f"✅ Design Proposal Generated — {modules} modules · {area:.1f} m² · "
    f"{payback:.1f} yr payback · {irr_val:.1f}% IRR · "
    f"{co2_annual:.1f} T CO₂/yr avoided"
)
st.caption(
    "Physics engine: ISO 9806 Hottel-Whillier-Bliss model · "
    "Financial model: DCF with fuel escalation & degradation · "
    "Solar resource: Sinusoidal seasonal model with monsoon correction"
)
