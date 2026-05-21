import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 🎨 Premium Compact Styling & Border Matrix Boundaries
st.markdown("""
    <style>
    .metric-container {
        background-color: #f8f9fa; padding: 12px; border-radius: 6px;
        border-top: 4px solid #0f52ba; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 12px; border-left: 1px solid #e9ecef;
        border-right: 1px solid #e9ecef; border-bottom: 1px solid #e9ecef;
    }
    .metric-title { font-size: 11px; color: #4a5568; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 4px;}
    .metric-value { font-size: 20px; color: #1a202c; font-weight: bold; }
    .section-header { color: #0f52ba; font-weight: bold; border-bottom: 2px solid #0f52ba; padding-bottom: 4px; margin-top: 20px; margin-bottom: 12px;}
    .card-box { background: #ffffff; padding: 15px; border-radius: 6px; box-shadow: 0 1px 5px rgba(0,0,0,0.05); margin-bottom: 12px; border: 1px solid #e9ecef; }
    div.block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 SQS Solar Collector Field Performance & BOP Sizing Platform")
st.markdown("---")

# 🖥️ SIDEBAR DATA INGESTION
st.sidebar.header("📁 Experimental Log Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Drop SQS experimental log files here", 
    type=["csv"], 
    accept_multiple_files=True
)

# Fallback defaults if no file is uploaded yet
if not uploaded_files:
    st.info("📥 Please drag and drop your experimental SQS log files into the sidebar to activate the dynamic tracking matrix.")
else:
    # Dropdown selector for uploaded testing logs
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.sidebar.selectbox("🎯 Select Active Log Dataset for Real-Time Analysis", file_names)
    active_file = uploaded_files[file_names.index(selected_file_name)]
    
    # Read files with robust encoding checks to fix variations in temperature headers
    try:
        df = pd.read_csv(active_file, encoding='utf-8')
    except Exception:
        active_file.seek(0)
        df = pd.read_csv(active_file, encoding='latin1')
        
    # Strip spaces from columns
    df.columns = [c.strip() for c in df.columns]
    
    # Helper mapping to find corresponding columns dynamically across variations
    def find_col(possible_names):
        for c in df.columns:
            if any(p.upper() in c.upper() for p in possible_names):
                return c
        raise ValueError(f"Required column trace missing. Inspected patterns: {possible_names}")

    # Standard columns from your logs
    col_tin = find_col(["TEMP IN", "TEMP_IN"])
    col_tout = find_col(["TEMP OUT", "TEMP_OUT"])
    col_tamb = find_col(["AMBIENT TEMP", "AMBIENT_TEMP"])
    col_rad = find_col(["IT(", "RADIATION", "W/m2", "W/m²"])
    col_flow = find_col(["FLOW RATE", "O FLOW", "FLOW_RATE"])
    col_eff = find_col(["Efficiency", "Eff"])
    col_xsd = find_col(["XSD", "X_SD"])

    # Data Scrubbing: Remove initial calibration state points (radiation = 0 or low flow lines)
    df_clean = df[(df[col_rad] > 50) & (df[col_flow] > 5)].copy()
    if df_clean.empty:
        df_clean = df.copy()

    # Core statistical parsing from real data streams
    avg_tin = float(df_clean[col_tin].mean())
    avg_tout = float(df_clean[col_tout].mean())
    avg_tamb = float(df_clean[col_tamb].mean())
    avg_rad = float(df_clean[col_rad].mean())
    avg_flow = float(df_clean[col_flow].mean())
    avg_eff = float(df_clean[col_eff].mean())
    avg_xsd_val = float(df_clean[col_xsd].mean()) if col_xsd in df_clean.columns else 0.05
    
    # Standardize efficiency formatting (decimal conversion if logged as 0-100 percentage scale)
    if avg_eff > 1.0:
         avg_eff /= 100.0

    # 🎛️ AUTOMATED LPH CLASSIFICATION AND HYDRAULIC EQUIPMENT MATRIX MAPPING
    if avg_flow < 150:
        target_flow_class = "100 LPH System Profile"
        pump_hp = "1.0 HP VFD Pump"
        pipe_size_dn = "DN25 (1\" Line Schedule)"
        pipe_color = "#4caf50"
        industry_note = "Optimized for micro-grid configurations and slow velocity heat transitions."
    elif avg_flow < 250:
        target_flow_class = "200 LPH System Profile"
        pump_hp = "1.5 HP VFD Pump"
        pipe_size_dn = "DN32 (1.25\" Line Schedule)"
        pipe_color = "#2196f3"
        industry_note = "Standard baseline loop profile. Balancing valve arrays operate mid-range."
    elif avg_flow < 350:
        target_flow_class = "300 LPH System Profile"
        pump_hp = "3.0 HP VFD Pump"
        pipe_size_dn = "DN40 (1.5\" Line Schedule)"
        pipe_color = "#ff9800"
        industry_note = "High thermal volume configuration. Requires augmented loop insulation limits."
    else:
        target_flow_class = "400 LPH System Profile"
        pump_hp = "5.0 HP VFD Pump"
        pipe_size_dn = "DN50 (2\" Line Schedule)"
        pipe_color = "#e53935"
        industry_note = "Maximum throughput design field. Demands industrial scale manifold arrays."

    # 🔢 ENGINEERING PHYSICAL EQUATION SOLVER
    cp = 4.186  # Water heat capacity kJ/kg·K
    dt = max(0.1, avg_tout - avg_tin)
    thermal_output_kw = (avg_flow * cp * dt) / 3600.0
    
    # Back-calculate thermal loss parameter based on standard performance curves
    eta_0_nominal = 0.82
    u_total_loss = (eta_0_nominal - avg_eff) / avg_xsd_val if avg_xsd_val > 0 else 4.5
    u_total_loss = max(1.0, min(u_total_loss, 12.0))

    # Plant storage scales
    storage_tank_capacity = avg_flow * 6.5  # Sized for daily circulation scale buffer
    flow_lpm = avg_flow / 60.0

    # Environmental Abatement Calculations (Annualized Metrics)
    annual_thermal_load_kwh = thermal_output_kw * 8 * 300
    fuel_saved_liters = (annual_thermal_load_kwh * 860) / (10200 * 0.82)
    co2_reduction_tons = (fuel_saved_liters * 2.68) / 1000.0

    # Notify configuration status to operator
    st.info(f"📊 **Active Dataset Analysis Engine:** Processing **{selected_file_name}** | Automatically Classified: **`{target_flow_class}`**")

    # SECTION 1: RUNTIME EXPERIMENTAL METRICS
    st.markdown('<h3 class="section-header">🧮 I. Live Experimental Thermal Performance Metrics</h3>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-container"><div class="metric-title">AVG MASS FLOW RATE</div><div class="metric-value">🌊 {avg_flow:.1f} <span style="font-size:12px;">kg/hr</span></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-container" style="border-top-color: #2a9d8f;"><div class="metric-title">ENERGY HARVESTED</div><div class="metric-value">⚡ {thermal_output_kw:.2f} <span style="font-size:12px;">kW_th</span></div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-container" style="border-top-color: #f4a261;"><div class="metric-title">OPERATING EFFICIENCY</div><div class="metric-value">🎯 {avg_eff*100:.1f}%</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-container" style="border-top-color: #e63946;"><div class="metric-title">FIELD LOSS COEFFICIENT</div><div class="metric-value">🌡️ {u_total_loss:.2f} <span style="font-size:12px;">W/m²K</span></div></div>', unsafe_allow_html=True)

    # SECTION 2: BALANCE OF PLANT DESIGN OUTPUTS
    st.markdown('<h3 class="section-header">⚙️ II. Derived Balance of Plant (BOP) Fluid Sizing</h3>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"""
        <div class="card-box" style="border-left: 4px solid #2196f3;">
            <h4 style="margin-top:0; margin-bottom:5px; color:#2196f3; font-size:14px;">📦 Storage Volume Spec</h4>
            <div style="background-color:#e3f2fd; padding:4px; border-radius:4px; font-weight:bold; color:#0d47a1; text-align:center; margin-bottom:8px; font-size:12px;">
                Buffer Tank Capacity: {storage_tank_capacity:,.0f} Liters
            </div>
            <span style="font-size:12px;">
            • Average Loop Inlet Feed: <b>{avg_tin:.1f}°C</b>.<br>
            • Average Loop Outlet Delivery: <b>{avg_tout:.1f}°C</b>.<br>
            • Temperature Delta ($ΔT$): <b>{dt:.1f}°C</b>.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        st.markdown(f"""
        <div class="card-box" style="border-left: 4px solid #ff9800;">
            <h4 style="margin-top:0; margin-bottom:5px; color:#ff9800; font-size:14px;">🗺️ Line Sizing Layout</h4>
            <div style="background-color:#fff3e0; padding:4px; border-radius:4px; font-weight:bold; color:#e65100; text-align:center; margin-bottom:8px; font-size:12px;">
                Pipe Specification: {pipe_size_dn}
            </div>
            <span style="font-size:12px;">
            • Sized for a steady mass flow of <b>{avg_flow:.1f} kg/hr</b>.<br>
            • Designed to keep fluid velocity values in check.<br>
            • Minimizes system friction and head pressure drop losses.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        st.markdown(f"""
        <div class="card-box" style="border-left: 4px solid #4caf50;">
            <h4 style="margin-top:0; margin-bottom:5px; color:#4caf50; font-size:14px;">🎛️ Motive Fluid Control</h4>
            <div style="background-color:#e8f5e9; padding:4px; border-radius:4px; font-weight:bold; color:#1b5e20; text-align:center; margin-bottom:8px; font-size:12px;">
                Circulation Rating: {pump_hp}
            </div>
            <span style="font-size:12px;">
            • Loop Volumetric Index: <b>{flow_lpm:.2f} LPM</b>.<br>
            • Dynamic configuration notes: <i>{industry_note}</i><br>
            • Modulates flow loop based on solar radiation variance.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 3: VISUALIZATION CHARTS
    st.markdown('<h3 class="section-header">📊 III. Experimental Efficiency Scatter & Solar Radiation Profiles</h3>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        x_max_lim = max(0.25, df_clean[col_xsd].max() if col_xsd in df_clean.columns else 0.2)
        x_curve = np.linspace(0, x_max_lim, 100)
        y_curve = (eta_0_nominal - (u_total_loss * x_curve)) * 100
        y_curve = np.clip(y_curve, 0, 100)
        
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Scatter(x=x_curve, y=y_curve, mode='lines', name='Regressed Curve Fit', line=dict(color='#0f52ba', width=2.5)))
        
        eff_multiplier = 100 if df_clean[col_eff].max() <= 1.0 else 1
        fig_eff.add_trace(go.Scatter(
            x=df_clean[col_xsd], y=df_clean[col_eff] * eff_multiplier, 
            mode='markers', name='Logged Scatters', marker=dict(color='#2a9d8f', size=4, opacity=0.5)
        ))
        fig_eff.update_layout(
            title="🎯 Thermal Parameter Curve vs Data Scatters",
            xaxis_title="Reduced Temp Parameter X_SD", yaxis_title="Efficiency (%)",
            plot_bgcolor='white', height=250, margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig_eff, use_container_width=True)

    with chart_col2:
        fig_rad = go.Figure()
        timeline_x = df_clean['Time'] if 'Time' in df_clean.columns else np.arange(len(df_clean))
        fig_rad.add_trace(go.Scatter(
            x=timeline_x, y=df_clean[col_rad], mode='lines', name='Logged GHI Intensity', line=dict(color='#f4a261', width=2)
        ))
        fig_rad.update_layout(
            title=f"☀️ Solar Intensity Timeline (Mean: {avg_rad:.1f} W/m²)",
            xaxis_title="Test Progress Timeline", yaxis_title="Radiation Intensity (W/m²)",
            plot_bgcolor='white', height=250, margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_rad, use_container_width=True)

    # SECTION 4: DIAGRAM AUTOMATION BY FLOW RATIO
    st.markdown('<h3 class="section-header">📐 IV. Process Flow Schematic (Dynamically Adapting to Selected Fluid Class)</h3>', unsafe_allow_html=True)
    st.graphviz_chart(f"""
    digraph G {{
        size="12,4.5!"; ratio="fill"; rankdir=LR; splines=ortho; nodesep=0.2; ranksep=0.3;
        node [fontname="Helvetica", fontsize=9, penwidth=1.2];
        edge [fontname="Helvetica-Bold", fontsize=8, penwidth=1.2];

        node [shape=triangle, fixedsize=true, width=0.22, height=0.15, style=filled, fillcolor="#b0bec5", color="#37474f"];
        valv_in [label=""]; valv_out [label=""]; valv_ret [label=""]; valv_by [label=""];
        
        node [shape=diamond, fixedsize=true, width=0.2, height=0.2, fillcolor="#eceff1", label="Y"]; strainer [label=""];
        node [shape=circle, fixedsize=true, width=0.48, style=filled, fillcolor="#e0f7fa", color="#006064", fontname="Helvetica-Bold", fontsize=8];
        TT_101 [label="TT\\n101"]; TT_102 [label="TT\\n102"]; TIC_101 [label="TIC\\n101", fillcolor="#fff9c4", color="#f57f17"];

        node [shape=box, style="filled,rounded", width=1.4, height=0.8, color="#0f52ba", fillcolor="#f8f9fa", fontsize=9];
        Inlet [label="📥 SUPPLY CONTAINER\\nFeed Water Line\\n({avg_tin:.1f}°C Logged)", shape=cds, fillcolor="#e3f2fd"];
        
        subgraph cluster_solar {{
            label="☀️ EXPERIMENTAL COLLECTOR CIRCUITS"; color="#c62828"; style="dashed,rounded"; bgcolor="#fffde7";
            Array_A [label="SOLAR COLLECTOR ARRAYS\\nField Circuit Row Run\\n({avg_flow:.1f} kg/h Loop)", fillcolor="#ffebee", color="#e53935", width=2.2, height=0.6];
        }}

        Tank [label="🛢 BUFFER TANK\\nTK-101 Storage\\n({storage_tank_capacity:,.0f} Liters)", shape=cylinder, fillcolor="#fff3cd", color="#f9a825", width=1.4, height=1.4];
        Process [label="🏭 PLANT DELIVERY NODE\\nThermal Flow Out\\n({avg_tout:.1f}°C Delivery)", shape=cds, fillcolor="{pipe_color}", color="#1c1c1e", width=1.8];

        node [shape=component, width=0.5, height=0.35, fillcolor="#e8f5e9", color="#2e7d32"];
        Pump_P1 [label="Pump P-1\\n({pump_hp})"];

        Inlet -> strainer [color="#0f52ba"];
        strainer -> valv_in [color="#0f52ba"];
        valv_in -> Tank [color="#0f52ba"];
        Tank -> Pump_P1 [color="#0f52ba"];
        Pump_P1 -> Array_A [color="#0f52ba", label=" {flow_lpm:.2f} LPM"];
        Array_A -> TT_101 [color="#c62828"];
        TT_101 -> valv_out [color="#c62828"];
        valv_out -> Tank [color="#c62828"];
        Tank -> TT_102 [color="#c62828"];
        TT_102 -> valv_ret [color="#c62828"];
        valv_ret -> Process [color="#c62828"];
        valv_ret -> valv_by [color="#f9a825"];
        valv_by -> Tank [color="#f9a825"];

        edge [style=dashed, color="#757575", penwidth=1.0, arrowhead=dot];
        TT_101 -> TIC_101; TT_102 -> TIC_101; TIC_101 -> Pump_P1; TIC_101 -> valv_ret;
    }}
    """)

    # SECTION 5: PROPOSAL MATRIX SUMMARY
    st.markdown('<h3 class="section-header">📋 V. Comprehensive Engineering Project Summary Matrix</h3>', unsafe_allow_html=True)
    st.markdown(f"""
    | Performance Matrix Field | Values Processed Directly From Experimental Runs |
    | :--- | :--- |
    | **Auto-Identified Evaluation Grid Class** | 📊 `{target_flow_class.upper()}` |
    | **Logged Fluid Mass Flow Rate** | 🌊 **{avg_flow:.2f} kg/hour** |
    | **Mean Incident Solar Irradiance ($I_T$)** | ☀️ **{avg_rad:.1f} W/m²** |
    | **Net Thermal Power Output Peak** | ⚡ **{thermal_output_kw:.2f} kW Thermal Energy Yield** |
    | **Calculated Field Heat Loss Exponent ($U_L$)** | 🌡️ **{u_total_loss:.2f} W/m²K** |
    | **Automated BOP Pipe Sizing Boundary** | 📐 **{pipe_size_dn}** |
    | **Motive Loop Pump Horsepower Target** | 🎛️ **{pump_hp}** |
    | **Annual Carbon Abatement Metric** | 🍃 **{co2_reduction_tons:.2f} Metric Tons of CO₂ Saved/Year** |
    """, unsafe_allow_html=True)
