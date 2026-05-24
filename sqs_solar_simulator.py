import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

# Enhanced CSS with more attractive, pictorial styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%); }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label { color: #94A3B8 !important; font-size:0.8rem !important; }

    .metric-card {
        background: linear-gradient(135deg, #1E293B, #0F172A) !important;
        border: 1px solid #334155 !important;
        padding: 18px 16px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
    }
    .metric-card [data-testid="stMetricValue"] { color: #F97316 !important; font-weight: 700 !important; }
    .metric-card [data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 0.75rem !important; }

    .stTabs [data-baseweb="tab-list"] {
        background: #1E293B;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #334155;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94A3B8 !important;
        font-weight: 500;
        font-size: 0.82rem;
        padding: 8px 14px;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #F97316, #EA580C) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(249,115,22,0.4);
    }

    h1 { color: #F1F5F9 !important; font-weight: 700 !important; letter-spacing:-0.5px; }
    h2, h3 { color: #E2E8F0 !important; font-weight: 600 !important; }
    p, .stMarkdown { color: #CBD5E1 !important; }

    .stTable, .stDataFrame { background: #1E293B !important; border-radius: 10px !important; overflow: hidden; }
    .stTable thead tr th { background: #334155 !important; color: #F1F5F9 !important; }
    .stTable tbody tr td { color: #CBD5E1 !important; border-color: #334155 !important; }

    hr { border-color: #334155 !important; }

    .proposal-section {
        background: linear-gradient(135deg, #1E293B, #0F172A) !important;
        border: 1px solid #334155 !important;
        border-left: 4px solid #F97316 !important;
        padding: 28px !important;
        border-radius: 12px !important;
        margin-top: 20px;
    }

    .stAlert { border-radius: 10px !important; }
    .stInfo { background: #0F2942 !important; border-color: #1D4ED8 !important; }
    .stWarning { background: #1C0E00 !important; border-color: #D97706 !important; }

    div[data-testid="stDecoration"] { display: none; }

    .pid-container {
        background: #F8FAFC;
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        padding: 8px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
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
# PROFESSIONAL ISA-STANDARD SVG P&ID DIAGRAMS — ONE PER APPLICATION
# ==============================================================================

_PID_DEFS = """
  <defs>
    <marker id="mR" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#DC2626"/></marker>
    <marker id="mB" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#2563EB"/></marker>
    <marker id="mG" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#059669"/></marker>
    <marker id="mD" markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0,7 2.5,0 5" fill="#64748B"/></marker>
    <marker id="mS" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#7C3AED"/></marker>
  </defs>
"""

def _legend(x, y, items):
    """Generate a legend block at (x,y) with given items list of (color,dash,label,symbol)."""
    h = "<rect x='{x}' y='{y}' width='210' height='{h}' fill='white' stroke='#CBD5E1' stroke-width='1.5' rx='6'/>".format(
        x=x, y=y, h=22 + len(items)*22 + 8)
    h += "<rect x='{x}' y='{y}' width='210' height='22' fill='#1E293B' rx='5'/>".format(x=x, y=y)
    h += "<text x='{cx}' y='{ty}' text-anchor='middle' font-size='9' font-weight='bold' fill='white'>LEGEND — ISA 5.1</text>".format(
        cx=x+105, ty=y+15)
    for i, (color, dash, label) in enumerate(items):
        iy = y + 22 + 10 + i*22
        ds = f"stroke-dasharray='{dash}'" if dash else ""
        h += f"<line x1='{x+12}' y1='{iy+6}' x2='{x+52}' y2='{iy+6}' stroke='{color}' stroke-width='2.5' {ds}/>"
        h += f"<text x='{x+60}' y='{iy+10}' font-size='7.5' fill='#1E293B'>{label}</text>"
    return h

def _instr_bubble(cx, cy, top, bot, color="#2563EB", bg="#EFF6FF"):
    return (f"<circle cx='{cx}' cy='{cy}' r='20' fill='{bg}' stroke='{color}' stroke-width='2'/>"
            f"<line x1='{cx-20}' y1='{cy}' x2='{cx+20}' y2='{cy}' stroke='{color}' stroke-width='1'/>"
            f"<text x='{cx}' y='{cy-4}' text-anchor='middle' font-size='7.5' font-weight='bold' fill='#1E293B'>{top}</text>"
            f"<text x='{cx}' y='{cy+10}' text-anchor='middle' font-size='7.5' fill='#1E293B'>{bot}</text>")

def _pump(cx, cy, tag, label):
    return (f"<circle cx='{cx}' cy='{cy}' r='26' fill='white' stroke='#475569' stroke-width='2'/>"
            f"<polygon points='{cx-14},{cy-14} {cx-14},{cy+14} {cx+18},{cy}' fill='#94A3B8' stroke='#475569' stroke-width='1'/>"
            f"<text x='{cx}' y='{cy+42}' text-anchor='middle' font-size='7.5' font-weight='bold' fill='#1E293B'>{tag}</text>"
            f"<text x='{cx}' y='{cy+53}' text-anchor='middle' font-size='7' fill='#64748B'>{label}</text>")

def _valve(cx, cy, tag, label, color="#D97706", bg="#FEF3C7"):
    return (f"<polygon points='{cx-20},{cy-16} {cx+20},{cy} {cx-20},{cy+16}' fill='{bg}' stroke='{color}' stroke-width='2'/>"
            f"<polygon points='{cx+20},{cy-16} {cx-20},{cy} {cx+20},{cy+16}' fill='{bg}' stroke='{color}' stroke-width='2'/>"
            f"<text x='{cx}' y='{cy+32}' text-anchor='middle' font-size='7.5' font-weight='bold' fill='#1E293B'>{tag}</text>"
            f"<text x='{cx}' y='{cy+43}' text-anchor='middle' font-size='7' fill='#64748B'>{label}</text>")

def _three_way_valve(cx, cy, tag, label):
    return (f"<polygon points='{cx-22},{cy-14} {cx+22},{cy} {cx-22},{cy+14}' fill='#FEF3C7' stroke='#D97706' stroke-width='2'/>"
            f"<polygon points='{cx+22},{cy-14} {cx-22},{cy} {cx+22},{cy+14}' fill='#FEF3C7' stroke='#D97706' stroke-width='2'/>"
            f"<line x1='{cx}' y1='{cy}' x2='{cx}' y2='{cy+22}' stroke='#D97706' stroke-width='2'/>"
            f"<circle cx='{cx}' cy='{cy}' r='5' fill='#D97706'/>"
            f"<text x='{cx}' y='{cy+36}' text-anchor='middle' font-size='7.5' font-weight='bold' fill='#1E293B'>{tag}</text>"
            f"<text x='{cx}' y='{cy+47}' text-anchor='middle' font-size='7' fill='#64748B'>{label}</text>")

def _hx_shell_tube(x, y, w, h, tag, label):
    return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='#D1FAE5' stroke='#059669' stroke-width='2' rx='4'/>"
            f"<path d='M {x+12} {y+h//3} Q {x+22} {y+h//3-10} {x+32} {y+h//3} Q {x+42} {y+h//3+10} {x+52} {y+h//3} Q {x+62} {y+h//3-10} {x+72} {y+h//3} Q {x+82} {y+h//3+10} {x+92} {y+h//3}' stroke='#059669' stroke-width='1.5' fill='none'/>"
            f"<path d='M {x+12} {y+2*h//3} Q {x+22} {y+2*h//3-10} {x+32} {y+2*h//3} Q {x+42} {y+2*h//3+10} {x+52} {y+2*h//3} Q {x+62} {y+2*h//3-10} {x+72} {y+2*h//3} Q {x+82} {y+2*h//3+10} {x+92} {y+2*h//3}' stroke='#059669' stroke-width='1.5' fill='none'/>"
            f"<line x1='{x}' y1='{y+h//2}' x2='{x+w}' y2='{y+h//2}' stroke='#059669' stroke-width='0.8' stroke-dasharray='3,2'/>"
            f"<text x='{x+w//2}' y='{y+h+15}' text-anchor='middle' font-size='8' font-weight='bold' fill='#1E293B'>{tag}</text>"
            f"<text x='{x+w//2}' y='{y+h+26}' text-anchor='middle' font-size='7' fill='#64748B'>{label}</text>")

def _tank(x, y, w, h, tag, line1, line2, color="#475569", bg="#F1F5F9", fill_color="#E2E8F0"):
    ex, ew = x + w//2, w//2
    ey = h//5
    return (f"<rect x='{x}' y='{y+ey}' width='{w}' height='{h-ey}' fill='{bg}' stroke='{color}' stroke-width='2' rx='3'/>"
            f"<ellipse cx='{ex}' cy='{y+ey}' rx='{ew}' ry='{ey}' fill='{fill_color}' stroke='{color}' stroke-width='2'/>"
            f"<ellipse cx='{ex}' cy='{y+h}' rx='{ew}' ry='{ey}' fill='{bg}' stroke='{color}' stroke-width='2'/>"
            f"<text x='{ex}' y='{y + h//2 + 4}' text-anchor='middle' font-size='7.5' font-weight='bold' fill='#1E293B'>{tag}</text>"
            f"<text x='{ex}' y='{y + h//2 + 16}' text-anchor='middle' font-size='7' fill='#1E293B'>{line1}</text>"
            f"<text x='{ex}' y='{y + h//2 + 27}' text-anchor='middle' font-size='7' fill='#475569'>{line2}</text>")

def _solar_panel(x, y, w, h, tag):
    rows, cols = 4, 3
    cw, ch = w // cols, h // rows
    cells = ""
    for r in range(rows):
        for c in range(cols):
            cells += f"<rect x='{x+c*cw+2}' y='{y+r*ch+2}' width='{cw-4}' height='{ch-4}' fill='#1E40AF' rx='1' opacity='0.7'/>"
    sun = (f"<circle cx='{x+w//2}' cy='{y+h//2}' r='18' fill='#FCD34D' stroke='#F59E0B' stroke-width='1.5'/>"
           f"<text x='{x+w//2}' y='{y+h//2+5}' text-anchor='middle' font-size='14'>☀</text>")
    return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='#BFDBFE' stroke='#1E40AF' stroke-width='2' rx='4'/>"
            + cells + sun
            + f"<text x='{x+w//2}' y='{y+h+14}' text-anchor='middle' font-size='8' font-weight='bold' fill='#1E3A8A'>{tag}</text>")

def _title_bar(text, sub=""):
    return (f"<rect x='0' y='0' width='1100' height='38' fill='#1E293B' rx='8'/>"
            f"<text x='550' y='20' text-anchor='middle' font-size='11' font-weight='bold' fill='#F97316'>{text}</text>"
            f"<text x='550' y='32' text-anchor='middle' font-size='8' fill='#94A3B8'>{sub}</text>")

def _boundary(x, y, w, h, label, color="#EA580C"):
    return (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='none' stroke='{color}' stroke-width='1.5' stroke-dasharray='7,4' rx='6'/>"
            f"<rect x='{x+10}' y='{y-8}' width='{len(label)*6+10}' height='16' fill='white' rx='3'/>"
            f"<text x='{x+15}' y='{y+5}' font-size='8' font-weight='bold' fill='{color}'>{label}</text>")

# --- PHARMACEUTICAL P&ID ---
PHARMA_PID_HTML = f"""
<div style="background:#F1F5F9;border-radius:12px;padding:10px;border:1.5px solid #CBD5E1;">
<svg viewBox="0 0 1100 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;font-family:Arial,sans-serif;">
{_PID_DEFS}
{_title_bar("PHARMACEUTICAL SOLAR WFI PROCESS HEATING — P&amp;ID [SC-101]","ISA 5.1 Standard · WFI Sterilization Loop · Shell &amp; Tube Heat Exchange")}
{_boundary(12,48,190,240,"SOLAR COLLECTOR FIELD [SC-101]","#EA580C")}
{_solar_panel(22,58,170,210,"7.2 m² Flat Plate Array")}
{_boundary(215,108,760,215,"PHARMACEUTICAL UTILITY LOOP SKID","#475569")}
<line x1="192" y1="163" x2="255" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<text x="220" y="155" text-anchor="middle" font-size="7.5" fill="#DC2626">Heated Fluid</text>
{_pump(283,163,"[P-101A/B]","Centrifugal")}
<line x1="309" y1="163" x2="365" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_instr_bubble(390,163,"TE/TT","101")}
<line x1="410" y1="163" x2="455" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<line x1="390" y1="183" x2="390" y2="290" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
<text x="400" y="243" font-size="7" fill="#64748B">4-20mA</text>
{_instr_bubble(390,315,"TIC","101","#1E3A8A","#EFF6FF")}
<line x1="410" y1="315" x2="510" y2="315" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3"/>
<line x1="510" y1="315" x2="510" y2="203" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
<text x="455" y="307" text-anchor="middle" font-size="7" fill="#64748B">Pneumatic Actuate</text>
{_three_way_valve(510,163,"[TV-101]","3-Way Divert")}
<line x1="532" y1="163" x2="580" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<text x="556" y="153" text-anchor="middle" font-size="7" fill="#DC2626">T ≥ 85°C</text>
{_hx_shell_tube(580,120,110,88,"[HX-101]","Shell &amp; Tube")}
<line x1="690" y1="163" x2="730" y2="163" stroke="#059669" stroke-width="2.5" marker-end="url(#mG)"/>
{_instr_bubble(755,163,"TT","102","#2563EB","#DBEAFE")}
<line x1="775" y1="163" x2="820" y2="163" stroke="#059669" stroke-width="2.5" marker-end="url(#mG)"/>
{_tank(820,95,100,150,"[TK-103]","Pure WFI","Storage","#059669","#D1FAE5","#A7F3D0")}
<line x1="868" y1="95" x2="868" y2="72" stroke="#DC2626" stroke-width="1.5"/>
<polygon points="860,72 876,72 868,60" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>
<text x="888" y="70" font-size="7.5" font-weight="bold" fill="#DC2626">PSV</text>
<line x1="635" y1="120" x2="635" y2="80" stroke="#2563EB" stroke-width="2" stroke-dasharray="none" marker-end="url(#mB)"/>
<rect x="570" y="55" width="120" height="24" fill="#DBEAFE" stroke="#2563EB" stroke-width="1.5" rx="4"/>
<text x="630" y="71" text-anchor="middle" font-size="8" font-weight="bold" fill="#2563EB">Raw WFI Inflow</text>
<line x1="510" y1="185" x2="510" y2="340" stroke="#2563EB" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#mB)"/>
<text x="528" y="268" font-size="7" fill="#2563EB">T &lt; 85°C</text>
<text x="528" y="279" font-size="7" fill="#2563EB">Divert Loop</text>
{_tank(448,340,122,100,"[TK-102]","Recirculation","Buffer Tank","#475569","#F1F5F9","#E2E8F0")}
<line x1="448" y1="392" x2="283" y2="392" stroke="#2563EB" stroke-width="2"/>
<line x1="283" y1="392" x2="283" y2="189" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
<text x="360" y="384" text-anchor="middle" font-size="7.5" fill="#2563EB">Cold Feed Return Loop</text>
<line x1="259" y1="163" x2="192" y2="163" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
<text x="226" y="155" text-anchor="middle" font-size="7" fill="#2563EB">Cold Feed</text>
{_legend(880,270,[("#DC2626","","Hot Process Water (Supply)"),("#2563EB","","Cold Water / Return Feed"),("#059669","","Sterile WFI Product Flow"),("#64748B","4,3","Instrument Signal (ISA)")  ])}
<text x="885" y="420" font-size="7" fill="#1E293B">● TT: Temp Transmitter   ● TIC: Temp Indicator/Controller</text>
<text x="885" y="432" font-size="7" fill="#1E293B">● TV: Temperature Valve   ● PSV: Pressure Safety Valve</text>
<rect x="12" y="460" width="1076" height="35" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4"/>
<text x="20" y="475" font-size="7.5" font-weight="bold" fill="#1E293B">P&amp;ID NOTES:</text>
<text x="95" y="475" font-size="7.5" fill="#475569">Strict temperature interlock via TT-101/TIC-101 logic gates guarantees zero unpasteurized bypass into secondary pure WFI loops. Redundant pump P-101A/B.</text>
<text x="20" y="488" font-size="7.5" fill="#475569">Divert valve TV-101 actuates pneumatically on 4-20mA signal. PSV sized per ASME Sec.VIII. Comply with FDA cGMP 21 CFR Part 11 and WHO GMP annexure.</text>
</svg></div>"""

# --- DAIRY INDUSTRY P&ID ---
DAIRY_PID_HTML = f"""
<div style="background:#F1F5F9;border-radius:12px;padding:10px;border:1.5px solid #CBD5E1;">
<svg viewBox="0 0 1100 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;font-family:Arial,sans-serif;">
{_PID_DEFS}
{_title_bar("DAIRY INDUSTRY SOLAR PASTEURIZATION SYSTEM — P&amp;ID [SC-201]","ISA 5.1 Standard · HTST Pasteurization Loop · Plate Heat Exchanger")}
{_boundary(12,48,190,240,"SOLAR FIELD [SC-201]","#EA580C")}
{_solar_panel(22,58,170,210,"7.2 m² High-Eff. Array")}
{_boundary(215,108,760,215,"SANITARY PASTEURIZATION MANIFOLD","#475569")}
<line x1="192" y1="165" x2="255" y2="165" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<text x="222" y="156" text-anchor="middle" font-size="7.5" fill="#DC2626">Process Loop Feed</text>
{_pump(283,165,"[P-201]","Sanitary Feed")}
<line x1="309" y1="165" x2="358" y2="165" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_instr_bubble(383,165,"TE","201")}
<line x1="403" y1="165" x2="435" y2="165" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_instr_bubble(460,165,"FIT","201","#059669","#D1FAE5")}
<line x1="480" y1="165" x2="520" y2="165" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<line x1="460" y1="185" x2="460" y2="300" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
{_instr_bubble(460,325,"PLC","200","#1E3A8A","#EFF6FF")}
<line x1="480" y1="325" x2="550" y2="325" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3"/>
<line x1="550" y1="325" x2="550" y2="205" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
<text x="500" y="316" text-anchor="middle" font-size="7" fill="#64748B">Modbus→Pneumatic</text>
{_valve(550,165,"[FCV-201]","Proportional Flow")}
<line x1="572" y1="165" x2="610" y2="165" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<text x="590" y="155" text-anchor="middle" font-size="7" fill="#DC2626">Regulated Hot Water</text>
<rect x="610" y="118" width="120" height="94" fill="#D1FAE5" stroke="#059669" stroke-width="2" rx="4"/>
<line x1="622" y1="118" x2="622" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="634" y1="118" x2="634" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="646" y1="118" x2="646" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="658" y1="118" x2="658" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="670" y1="118" x2="670" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="682" y1="118" x2="682" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="694" y1="118" x2="694" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="706" y1="118" x2="706" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="718" y1="118" x2="718" y2="212" stroke="#059669" stroke-width="1.2"/>
<line x1="610" y1="165" x2="730" y2="165" stroke="#059669" stroke-width="1" stroke-dasharray="3,2"/>
<text x="670" y="230" text-anchor="middle" font-size="8" font-weight="bold" fill="#1E293B">[HX-201]</text>
<text x="670" y="241" text-anchor="middle" font-size="7" fill="#64748B">Plate Pasteurizer</text>
<line x1="670" y1="118" x2="670" y2="78" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
<rect x="590" y="54" width="160" height="24" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" rx="4"/>
<text x="670" y="69" text-anchor="middle" font-size="8" font-weight="bold" fill="#DC2626">Raw Milk Intake Stream</text>
<line x1="730" y1="145" x2="790" y2="145" stroke="#059669" stroke-width="2.5" marker-end="url(#mG)"/>
<text x="760" y="136" text-anchor="middle" font-size="7" fill="#059669">Pasteurized Milk</text>
{_tank(790,85,110,155,"[TK-202]","Pasteurized","Storage Vat","#059669","#D1FAE5","#A7F3D0")}
<line x1="730" y1="185" x2="770" y2="185" stroke="#DC2626" stroke-width="2"/>
<line x1="770" y1="185" x2="770" y2="250" stroke="#DC2626" stroke-width="2"/>
<line x1="770" y1="250" x2="283" y2="250" stroke="#DC2626" stroke-width="2"/>
<line x1="283" y1="250" x2="283" y2="191" stroke="#DC2626" stroke-width="2" marker-end="url(#mR)"/>
<text x="520" y="242" text-anchor="middle" font-size="7.5" fill="#DC2626">Thermal Return / CIP Recirculation Loop</text>
<line x1="259" y1="165" x2="192" y2="165" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
{_legend(880,270,[("#DC2626","","Hot Solar Loop / Supply"),("#2563EB","","Cold Feed / Return"),("#059669","","Pasteurized Milk Product"),("#64748B","4,3","Instrument / Control Signal")])}
<text x="885" y="420" font-size="7" fill="#1E293B">● FIT: Flow Indicator Transmitter   ● PLC: Programmable Logic Controller</text>
<text x="885" y="432" font-size="7" fill="#1E293B">● FCV: Flow Control Valve  ● CIP: Clean-In-Place Circuit</text>
<rect x="12" y="460" width="1076" height="35" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4"/>
<text x="20" y="475" font-size="7.5" font-weight="bold" fill="#1E293B">P&amp;ID NOTES:</text>
<text x="95" y="475" font-size="7.5" fill="#475569">PLC-200 monitors TE-201 and FIT-201 to maintain HTST 72°C/15s hold. Plate HX cleaned via CIP loop. Compliant with EC 853/2004 dairy hygiene regulations.</text>
<text x="20" y="488" font-size="7.5" fill="#475569">All wetted surfaces 316L SS, Ra ≤ 0.8μm. FCV-201 modulates to maintain Δ-T setpoint. PRV fitted on pasteurized side. SCADA trend-logging mandatory.</text>
</svg></div>"""

# --- TEXTILES INDUSTRY P&ID ---
TEXTILE_PID_HTML = f"""
<div style="background:#F1F5F9;border-radius:12px;padding:10px;border:1.5px solid #CBD5E1;">
<svg viewBox="0 0 1100 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;font-family:Arial,sans-serif;">
{_PID_DEFS}
{_title_bar("TEXTILE INDUSTRY SOLAR DYE BATH HEATING SYSTEM — P&amp;ID [SC-301]","ISA 5.1 Standard · High-Mass Thermal Dump · Safety Interlock Architecture")}
{_boundary(12,48,190,240,"BULK THERMAL COLLECTORS [SC-301]","#EA580C")}
{_solar_panel(22,58,170,210,"7.2 m² Bulk Rad. Elements")}
{_boundary(215,108,760,215,"HIGH MASS MIXING SYSTEM","#475569")}
<line x1="192" y1="163" x2="255" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_pump(283,163,"[P-301]","HD Recirc Pump")}
<line x1="309" y1="163" x2="358" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_instr_bubble(383,163,"TE","301")}
<line x1="403" y1="163" x2="435" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_instr_bubble(460,163,"PT","301","#7C3AED","#EDE9FE")}
<line x1="480" y1="163" x2="520" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
<line x1="460" y1="183" x2="460" y2="295" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
{_instr_bubble(460,320,"TIC","301","#1E3A8A","#EFF6FF")}
<line x1="480" y1="320" x2="525" y2="320" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3"/>
<rect x="525" y="305" width="60" height="30" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" rx="4"/>
<text x="555" y="318" text-anchor="middle" font-size="7.5" font-weight="bold" fill="#DC2626">[Y-301]</text>
<text x="555" y="329" text-anchor="middle" font-size="6.5" fill="#DC2626">Safety Relay</text>
<line x1="555" y1="305" x2="555" y2="205" stroke="#DC2626" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
<text x="566" y="255" font-size="7" fill="#DC2626">Safety Trip</text>
{_valve(555,163,"[HCV-301]","High-Vol Dump")}
<line x1="577" y1="163" x2="615" y2="163" stroke="#DC2626" stroke-width="2.5" marker-end="url(#mR)"/>
{_tank(615,105,115,155,"[TK-301]","Thermal Mass","Storage","#475569","#F8FAFC","#E2E8F0")}
<line x1="730" y1="163" x2="790" y2="163" stroke="#059669" stroke-width="2.5" marker-end="url(#mG)"/>
<rect x="790" y="118" width="120" height="90" fill="#D1FAE5" stroke="#059669" stroke-width="2" rx="6"/>
<text x="850" y="155" text-anchor="middle" font-size="8" font-weight="bold" fill="#1E293B">Dyeing Vat</text>
<text x="850" y="167" text-anchor="middle" font-size="7.5" fill="#059669">Mixer Process</text>
<line x1="791" y1="178" x2="800" y2="178" stroke="#2563EB" stroke-width="2"/>
<text x="850" y="178" text-anchor="middle" font-size="8">🌀</text>
<line x1="790" y1="178" x2="715" y2="178" stroke="#2563EB" stroke-width="2"/>
<line x1="715" y1="178" x2="715" y2="250" stroke="#2563EB" stroke-width="2"/>
<line x1="715" y1="250" x2="283" y2="250" stroke="#2563EB" stroke-width="2"/>
<line x1="283" y1="250" x2="283" y2="189" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
<text x="490" y="242" text-anchor="middle" font-size="7.5" fill="#2563EB">Recirc Return Loop — Dye Bath Cooled Return</text>
<line x1="259" y1="163" x2="192" y2="163" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
{_legend(880,270,[("#DC2626","","Hot Solar Supply Loop"),("#2563EB","","Cooled Recirc Return"),("#059669","","Process Heat Delivery"),("#DC2626","4,3","Safety Interlock Signal")])}
<text x="885" y="420" font-size="7" fill="#1E293B">● PT: Pressure Transmitter   ● Y: Safety Interlock Relay</text>
<text x="885" y="432" font-size="7" fill="#1E293B">● HCV: High-Volume Control Valve   ● TIC: Temp Indicator/Controller</text>
<rect x="12" y="460" width="1076" height="35" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4"/>
<text x="20" y="475" font-size="7.5" font-weight="bold" fill="#1E293B">P&amp;ID NOTES:</text>
<text x="95" y="475" font-size="7.5" fill="#475569">Safety interlock Y-301 trips HCV-301 on PT-301 overpressure or TE-301 overtemperature. Thermal mass TK-301 buffers batch demand spikes. Rapid dump valve sized for full volumetric flow.</text>
<text x="20" y="488" font-size="7.5" fill="#475569">System compliant with OEKO-TEX thermal standards. Dye bath uniformity maintained via recirc pump cycling. All pipe materials CS-HDPE rated for 120°C continuous service.</text>
</svg></div>"""

# --- THERMAL POWER UTILITIES P&ID ---
POWER_PID_HTML = f"""
<div style="background:#F1F5F9;border-radius:12px;padding:10px;border:1.5px solid #CBD5E1;">
<svg viewBox="0 0 1100 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;font-family:Arial,sans-serif;">
{_PID_DEFS}
{_title_bar("THERMAL POWER — SOLAR STEAM GENERATION SYSTEM — P&amp;ID [SC-401]","ISA 5.1 Standard · High-Enthalpy Parabolic Array · Steam Accumulator &amp; Turbine Feed")}
{_boundary(12,48,190,240,"PARABOLIC DISH ARRAY [SC-401]","#EA580C")}
<rect x="22" y="58" width="170" height="210" fill="#1E3A8A" stroke="#1E40AF" stroke-width="2" rx="6"/>
<ellipse cx="107" cy="85" rx="75" ry="20" fill="#3B82F6" stroke="#60A5FA" stroke-width="1.5"/>
<ellipse cx="107" cy="130" rx="75" ry="20" fill="#2563EB" stroke="#60A5FA" stroke-width="1.5"/>
<ellipse cx="107" cy="175" rx="75" ry="20" fill="#1D4ED8" stroke="#60A5FA" stroke-width="1.5"/>
<circle cx="107" cy="85" r="12" fill="#FCD34D" stroke="#F59E0B" stroke-width="1.5"/>
<circle cx="107" cy="130" r="12" fill="#FCD34D" stroke="#F59E0B" stroke-width="1.5"/>
<circle cx="107" cy="175" r="12" fill="#FCD34D" stroke="#F59E0B" stroke-width="1.5"/>
<text x="107" y="220" text-anchor="middle" font-size="8" font-weight="bold" fill="white">Parabolic Concentrator</text>
<text x="107" y="232" text-anchor="middle" font-size="7.5" fill="#93C5FD">High Enthalpy Array</text>
{_boundary(215,108,760,215,"BOILER REGULATION SYSTEM","#475569")}
<line x1="192" y1="163" x2="255" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
<text x="222" y="153" text-anchor="middle" font-size="7.5" fill="#DC2626">Hi-Press Liquid</text>
{_pump(283,163,"[P-401]","Multi-Stage Inj.")}
<line x1="309" y1="163" x2="355" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
{_instr_bubble(380,163,"TE","401")}
<line x1="400" y1="163" x2="430" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
{_instr_bubble(455,163,"PT","401","#7C3AED","#EDE9FE")}
<line x1="475" y1="163" x2="518" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
<line x1="455" y1="183" x2="455" y2="295" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
{_instr_bubble(455,320,"PIC","401","#1E3A8A","#EFF6FF")}
<line x1="475" y1="320" x2="545" y2="320" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3"/>
<line x1="545" y1="320" x2="545" y2="205" stroke="#64748B" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#mD)"/>
<text x="500" y="311" text-anchor="middle" font-size="7" fill="#64748B">Pilot Pressure Signal</text>
{_valve(545,163,"[PCV-401]","Pilot Regulator")}
<line x1="567" y1="163" x2="610" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
<text x="590" y="153" text-anchor="middle" font-size="7" fill="#DC2626">Superheated</text>
{_hx_shell_tube(610,120,110,86,"[HX-401]","Hi-Press HX")}
<line x1="720" y1="163" x2="760" y2="163" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
{_tank(760,90,115,160,"[TK-402]","Hi-Press Steam","Accumulator","#475569","#FEE2E2","#FECACA")}
<line x1="875" y1="165" x2="940" y2="165" stroke="#DC2626" stroke-width="3" marker-end="url(#mR)"/>
<rect x="940" y="130" width="120" height="70" fill="#FEE2E2" stroke="#DC2626" stroke-width="2.5" rx="6"/>
<polygon points="952,145 952,185 980,165" fill="#DC2626" opacity="0.6"/>
<polygon points="970,145 970,185 998,165" fill="#DC2626" opacity="0.4"/>
<text x="1000" y="162" text-anchor="middle" font-size="8" font-weight="bold" fill="#991B1B">TURBINE</text>
<text x="1000" y="174" text-anchor="middle" font-size="7" fill="#DC2626">Steam Overflow</text>
<line x1="775" y1="250" x2="775" y2="290" stroke="#2563EB" stroke-width="2"/>
<line x1="775" y1="290" x2="283" y2="290" stroke="#2563EB" stroke-width="2"/>
<line x1="283" y1="290" x2="283" y2="189" stroke="#2563EB" stroke-width="2" marker-end="url(#mB)"/>
<rect x="360" y="275" width="180" height="18" fill="#DBEAFE" stroke="#2563EB" stroke-width="1" rx="3"/>
<text x="450" y="287" text-anchor="middle" font-size="7.5" fill="#1E3A8A" font-weight="bold">Condensate Feedback Return Line</text>
<line x1="259" y1="163" x2="192" y2="163" stroke="#2563EB" stroke-width="2.5" marker-end="url(#mB)"/>
<line x1="760" y1="135" x2="742" y2="115" stroke="#DC2626" stroke-width="1.5"/>
<polygon points="734,110 750,110 742,98" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>
<text x="718" y="107" font-size="7.5" font-weight="bold" fill="#DC2626">PSV</text>
{_legend(880,290,[("#DC2626","","High-Enthalpy Steam Supply"),("#2563EB","","Condensate / Cold Return"),("#7C3AED","","Pressure Instrument Loop"),("#64748B","4,3","Control / Pilot Signal")])}
<text x="885" y="430" font-size="7" fill="#1E293B">● PT: Pressure Transmitter   ● PCV: Pressure Control Valve</text>
<text x="885" y="442" font-size="7" fill="#1E293B">● PSV: Pressure Safety Valve   ● PIC: Pressure Indicator/Controller</text>
<rect x="12" y="460" width="1076" height="35" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4"/>
<text x="20" y="475" font-size="7.5" font-weight="bold" fill="#1E293B">P&amp;ID NOTES:</text>
<text x="95" y="475" font-size="7.5" fill="#475569">High-pressure operation — all components rated min. 25 bar(g). PSV sized per API 520/521. PCV-401 maintains steam accumulator pressure within ±0.2 bar. PRV on turbine inlet mandatory.</text>
<text x="20" y="488" font-size="7.5" fill="#475569">Multi-stage injection pump P-401 rated for 30 bar suction head. Condensate returned via deaerator DA-401 (not shown). Comply with ASME B31.1 Power Piping and IEC 61511 SIL.</text>
</svg></div>"""

# ==============================================================================
# APPLICATION REGISTRY — SVG P&ID DIAGRAMS REPLACING GRAPHVIZ
# ==============================================================================
APPLICATION_REGISTRY = {
    "Pharmaceuticals": {
        "default_t_in": 45.0,
        "default_t_out": 85.0,
        "default_daily_volume": 15000,
        "pid_html": PHARMA_PID_HTML,
        "notes": "Requires strict temperature tracking via TT-101/TIC-101 logic gates to guarantee zero unpasteurized bypass fluid into secondary pure loops."
    },
    "Dairy Industry": {
        "default_t_in": 50.0,
        "default_t_out": 75.0,
        "default_daily_volume": 35000,
        "pid_html": DAIRY_PID_HTML,
        "notes": "Maintains precise micro-gap feedback adjustments via PLC automation loops to manage tight bio-layer structural tolerances."
    },
    "Textiles": {
        "default_t_in": 30.0,
        "default_t_out": 90.0,
        "default_daily_volume": 60000,
        "pid_html": TEXTILE_PID_HTML,
        "notes": "Optimized for raw plant sizing margins handling high volume throughput with rapid cycle dump valves."
    },
    "Thermal Power Utilities": {
        "default_t_in": 60.0,
        "default_t_out": 115.0,
        "default_daily_volume": 20000,
        "pid_html": POWER_PID_HTML,
        "notes": "Operates under enhanced high-pressure threshold limits. High safety factor pressure relief valve monitoring is compulsory."
    }
}

# ==============================================================================
# THERMODYNAMIC CORE COMPUTATIONAL SOLVER SUBROUTINES  [LOGIC UNCHANGED]
# ==============================================================================
def estimate_water_properties(t_mean_c):
    t = max(5.0, min(140.0, t_mean_c))
    cp = 4217.4 - 3.7202*t + 0.14125*(t**2) - 0.0020554*(t**3) + 1.1275e-5*(t**4)
    rho = 1000.34 - 0.05434*t - 0.003632*(t**2) + 1.107e-5*(t**3)
    return cp, rho

def solve_collector_thermodynamics(flow_rate_lph, t_in, it, t_amb, ap_area=7.2, config_dict=None):
    if it <= 0.0:
        return {
            "efficiency_pct": 0.0, "energy_input_w": 0.0, "energy_output_w": 0.0,
            "delta_t": -0.5 if it < 10.0 and t_in > t_amb else 0.0,
            "temp_out": t_in + (-0.5 if it < 10.0 and t_in > t_amb else 0.0),
            "cp_j_kgk": 4184.0, "mass_flow_kgs": (flow_rate_lph / 3600.0)
        }

    eta0 = config_dict["intercept_eta0"]
    a1   = config_dict["loss_coeff_a1"]
    a2   = config_dict["loss_coeff_a2"]
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
        efficiency_exec = eta0 - a1*reduced_temperature - a2*(reduced_temperature**2)*it
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
            energy_output_w    = energy_output_exec
            t_out_guess        = t_out_new
            final_cp           = cp_exec
            final_m_dot        = m_dot_exec
            break
        t_out_guess        = t_out_new
        current_efficiency = efficiency_exec
        energy_output_w    = energy_output_exec
        final_cp           = cp_exec
        final_m_dot        = m_dot_exec

    if it < 50.0:
        current_efficiency = 0.0
        energy_output_w    = 0.0
        t_out_guess        = t_in - 0.4

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
# MAIN APPLICATION HEADER
# ==============================================================================
st.markdown("""
<div style="background:linear-gradient(135deg,#1E293B,#0F172A);border:1px solid #334155;
border-radius:16px;padding:28px 32px;margin-bottom:24px;
box-shadow:0 8px 32px rgba(0,0,0,0.5);">
<div style="display:flex;align-items:center;gap:16px;">
  <div style="font-size:3rem;line-height:1;">☀️</div>
  <div>
    <h1 style="margin:0;font-size:1.7rem;color:#F97316 !important;letter-spacing:-0.5px;">
      SQS Advanced Solar Thermal Rig Analytics Simulator
    </h1>
    <p style="margin:6px 0 0;color:#94A3B8 !important;font-size:0.9rem;">
      Multi-variable thermodynamic regressions · 100 / 200 / 300 / 400 LPH empirical datasets
      · ISA-5.1 compliant P&amp;ID generation · Industrial deployment scoping
    </p>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROL INTERFACE
# ==============================================================================
st.sidebar.markdown("""
<div style="text-align:center;padding:12px 0 8px;">
  <span style="font-size:1.8rem;">⚙️</span>
  <div style="font-size:0.85rem;font-weight:700;color:#F97316;letter-spacing:0.5px;margin-top:4px;">
    SIMULATION PARAMETERS
  </div>
</div>
""", unsafe_allow_html=True)

selected_group = st.sidebar.selectbox(
    "Target Nominal Flow Setting",
    options=[100, 200, 300, 400],
    format_func=lambda x: f"Mode Sweep: {x} LPH Config"
)
active_config = EXPERIMENTAL_REGISTRY[selected_group]

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Industrial Application")
selected_app = st.sidebar.selectbox(
    "Target Commercial Sector",
    options=list(APPLICATION_REGISTRY.keys())
)
app_meta = APPLICATION_REGISTRY[selected_app]

st.sidebar.markdown("#### 🌡️ Plant Thermal Targets")
user_target_t_in = st.sidebar.slider(
    "Desired Plant Inlet Temp (°C)",
    min_value=15.0, max_value=110.0,
    value=app_meta["default_t_in"], step=1.0
)
user_target_t_out = st.sidebar.slider(
    "Desired Plant Outlet Temp (°C)",
    min_value=user_target_t_in + 2.0, max_value=140.0,
    value=app_meta["default_t_out"], step=1.0
)
user_daily_volume = st.sidebar.number_input(
    "Daily Process Volume Demand (Liters)",
    min_value=100, max_value=500000,
    value=app_meta["default_daily_volume"], step=500
)
user_latitude = st.sidebar.slider(
    "Deploy Geographical Latitude (°)",
    min_value=-60.0, max_value=60.0, value=28.61, step=0.1,
    help="Determines regional sun elevation and insulation fields."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Primary Rig Controls")
flow_input = st.sidebar.slider(
    "Adjust Actual Rig Flow (kg/hr)",
    min_value=float(math.floor(active_config["min_flow_observed"] - 5)),
    max_value=float(math.ceil(active_config["max_flow_observed"] + 5)),
    value=active_config["mean_flow_rate"], step=0.1,
    help=f"Mean registered across dataset for this setting: {active_config['mean_flow_rate']} kg/hr"
)
t_in_input = st.sidebar.slider(
    "Fluid Inlet Temp: SQS TEMP IN (°C)",
    min_value=20.0, max_value=120.0, value=75.0, step=0.5,
    help="Inlet working fluid temperature recorded at the rig manifold."
)
it_input = st.sidebar.slider(
    "Solar Radiation Intensity: IT (W/m²)",
    min_value=0.0, max_value=1200.0, value=650.0, step=10.0,
    help="Global solar radiation data measured on the collector plane."
)
t_amb_input = st.sidebar.slider(
    "Environment Ambient Air Temp (°C)",
    min_value=15.0, max_value=45.0, value=28.5, step=0.5
)
aperture_area = st.sidebar.number_input(
    "Aperture Area: SQS AP (m²)",
    min_value=1.0, max_value=15.0, value=7.200, step=0.001, format="%.3f",
    help="Locked structural parameter extracted from data column header properties."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background:#1E293B;border:1px solid #334155;border-radius:8px;padding:12px;">
  <div style="font-size:0.75rem;font-weight:700;color:#F97316;margin-bottom:6px;">
    📋 ACTIVE PROFILE: {active_config['nominal_string']}
  </div>
  <div style="font-size:0.72rem;color:#94A3B8;line-height:1.5;">
    {active_config['description']}
  </div>
  <div style="font-size:0.7rem;color:#64748B;margin-top:6px;">
    ΔT Range: {active_config['typical_delta_t']}
  </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# ENGINE PROCESSING EXECUTION  [LOGIC UNCHANGED]
# ==============================================================================
metrics = solve_collector_thermodynamics(
    flow_rate_lph=flow_input, t_in=t_in_input, it=it_input,
    t_amb=t_amb_input, ap_area=aperture_area, config_dict=active_config
)

# ==============================================================================
# MAIN METRICS DISPLAY
# ==============================================================================
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Predicted Thermal Efficiency", f"{metrics['efficiency_pct']:.2f} %",
              delta=f"{(metrics['efficiency_pct'] - 50.0):+.1f}% vs Norm" if it_input > 0 else None)
    st.markdown('</div>', unsafe_allow_html=True)
with col_m2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Temperature Delta (ΔT)", f"{metrics['delta_t']:.2f} °C",
              delta=f"Typical: {active_config['typical_delta_t']}", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)
with col_m3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Calculated Exit Temp", f"{metrics['temp_out']:.2f} °C")
    st.markdown('</div>', unsafe_allow_html=True)
with col_m4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Energy Input", f"{metrics['energy_input_w']:.1f} W",
              delta="Available solar flux")
    st.markdown('</div>', unsafe_allow_html=True)
with col_m5:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("SQS Energy Output", f"{metrics['energy_output_w']:.1f} W",
              delta="Net thermal capture")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ==============================================================================
# DATA EXPANSION TABS
# ==============================================================================
tab_plots, tab_cross_flow, tab_meta, tab_industrial_scaling = st.tabs([
    "📈 Performance Curves & Visualizations",
    "🔀 Multi-Flow Comparative Analysis",
    "🗃️ Experimental Metadata Matrix",
    "🏭 Industrial P&ID & Deployment Scoping"
])

# ---- TAB 1 ----
with tab_plots:
    st.subheader(f"Thermodynamic Response Mapping — {selected_group} LPH Regime")
    col_g1, col_g2 = st.columns(2)

    plt.rcParams.update({'axes.facecolor': '#1E293B', 'figure.facecolor': '#0F172A',
                         'axes.edgecolor': '#475569', 'axes.labelcolor': '#CBD5E1',
                         'xtick.color': '#94A3B8', 'ytick.color': '#94A3B8',
                         'grid.color': '#334155', 'text.color': '#CBD5E1'})

    with col_g1:
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        irradiance_sweep = np.linspace(100, 1100, 100)
        efficiency_sweep = [solve_collector_thermodynamics(flow_input, t_in_input, irr, t_amb_input,
                             aperture_area, active_config)["efficiency_pct"] for irr in irradiance_sweep]
        ax1.plot(irradiance_sweep, efficiency_sweep, color='#F97316', lw=2.5, label='Regressed Efficiency')
        ax1.axvline(x=it_input, color='#60A5FA', linestyle='--', lw=1.5,
                    label=f'Active Setpoint ({it_input} W/m²)')
        ax1.fill_between(irradiance_sweep, efficiency_sweep, alpha=0.15, color='#F97316')
        ax1.set_title("Instantaneous Efficiency vs Solar Irradiance", fontsize=10, fontweight='bold', color='#F1F5F9')
        ax1.set_xlabel("Solar Irradiance (W/m²)", fontsize=9)
        ax1.set_ylabel("Efficiency (%)", fontsize=9)
        ax1.grid(True, linestyle=':', alpha=0.5)
        ax1.legend(fontsize=8, facecolor='#1E293B', edgecolor='#475569')
        st.pyplot(fig1)

    with col_g2:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        flow_sweep_bounds = np.linspace(active_config["min_flow_observed"] - 10,
                                        active_config["max_flow_observed"] + 10, 100)
        delta_t_sweep = [solve_collector_thermodynamics(flw, t_in_input, it_input, t_amb_input,
                          aperture_area, active_config)["delta_t"] for flw in flow_sweep_bounds]
        ax2.plot(flow_sweep_bounds, delta_t_sweep, color='#34D399', lw=2.5, label='Predicted Thermal Gain')
        ax2.axvline(x=flow_input, color='#60A5FA', linestyle='--', lw=1.5,
                    label=f'Current Setting ({flow_input:.1f} kg/hr)')
        ax2.fill_between(flow_sweep_bounds, delta_t_sweep, alpha=0.15, color='#34D399')
        ax2.set_title("Fluid Temperature Rise vs Mass Flow Spectrum", fontsize=10, fontweight='bold', color='#F1F5F9')
        ax2.set_xlabel("Regulated Flow Rate (kg/hr)", fontsize=9)
        ax2.set_ylabel("Delta Temperature (°C)", fontsize=9)
        ax2.grid(True, linestyle=':', alpha=0.5)
        ax2.legend(fontsize=8, facecolor='#1E293B', edgecolor='#475569')
        st.pyplot(fig2)

# ---- TAB 2 ----
with tab_cross_flow:
    st.subheader("Simultaneous Multi-Regime Operational Sweep Matrix")
    comparative_dataset = []
    for flow_key, configuration in EXPERIMENTAL_REGISTRY.items():
        sim_res = solve_collector_thermodynamics(
            flow_rate_lph=configuration["mean_flow_rate"], t_in=t_in_input,
            it=it_input, t_amb=t_amb_input, ap_area=aperture_area, config_dict=configuration
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
    colors_palette = {100: '#E63946', 200: '#F4A261', 300: '#2A9D8F', 400: '#1D9BF0'}
    for flow_key, configuration in EXPERIMENTAL_REGISTRY.items():
        eta = (configuration["intercept_eta0"] - configuration["loss_coeff_a1"]*reduced_temp_axis
               - configuration["loss_coeff_a2"]*(reduced_temp_axis**2)*500)
        eta_bounded = np.clip(eta * 100.0, 0, 100)
        ax3.plot(reduced_temp_axis, eta_bounded, label=f"{flow_key} LPH Efficiency Envelope",
                 color=colors_palette[flow_key], lw=2.2)
    t_mean_current = t_in_input + (metrics["delta_t"] / 2.0)
    current_x_pos = (t_mean_current - t_amb_input) / (it_input if it_input > 0 else 1.0)
    if it_input > 0:
        ax3.plot(current_x_pos, metrics["efficiency_pct"], 'o', color='#F97316',
                 markersize=11, label=f"Active Coordinate ({current_x_pos:.4f}, {metrics['efficiency_pct']:.1f}%)",
                 zorder=5, markeredgecolor='white', markeredgewidth=1.5)
    ax3.set_title("Characteristic System Efficiency Envelopes", fontsize=11, fontweight='bold', color='#F1F5F9')
    ax3.set_xlabel("Reduced Temperature Parameter Vector", fontsize=9)
    ax3.set_ylabel("Collector Efficiency Percentage", fontsize=9)
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle='--', alpha=0.4)
    ax3.legend(fontsize=9, loc='upper right', facecolor='#1E293B', edgecolor='#475569')
    st.pyplot(fig3)

# ---- TAB 3 ----
with tab_meta:
    st.subheader("Experimental Data Repositories & Regression Coefficients")
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

    st.markdown("### 🔍 Experimental Physics Log Analysis")
    if selected_group >= 300:
        st.info(
            f"⚡ **High Turbulent Transfer Detected ({selected_group} LPH Config):** Operating at high fluid "
            f"velocities limits fluid residence times within the copper riser circuits. This minimizes the temperature "
            f"gradient across the insulation, suppressing localized thermal emissions. Instantaneous efficiency curves "
            f"track higher values, but fluid temperature gains are narrower."
        )
    else:
        st.warning(
            f"🌡️ **High Thermal Residence Detected ({selected_group} LPH Config):** Low flow velocity settings allow "
            f"water components to absorb solar heat for longer periods within the header tubes. This drives large "
            f"absolute temperature rises, but increases convective and radiative heat loss from the collector surface."
        )

# ---- TAB 4: INDUSTRIAL P&ID & DEPLOYMENT ----
with tab_industrial_scaling:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1E293B,#0F172A);border:1px solid #334155;
    border-radius:12px;padding:16px 20px;margin-bottom:20px;">
      <div style="font-size:1.1rem;font-weight:700;color:#F97316;">⚙️ Plant Integration Blueprint</div>
      <div style="color:#94A3B8;font-size:0.85rem;margin-top:4px;">
        Application: <b style="color:#F1F5F9;">{selected_app}</b> &nbsp;|&nbsp;
        Flow Regime: <b style="color:#F1F5F9;">{active_config['nominal_string']}</b> &nbsp;|&nbsp;
        Latitude: <b style="color:#F1F5F9;">{user_latitude}°</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Compute sizing [LOGIC UNCHANGED]
    solar_hours = np.array([6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    lat_rad = math.radians(abs(user_latitude))
    peak_flux = max(350.0, 1020.0 * math.cos(lat_rad) - 50.0)
    hourly_irradiance = np.array([
        max(0.0, peak_flux * math.sin(math.pi * (hr - 6) / 12)) for hr in solar_hours
    ])
    mean_target_t = (user_target_t_in + user_target_t_out) / 2.0
    scaled_cp, scaled_rho = estimate_water_properties(mean_target_t)
    total_mass_kg = user_daily_volume * (scaled_rho / 1000.0)
    energy_needed_joules = total_mass_kg * scaled_cp * (user_target_t_out - user_target_t_in)
    energy_needed_kwh = energy_needed_joules / 3600000.0
    midday_test = solve_collector_thermodynamics(
        flow_rate_lph=active_config["mean_flow_rate"], t_in=user_target_t_in,
        it=peak_flux, t_amb=t_amb_input, ap_area=aperture_area, config_dict=active_config
    )
    integrated_efficiency = max(15.0, midday_test["efficiency_pct"]) / 100.0
    total_solar_flux_kwh_m2 = np.sum(hourly_irradiance) / 1000.0
    computed_ideal_area = (energy_needed_kwh / (total_solar_flux_kwh_m2 * integrated_efficiency)
                           if total_solar_flux_kwh_m2 > 0 else 100.0)
    computed_ideal_flow = user_daily_volume / 7.0

    st.subheader("📋 Sized Engineering Allocation Targets")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Required Plant Area", f"{computed_ideal_area:.2f} m²")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_p2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Ideal Flow Rate", f"{computed_ideal_flow:.1f} L/hr")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_p3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Daily Thermal Load", f"{energy_needed_kwh:.2f} kWh")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_p4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Regional Peak Radiation", f"{peak_flux:.1f} W/m²")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- PROFESSIONAL SVG P&ID RENDERING ----
    st.write("---")
    st.subheader("📌 Professional ISA-5.1 Piping & Instrumentation Diagram")
    st.markdown(
        "Schematic varies by selected application sector. Symbols follow ISA 5.1 / IEC 10628 instrumentation standards."
    )
    components.html(app_meta["pid_html"], height=540, scrolling=False)
    st.caption(f"**P&ID Control Directives:** {app_meta['notes']}")

    # ---- PUMP AUTOMATION SCHEDULE ----
    st.write("---")
    st.subheader("⏱️ Smart Pump Automation Schedule Controller")
    st.markdown("Pumps activate when solar yield exceeds the cut-out threshold, preventing reverse radiative siphoning.")

    min_energy_threshold_w = st.slider(
        "Minimum Operational Generation Trigger Cut-out (Watts)",
        min_value=50.0, max_value=600.0, value=180.0, step=10.0,
        help="The pump cuts out if current collection drops below this net power generation floor."
    )

    pump_timelines = []
    pump_on_intervals = 0
    total_harvested_w = 0.0

    for hr, step_it in zip(solar_hours, hourly_irradiance):
        step_calc = solve_collector_thermodynamics(
            flow_rate_lph=active_config["mean_flow_rate"], t_in=user_target_t_in,
            it=step_it, t_amb=t_amb_input, ap_area=aperture_area, config_dict=active_config
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

    # ---- PROPOSAL ----
    st.markdown('<div class="proposal-section">', unsafe_allow_html=True)
    st.subheader("📄 Commercial Plant Deployment Proposal & Feasibility Spec Sheet")
    st.markdown(f"""
### **Project Engineering Specification Document**
* **Target Framework Assignment Type:** Modular Process Heating Upgrade for **{selected_app}** Utilities.
* **Geographic Field Optimization Array Placement:** Sized for operational baseline profile at **{user_latitude}° Latitude**.

### **1. Fluid Kinetic Properties & Design Scaling Constraints**
To satisfy your daily requirement of **{user_daily_volume} Liters** shifting from **{user_target_t_in}°C** to **{user_target_t_out}°C**,
the system demands an array scaled using kinetic parameters from the **{active_config['nominal_string']}** empirical database.
* **Working Fluid Density (ρ):** `{scaled_rho:.2f} kg/m³` &nbsp;|&nbsp; **Specific Heat Capacity (Cp):** `{scaled_cp:.1f} J/kg·K`
* **Recommended Continuous Flow Rate Setpoint:** **`{computed_ideal_flow:.2f} LPH`**
* **Total Aperture Surface Area Requirement:** **`{computed_ideal_area:.2f} m²`** of high-performance flat-plate or vacuum tube elements.

### **2. Automated Pump Lifecycle & Energy Management Profile**
* **Total Effective Pump Running Time:** **`{pump_on_intervals} Hours`** of active automation runtime over a standard diurnal schedule.
* **Rig Performance Cut-out Safety Boundary:** System locks flow loops automatically if solar generation dips below **`{min_energy_threshold_w} W`**.
* **Estimated Cumulative Module Delivery Yield:** **`{(total_harvested_w / 1000.0):.3f} kWh`** per unit module baseline array layout.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
