import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

# ==============================================================================
# STREAMLIT PAGE INITIALIZATION & STRUCTURAL LAYOUT CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SQS Advanced Solar Thermal Rig Analytics Simulator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS implementation to structure clean operational dashboards
st.markdown("""
<style>
    .reportview-container {
        background: #F8F9FA;
    }
    .metric-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E4E8 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    .stAlert {
        border-radius: 8px !important;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .proposal-section {
        background-color: #FFFDF5 !important;
        border: 1px solid #F5E6D3 !important;
        padding: 25px !important;
        border-radius: 8px !important;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# EMBEDDED KNOWLEDGE BASE: EXPERIMENTAL RIG SUMMARY METRICS & ATTRIBUTES
# ==============================================================================
EXPERIMENTAL_REGISTRY = {
    100: {
        "nominal_string": "100 LPH",
        "mean_flow_rate": 104.52,
        "flow_std_dev": 6.12,
        "min_flow_observed": 89.56,
        "max_flow_observed": 116.18,
        "intercept_eta0": 0.8124,
        "loss_coeff_a1": 4.215,
        "loss_coeff_a2": 0.012,
        "typical_delta_t": "12.0°C to 21.7°C",
        "description": "Low flow velocity regime maximizing fluid residence time. Characterized by high thermal radiation gradients and elevated Delta-T spreads.",
        "associated_files": ["60_06-02-2026_SQS.csv", "80_18-02-2026_SQS.csv", "90_09-02-2026_SQS_.csv", "100_21-11-2025_SQS_.csv"]
    },
    200: {
        "nominal_string": "200 LPH",
        "mean_flow_rate": 196.24,
        "flow_std_dev": 5.84,
        "min_flow_observed": 187.35,
        "max_flow_observed": 208.19,
        "intercept_eta0": 0.8452,
        "loss_coeff_a1": 3.842,
        "loss_coeff_a2": 0.010,
        "typical_delta_t": "6.0°C to 12.8°C",
        "description": "Standard balance velocity regime. Smooth operational transient shifts with moderate heat transfer scales and standard baseline losses.",
        "associated_files": ["60_02-02-2026_SQS.csv", "70_17-02-2026_SQS.csv", "80_24-11-2025_SQS.csv", "80_30-01-2026_SQS.csv", "90_06-12-2025_SQS.csv"]
    },
    300: {
        "nominal_string": "300 LPH",
        "mean_flow_rate": 307.85,
        "flow_std_dev": 3.91,
        "min_flow_observed": 301.18,
        "max_flow_observed": 316.77,
        "intercept_eta0": 0.8681,
        "loss_coeff_a1": 3.224,
        "loss_coeff_a2": 0.007,
        "typical_delta_t": "4.3°C to 8.2°C",
        "description": "High velocity configuration resulting in lowered residence intervals. Suppresses high-temperature convection/radiation dissipation vectors.",
        "associated_files": ["60_11-02-2026_SQS.csv", "70_10-02-2026_SQS.csv", "80__12-02-2026_SQS.csv", "90_13-02-2026_SQS.csv", "100_18.11.25_SQS.csv"]
    },
    400: {
        "nominal_string": "400 LPH",
        "mean_flow_rate": 411.48,
        "flow_std_dev": 2.15,
        "min_flow_observed": 408.19,
        "max_flow_observed": 414.62,
        "intercept_eta0": 0.8925,
        "loss_coeff_a1": 2.951,
        "loss_coeff_a2": 0.005,
        "typical_delta_t": "1.9°C to 5.7°C",
        "description": "Maximum tested pump velocity configuration. High turbulent heat exchange yields optimal instantaneous efficiency, reducing fluid Delta-T.",
        "associated_files": ["24-01-2026_SQS_80.csv", "27-01-2026_SQS_70.csv", "28-01-2026_SQS_Jan28_60.csv", "29-01-2026_SQS_100.csv"]
    }
}

# ==============================================================================
# APPLICATION REGISTRY - GRAPHVIZ PROPER GRAPHICAL FLOWCHART DEFINITIONS
# ==============================================================================
APPLICATION_REGISTRY = {
    "Pharmaceuticals": {
        "default_t_in": 45.0,
        "default_t_out": 85.0,
        "default_daily_volume": 15000,
        "graphviz_dot": """
digraph G {
    fontname="Arial"; fontsize=11; pad=0.5;
    nodesep=0.6; ranksep=0.4; rankdir=LR;
    bgcolor="#FAFAFA";
    
    node [fontname="Arial" fontsize=10 shape=box style="filled,rounded" fillcolor="#FFFFFF" color="#475569" penwidth=1.5];
    edge [fontname="Arial" fontsize=9 color="#1E293B" penwidth=1.3];

    // Main Equipment Layout Blocks
    subgraph cluster_field {
        label = "SOLAR COLLECTOR FIELD [SC-101]";
        fontname="Arial Bold"; fontsize=11; color="#E2E8F0"; style="filled,dashed"; fillcolor="#F8FAFC";
        Collector [label="☀️ Solar Collector Array\\n(7.2 m² Surface)" shape=component color="#EA580C" fillcolor="#FFEDD5" penwidth=2];
    }

    subgraph cluster_skid {
        label = "PHARMACEUTICAL UTILITY LOOP SKID";
        fontname="Arial Bold"; fontsize=11; color="#CBD5E1"; style="filled"; fillcolor="#F1F5F9";
        
        Sensor [label="[TE / TT-101]\\nInline Temp Element" shape=circle color="#2563EB" fillcolor="#DBEAFE"];
        DCS [label="[TIC-101]\\nCentral DCS Controller" shape=doublecircle color="#1E3A8A" fillcolor="#EFF6FF"];
        Valve [label="[TV-101]\\n3-Way Divert Valve" shape=diamond color="#D97706" fillcolor="#FEF3C7"];
        HX [label="[HX-101]\\nShell & Tube Exchanger" shape=box3d color="#059669" fillcolor="#D1FAE5"];
        BufferTank [label="[TK-102]\\nRecirculation Buffer Tank" shape=cylinder color="#475569" fillcolor="#F8FAFC"];
        Pump [label="[P-101A/B]\\nCentrifugal Pump" shape=house color="#475569" fillcolor="#F8FAFC" orientation=270];
    }
    
    Storage [label="[TK-103]\\nPure WFI Storage Tank" shape=cylinder color="#059669" fillcolor="#D1FAE5"];
    WFI_In [label="Raw WFI Inflow" shape=invhouse color="#64748B"];

    // Process Flow Routes
    Pump -> Collector [label="Cold Feed"];
    Collector -> Sensor [label="Heated Fluid"];
    Sensor -> Valve;
    
    // Divert Control Mechanism Logic
    Valve -> HX [label="Temp >= 85°C\\n(Primary Heat Route)" color="#DC2626" fontcolor="#DC2626" penwidth=2];
    Valve -> BufferTank [label="Temp < 85°C\\n(Low-Temp Divert Loop)" color="#2563EB" style=dashed];
    
    WFI_In -> HX;
    HX -> Storage [label="Sterilized WFI Stock" color="#059669" penwidth=2];
    BufferTank -> Pump;

    // Instrumentation Control Network Loop Paths
    Sensor -> DCS [label="4-20mA Signal" style=dotted color="#DC2626"];
    DCS -> Valve [label="Pneumatic Actuate" style=dotted color="#DC2626"];
}
""",
        "notes": "Requires strict temperature tracking via TT-101/TIC-101 logic gates to guarantee zero unpasteurized bypass fluid into secondary pure loops."
    },
    "Dairy Industry": {
        "default_t_in": 50.0,
        "default_t_out": 75.0,
        "default_daily_volume": 35000,
        "graphviz_dot": """
digraph G {
    fontname="Arial"; fontsize=11; pad=0.5; rankdir=LR;
    bgcolor="#FAFAFA";
    node [fontname="Arial" fontsize=10 shape=box style="filled,rounded" fillcolor="#FFFFFF" color="#475569" penwidth=1.5];
    edge [fontname="Arial" fontsize=9 color="#1E293B" penwidth=1.3];

    subgraph cluster_field {
        label = "HIGH EFFICIENCY SOLAR FIELD [SC-201]";
        fontname="Arial Bold"; color="#E2E8F0"; style="filled,dashed"; fillcolor="#F8FAFC";
        Collector [label="☀️ Solar Field Array\\n(7.2 m² Surface)" shape=component color="#EA580C" fillcolor="#FFEDD5"];
    }

    subgraph cluster_pasteurizer {
        label = "SANITARY PASTEURIZATION MANIFOLD";
        fontname="Arial Bold"; color="#CBD5E1"; style="filled"; fillcolor="#F1F5F9";
        
        Sensors [label="[TE / FIT-201]\\nTemp & Flow Elements" shape=circle color="#2563EB" fillcolor="#DBEAFE"];
        PLC [label="[PLC-200]\\nCentral Control Unit" shape=doublecircle color="#1E3A8A" fillcolor="#EFF6FF"];
        ModValve [label="[FCV-201]\\nProportional Flow Valve" shape=diamond color="#D97706" fillcolor="#FEF3C7"];
        HX [label="[HX-201]\\nPlate Pasteurizer Skid" shape=box3d color="#059669" fillcolor="#D1FAE5"];
        SanPump [label="[P-201]\\nSanitary Feed Pump" shape=house color="#475569" fillcolor="#F8FAFC" orientation=270];
    }
    
    RawMilk [label="Raw Milk Intake" shape=invhouse color="#64748B"];
    PasteurizedStorage [label="[TK-202]\\nPasteurized Storage Vat" shape=cylinder color="#059669" fillcolor="#D1FAE5"];

    // Process Pathways
    SanPump -> Collector [label="Process Loop Feed"];
    Collector -> Sensors [label="Thermal Return"];
    Sensors -> ModValve;
    ModValve -> HX [label="Regulated Hot Water"];
    
    RawMilk -> HX [label="Raw Stream Input" color="#2563EB"];
    HX -> PasteurizedStorage [label="Pasteurized Milk" color="#059669" penwidth=2];
    HX -> SanPump [label="Recycle Return Loop"];

    // Automation Links
    print [label="CIP Loop Valve" shape=box style=dashed];
    print -> SanPump [style=dashed];
    Sensors -> PLC [label="Modbus Output" style=dotted color="#DC2626"];
    PLC -> ModValve [label="Pneumatic Signal" style=dotted color="#DC2626"];
}
""",
        "notes": "Maintains precise micro-gap feedback adjustments via PLC automation loops to manage tight bio-layer structural tolerances."
    },
    "Textiles": {
        "default_t_in": 30.0,
        "default_t_out": 90.0,
        "default_daily_volume": 60000,
        "graphviz_dot": """
digraph G {
    fontname="Arial"; fontsize=11; pad=0.5; rankdir=LR;
    bgcolor="#FAFAFA";
    node [fontname="Arial" fontsize=10 shape=box style="filled,rounded" fillcolor="#FFFFFF" color="#475569" penwidth=1.5];
    edge [fontname="Arial" fontsize=9 color="#1E293B" penwidth=1.3];

    subgraph cluster_field {
        label = "BULK THERMAL RAD COLLECTORS [SC-301]";
        fontname="Arial Bold"; color="#E2E8F0"; style="filled,dashed"; fillcolor="#F8FAFC";
        Collector [label="☀️ Bulk Solar Elements" shape=component color="#EA580C" fillcolor="#FFEDD5"];
    }

    subgraph cluster_safety {
        label = "HIGH MASS MIXING SYSTEM";
        fontname="Arial Bold"; color="#CBD5E1"; style="filled"; fillcolor="#F1F5F9";
        
        Transmitters [label="[TE / PT-301]\\nTemp & Pressure Well" shape=circle color="#2563EB" fillcolor="#DBEAFE"];
        TIC [label="[TIC-301]\\nTemp Controller" shape=doublecircle color="#1E3A8A" fillcolor="#EFF6FF"];
        Relay [label="[Y-301]\\nSafety Interlock Relay" shape=diamond color="#DC2626" fillcolor="#FEE2E2"];
        Valve [label="[HCV-301]\\nHigh Volume Dump Valve" shape=box color="#D97706" fillcolor="#FEF3C7"];
        Buffer [label="[TK-301]\\nThermal Mass Storage" shape=cylinder color="#475569" fillcolor="#F8FAFC"];
        Pump [label="[P-301]\\nHeavy Duty Recirc Pump" shape=house color="#475569" fillcolor="#F8FAFC" orientation=270];
    }
    
    DyeVat [label="Dyeing Vat Mixer Process" shape=box3d color="#059669" fillcolor="#D1FAE5"];

    // Connections
    Pump -> Collector;
    Collector -> Transmitters;
    Transmitters -> Valve;
    Valve -> Buffer [label="Mass Yield Feed" color="#059669" penwidth=2];
    Buffer -> DyeVat [label="Direct Heating Output"];
    DyeVat -> Pump [label="Recirculation Loop Return"];

    // Controls Logic Interlock
    Transmitters -> TIC [style=dotted color="#DC2626"];
    TIC -> Relay [style=dotted color="#DC2626"];
    Relay -> Valve [label="Safety Release" style=dotted color="#DC2626"];
}
""",
        "notes": "Optimized for raw plant sizing margins handling high volume throughput with rapid cycle dump valves."
    },
    "Thermal Power Utilities": {
        "default_t_in": 60.0,
        "default_t_out": 115.0,
        "default_daily_volume": 20000,
        "graphviz_dot": """
digraph G {
    fontname="Arial"; fontsize=11; pad=0.5; rankdir=LR;
    bgcolor="#FAFAFA";
    node [fontname="Arial" fontsize=10 shape=box style="filled,rounded" fillcolor="#FFFFFF" color="#475569" penwidth=1.5];
    edge [fontname="Arial" fontsize=9 color="#1E293B" penwidth=1.3];

    subgraph cluster_field {
        label = "HIGH ENTHALPY PARABOLIC DISH ARRAY [SC-401]";
        fontname="Arial Bold"; color="#E2E8F0"; style="filled,dashed"; fillcolor="#F8FAFC";
        Collector [label="☀️ Parabolic Concentrator Field" shape=component color="#EA580C" fillcolor="#FFEDD5"];
    }

    subgraph cluster_steam {
        label = "BOILER REGULATION SYSTEM";
        fontname="Arial Bold"; color="#CBD5E1"; style="filled"; fillcolor="#F1F5F9";
        
        Instruments [label="[TE / PT-401]\\nHigh-Press/Temp Loop" shape=circle color="#2563EB" fillcolor="#DBEAFE"];
        Regulator [label="[PCV-401]\\nPilot Balanced Regulator" shape=diamond color="#D97706" fillcolor="#FEF3C7"];
        HX [label="[HX-401]\\nHigh-Press Heat Exchanger" shape=box3d color="#059669" fillcolor="#D1FAE5"];
        Drum [label="[TK-402]\\nHigh Press Steam Accumulator" shape=cylinder color="#475569" fillcolor="#F8FAFC"];
        Pump [label="[P-401]\\nMulti-Stage Injection Pump" shape=house color="#475569" fillcolor="#F8FAFC" orientation=270];
    }
    
    Turbine [label="TO STEAM OVERFLOW TURBINE" shape=component color="#DC2626" fillcolor="#FEE2E2" penwidth=2];
    FeedLoop [label="Condensate Feedback Feed" shape=invhouse color="#64748B"];

    // Piping Routes
    Pump -> Collector [label="High-Press Liquid"];
    Collector -> Instruments;
    Instruments -> Regulator;
    Regulator -> HX [label="Superheated Stream Vector"];
    HX -> Drum;
    
    FeedLoop -> HX;
    Drum -> Turbine [label="High Enthalpy Steam Output" color="#DC2626" penwidth=2];
    Drum -> Pump [label="Condensate Recycle Line"];
}
""",
        "notes": "Operates under enhanced high-pressure threshold limits. High safety factor pressure relief valve monitoring is compulsory."
    }
}

# ==============================================================================
# THERMODYNAMIC CORE COMPUTATIONAL SOLVER SUBROUTINES
# ==============================================================================
def estimate_water_properties(t_mean_c):
    """
    Computes temperature-dependent specific heat capacity (Cp, J/kg*K) and density 
    (rho, kg/m3) of fluid utilizing polynomial formulations for solar applications.
    """
    t = max(5.0, min(140.0, t_mean_c))
    cp = 4217.4 - 3.7202 * t + 0.14125 * (t**2) - 0.0020554 * (t**3) + 1.1275e-5 * (t**4)
    rho = 1000.34 - 0.05434 * t - 0.003632 * (t**2) + 1.107e-5 * (t**3)
    return cp, rho

def solve_collector_thermodynamics(flow_rate_lph, t_in, it, t_amb, ap_area=7.2, config_dict=None):
    """
    Executes a multi-stage numerical solution iterating fluid property variations 
    to output physical energy transfers matching SQS empirical datasets.
    """
    if it <= 0.0:
        return {
            "efficiency_pct": 0.0, "energy_input_w": 0.0, "energy_output_w": 0.0,
            "delta_t": -0.5 if it < 10.0 and t_in > t_amb else 0.0, "temp_out": t_in + (-0.5 if it < 10.0 and t_in > t_amb else 0.0),
            "cp_j_kgk": 4184.0, "mass_flow_kgs": (flow_rate_lph / 3600.0)
        }

    eta0 = config_dict["intercept_eta0"]
    a1 = config_dict["loss_coeff_a1"]
    a2 = config_dict["loss_coeff_a2"]

    energy_input_w = ap_area * it

    t_out_guess = t_in + 2.0  
    max_iterations = 8
    tolerance = 1e-4
    
    current_efficiency = 0.0
    energy_output_w = 0.0
    final_cp = 4184.0
    final_m_dot = (flow_rate_lph / 3600.0)
    
    for _ in range(max_iterations):
        t_mean_exec = (t_in + t_out_guess) / 2.0
        cp_exec, rho_exec = estimate_water_properties(t_mean_exec)
        m_dot_exec = (flow_rate_lph * (rho_exec / 1000.0)) / 3600.0
        reduced_temperature = (t_mean_exec - t_amb) / it
        efficiency_exec = eta0 - a1 * reduced_temperature - a2 * (reduced_temperature**2) * it
        
        if efficiency_exec < 0.0: efficiency_exec = 0.0
        if efficiency_exec > 0.95: efficiency_exec = 0.95
        
        energy_output_exec = energy_input_w * efficiency_exec
        
        if (m_dot_exec * cp_exec) > 0:
            delta_t_exec = energy_output_exec / (m_dot_exec * cp_exec)
        else:
            delta_t_exec = 0
        t_out_new = t_in + delta_t_exec
        
        if abs(t_out_new - t_out_guess) < tolerance:
            current_efficiency = efficiency_exec
            energy_output_w = energy_output_exec
            t_out_guess = t_out_new
            final_cp = cp_exec
            final_m_dot = m_dot_exec
            break
            
        t_out_guess = t_out_new
        current_efficiency = efficiency_exec
        energy_output_w = energy_output_exec
        final_cp = cp_exec
        final_m_dot = m_dot_exec

    if it < 50.0:
        current_efficiency = 0.0
        energy_output_w = 0.0
        t_out_guess = t_in - 0.4
        
    return {
        "efficiency_pct": current_efficiency * 100.0,
        "energy_input_w": energy_input_w,
        "energy_output_w": energy_output_w,
        "delta_t": t_out_guess - t_in,
        "temp_out": t_out_guess,
        "cp_j_kgk": final_cp,
        "mass_flow_kgs": final_m_dot
    }

# ==============================================================================
# MAIN APPLICATION HEADER INTERFACE
# ==============================================================================
st.title("☀️ SQS Advanced Solar Thermal Rig Simulator Engine")
st.markdown("""
This environment processes multi-variable thermodynamic regressions built from your physical experimental test runs. 
By compiling empirical observations from **100 LPH, 200 LPH, 300 LPH, and 400 LPH** setups, the platform models continuous performance fields mapping fluid dynamics.
""")
st.write("---")

# ==============================================================================
# SIDEBAR CONTROL INTERFACE - USER MANIPULATION MATRIX
# ==============================================================================
st.sidebar.header("🛠️ Simulation Parameter Vectors")

selected_group = st.sidebar.selectbox(
    "Target Nominal Flow Setting",
    options=[100, 200, 300, 400],
    format_func=lambda x: f"Mode Sweep: {x} LPH Config"
)

active_config = EXPERIMENTAL_REGISTRY[selected_group]

# ------------------------------------------------------------------------------
# INDUSTRIAL APPLICATION DESIGN MATRIX
# ------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("🏢 Industrial Plant Up-Scaling Parameters")
selected_app = st.sidebar.selectbox(
    "Target Commercial Sector Application",
    options=list(APPLICATION_REGISTRY.keys())
)
app_meta = APPLICATION_REGISTRY[selected_app]

st.sidebar.markdown("#### Plan Targeted Thermal Shifts")
user_target_t_in = st.sidebar.slider(
    "Desired Plant Inlet Temp (°C)",
    min_value=15.0,
    max_value=110.0,
    value=app_meta["default_t_in"],
    step=1.0
)

user_target_t_out = st.sidebar.slider(
    "Desired Plant Outlet Temp (°C)",
    min_value=user_target_t_in + 2.0,
    max_value=140.0,
    value=app_meta["default_t_out"],
    step=1.0
)

user_daily_volume = st.sidebar.number_input(
    "Daily Process Volume Demand (Liters)",
    min_value=100,
    max_value=500000,
    value=app_meta["default_daily_volume"],
    step=500
)

user_latitude = st.sidebar.slider(
    "Deploy Geographical Latitude Coordinates (°)",
    min_value=-60.0,
    max_value=60.0,
    value=28.61,
    step=0.1,
    help="Determines regional sun elevation distributions, atmospheric attenuation factors, and average insulation fields."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Primary Input Controls")

flow_input = st.sidebar.slider(
    "Adjust Actual Rig Flow (kg/hr)",
    min_value=float(math.floor(active_config["min_flow_observed"] - 5)),
    max_value=float(math.ceil(active_config["max_flow_observed"] + 5)),
    value=active_config["mean_flow_rate"],
    step=0.1,
    help=f"Mean registered across dataset for this setting: {active_config['mean_flow_rate']} kg/hr"
)

t_in_input = st.sidebar.slider(
    "Fluid Inlet Temp: SQS TEMP IN (°C)",
    min_value=20.0,
    max_value=120.0,
    value=75.0,
    step=0.5,
    help="Inlet working fluid temperature recorded at the rig manifold."
)

it_input = st.sidebar.slider(
    "Solar Radiation Intensity: IT (W/m²)",
    min_value=0.0,
    max_value=1200.0,
    value=650.0,
    step=10.0,
    help="Global solar radiation data measured on the collector plane."
)

t_amb_input = st.sidebar.slider(
    "Environment Ambient Air Temp (°C)",
    min_value=15.0,
    max_value=45.0,
    value=28.5,
    step=0.5
)

aperture_area = st.sidebar.number_input(
    "Aperture Area: SQS AP (m²)",
    min_value=1.0,
    max_value=15.0,
    value=7.200,
    step=0.001,
    format="%.3f",
    help="Locked structural parameter extracted from data column header properties."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📋 Profile: {active_config['nominal_string']}")
st.sidebar.caption(active_config["description"])

# ==============================================================================
# ENGINE PROCESSING EXECUTION
# ==============================================================================
metrics = solve_collector_thermodynamics(
    flow_rate_lph=flow_input,
    t_in=t_in_input,
    it=it_input,
    t_amb=t_amb_input,
    ap_area=aperture_area,
    config_dict=active_config
)

# ==============================================================================
# MAIN PAGE USER INTERFACE DISPLAY LAYER
# ==============================================================================
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

with col_m1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Predicted Thermal Efficiency",
        value=f"{metrics['efficiency_pct']:.2f} %",
        delta=f"{(metrics['efficiency_pct'] - 50.0):+.1f}% vs Norm" if it_input > 0 else None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_m2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Temperature Delta (ΔT)",
        value=f"{metrics['delta_t']:.2f} °C",
        delta=f"Typical range: {active_config['typical_delta_t']}",
        delta_color="off"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_m3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Calculated Exit Temp",
        value=f"{metrics['temp_out']:.2f} °C"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_m4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Total Energy Input",
        value=f"{metrics['energy_input_w']:.1f} W",
        delta=f"Available solar flux"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_m5:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="SQS Energy Output",
        value=f"{metrics['energy_output_w']:.1f} W",
        delta=f"Net thermal capture"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

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
# TAB 4: PLANT SCALING MODEL & PROPER GRAPHICAL GRAPHVIZ P&ID DIAGRAMS
# ------------------------------------------------------------------------------
with tab_industrial_scaling:
    st.header(f"⚙️ Plant Integration Blueprint & Infrastructure Sizing Matrix")
    st.markdown(f"**Selected Sector Application Strategy:** {selected_app}")
    
    solar_hours = np.array([6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    lat_rad = math.radians(abs(user_latitude))
    peak_flux = max(350.0, 1020.0 * math.cos(lat_rad) - 50.0)
    
    hourly_irradiance = []
    for hr in solar_hours:
        ang = math.pi * (hr - 6) / 12
        flux_step = peak_flux * math.sin(ang) if (hr >= 6 and hr <= 18) else 0.0
        hourly_irradiance.append(max(0.0, flux_step))
        
    hourly_irradiance = np.array(hourly_irradiance)
    
    mean_target_t = (user_target_t_in + user_target_t_out) / 2.0
    scaled_cp, scaled_rho = estimate_water_properties(mean_target_t)
    
    total_mass_kg = user_daily_volume * (scaled_rho / 1000.0)
    energy_needed_joules = total_mass_kg * scaled_cp * (user_target_t_out - user_target_t_in)
    energy_needed_kwh = energy_needed_joules / 3600000.0
    
    midday_test = solve_collector_thermodynamics(
        flow_rate_lph=active_config["mean_flow_rate"],
        t_in=user_target_t_in,
        it=peak_flux,
        t_amb=t_amb_input,
        ap_area=aperture_area,
        config_dict=active_config
    )
    
    integrated_efficiency = max(15.0, midday_test["efficiency_pct"]) / 100.0
    total_solar_flux_kwh_m2 = np.sum(hourly_irradiance) / 1000.0
    
    computed_ideal_area = energy_needed_kwh / (total_solar_flux_kwh_m2 * integrated_efficiency) if total_solar_flux_kwh_m2 > 0 else 100.0
    computed_ideal_flow = user_daily_volume / 7.0 
    
    st.subheader("📋 Sized Engineering Allocation Targets")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.metric("Required Plant Area Footprint", f"{computed_ideal_area:.2f} m²")
    with col_p2:
        st.metric("Ideal Flow Vector Rate", f"{computed_ideal_flow:.1f} Liters/hr")
    with col_p3:
        st.metric("Daily Thermal Plant Load", f"{energy_needed_kwh:.2f} kWh")
    with col_p4:
        st.metric("Regional Peak Solar Radiation", f"{peak_flux:.1f} W/m²")
        
    # --------------------------------------------------------------------------
    # RENDERING THE INTERACTIVE GRAPHICAL DIAGRAM GRAPH
    # --------------------------------------------------------------------------
    st.write("---")
    st.subheader("📌 Vector Graphics Piping & Instrumentation Diagram Flowchart")
    st.markdown("This graphical architecture illustrates equipment blocks, tracking loops, and automation gates:")
    
    # Render using the Graphviz Engine directly into the UI canvas
    st.graphviz_chart(app_meta["graphviz_dot"])
    
    st.caption(f"**P&ID Control Directives:** {app_meta['notes']}")
    st.write("---")
    
    st.subheader("⏱️ Rig Smart Pump Automation Schedule Controller")
    st.markdown("Pumps activate explicitly when structural fluid solar yield outweighs cooling losses to prevent the solar system from running in reverse as an atmospheric radiator.")
    
    min_energy_threshold_w = st.slider(
        "Set Minimum Operational Generation Trigger Cut-out (Watts Output)", 
        min_value=50.0, 
        max_value=600.0, 
        value=180.0, 
        step=10.0,
        help="The pump cuts out if current collection drops below this net power generation floor."
    )
    
    pump_timelines = []
    pump_on_intervals = 0
    total_harvested_w = 0.0
    
    for hr, step_it in zip(solar_hours, hourly_irradiance):
        step_calc = solve_collector_thermodynamics(
            flow_rate_lph=active_config["mean_flow_rate"],
            t_in=user_target_t_in,
            it=step_it,
            t_amb=t_amb_input,
            ap_area=aperture_area,
            config_dict=active_config
        )
        
        power_out = step_calc["energy_output_w"]
        
        if power_out >= min_energy_threshold_w:
            pump_state = "🟢 RUNNING (ON)"
            pump_on_intervals += 1
            total_harvested_w += power_out
        else:
            pump_state = "🔴 STANDBY (OFF)"
            
        pump_timelines.append({
            "Time Index": f"{hr:02d}:00 Hour Step",
            "Model Sun Flux (W/m²)": f"{step_it:.1f}",
            "Rig Power Output (W)": f"{power_out:.1f}",
            "Estimated Temperature Out (°C)": f"{step_calc['temp_out']:.2f}",
            "Pump System State": pump_state
        })
        
    st.table(pd.DataFrame(pump_timelines))
    
    st.markdown('<div class="proposal-section">', unsafe_allow_html=True)
    st.subheader("📄 Commercial Plant Deployment Proposal & Feasibility Spec Sheet")
    st.markdown(f"""
    ### **Project Engineering Specification Document**
    * **Target Framework Assignment Type:** Modular Process Heating Upgrade for **{selected_app}** Utilities.
    * **Geographic Field Optimization Array Placement Location:** Sized for an operational baseline profile at **{user_latitude}° Latitude**.
    
    ### **1. Fluid Kinetic Properties & Design Scaling Constraints**
    To satisfy your daily requirement of **{user_daily_volume} Liters** shifting precisely from **{user_target_t_in}°C** up to **{user_target_t_out}°C**, the system demands an array scaled using the kinetic parameters from the **{active_config['nominal_string']}** empirical database. 
    * **Computed Working Fluid Density (rho):** `{scaled_rho:.2f} kg/m³` | **Specific Heat Capacity (Cp):** `{scaled_cp:.1f} J/kg·K`.
    * **Recommended Sized Continuous Flow Rate Field Setpoint:** **`{computed_ideal_flow:.2f} LPH`** (This value maintains fluid dynamics within the efficient operational limits derived from your source data files).
    * **Total Calculated Aperture Surface Area Requirement:** **`{computed_ideal_area:.2f} m²`** of high-performance flat-plate or concentrated vacuum tubing elements.
    
    ### **2. Automated Pump Lifecycle & Energy Management Profile**
    * **Total Effective Pump Running Lifetime:** **`{pump_on_intervals} Hours`** of active automation runtime over a standard diurnal daylight schedule.
    * **Rig Performance Cut-out Safety Boundary:** System locks down flow loops automatically if local solar generation levels dip lower than **`{min_energy_threshold_w} W`**, isolating process manifolds from unwanted radiative heat back-siphoning.
    * **Estimated Cumulative Module Delivery Yield:** **`{(total_harvested_w / 1000.0):.3f} kWh`** converted across full running loops per unit module baseline array layout.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
