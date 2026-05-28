"""
thermal_engine.py
Core solar thermal calculation engine using HWB (Hottel-Whillier-Bliss) equations.
Supports ISO 9806 / EN12975 style collector parameters.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class CollectorParams:
    """Universal solar collector parameter set (ISO 9806 / EN12975 compatible)."""
    name: str = "Custom Collector"
    collector_type: str = "Flat Plate"           # Flat Plate | ETC | Thermosiphon | Concentrating
    aperture_area: float = 2.0                   # m²
    gross_area: float = 2.2                      # m²
    width: float = 1.0                           # m
    height: float = 2.0                          # m
    eta0: float = 0.78                           # Optical efficiency intercept
    a1: float = 3.5                              # Linear heat loss coeff W/(m²·K)
    a2: float = 0.015                            # Quadratic heat loss coeff W/(m²·K²)
    iam_bL: float = 0.1                          # IAM coefficient (transverse)
    iam_bT: float = 0.05                         # IAM coefficient (longitudinal)
    max_pressure: float = 8.0                    # bar
    rated_flow_per_collector: float = 50.0       # LPH per collector
    fluid_type: str = "Water"                    # Water | Glycol 30% | Glycol 50%
    tilt_angle: float = 20.0                     # degrees from horizontal
    orientation: float = 0.0                     # degrees from south (0=south, +east, -west)
    thermal_capacitance: float = 5000.0          # J/(m²·K) - collector capacitance


@dataclass
class ProcessRequirements:
    """Industrial process hot water requirements."""
    daily_volume_lpd: float = 5000.0
    inlet_temp_c: float = 25.0
    required_temp_c: float = 80.0
    ambient_temp_c: float = 30.0
    wind_speed_ms: float = 2.0
    industry_type: str = "Dairy Plant"
    operating_days_per_year: int = 300
    operating_hours_per_day: float = 8.0


@dataclass
class SolarResourceData:
    """Site-specific solar resource and geographic data."""
    city: str = "Mumbai"
    latitude: float = 19.1
    longitude: float = 72.9
    altitude_m: float = 14.0
    monthly_irradiance: list = field(default_factory=lambda: [760]*12)  # W/m²
    monthly_ambient: list = field(default_factory=lambda: [28]*12)      # °C
    peak_sun_hours: float = 5.5                                          # hours/day


@dataclass
class ThermalResult:
    """Output of thermal simulation."""
    efficiency_pct: float = 0.0
    delta_t_c: float = 0.0
    temp_out_c: float = 0.0
    useful_heat_w: float = 0.0
    heat_loss_w: float = 0.0
    reduced_temp: float = 0.0
    solar_fraction: float = 0.0


# ─────────────────────────────────────────────
#  FLUID PROPERTIES
# ─────────────────────────────────────────────

FLUID_PROPS = {
    "Water": {"cp": 4186.0, "rho": 998.0, "mu": 0.001002, "k": 0.598},
    "Glycol 30%": {"cp": 3900.0, "rho": 1040.0, "mu": 0.0015, "k": 0.52},
    "Glycol 50%": {"cp": 3650.0, "rho": 1060.0, "mu": 0.0025, "k": 0.44},
}


def get_fluid_props(fluid_type: str) -> dict:
    return FLUID_PROPS.get(fluid_type, FLUID_PROPS["Water"])


# ─────────────────────────────────────────────
#  CORE HWB SOLVER
# ─────────────────────────────────────────────

def solve_collector_thermal(
    collector: CollectorParams,
    t_inlet: float,
    irradiance: float,
    t_ambient: float,
    flow_rate_lph: Optional[float] = None,
    max_iter: int = 20,
    tolerance: float = 0.01
) -> ThermalResult:
    """
    Iterative HWB thermal solver.
    η = η0 - a1·(Tm-Ta)/G - a2·(Tm-Ta)²/G
    Iterates until Tm converges.
    """
    result = ThermalResult()

    if irradiance <= 10:
        result.temp_out_c = t_inlet
        return result

    fp = get_fluid_props(collector.fluid_type)
    cp = fp["cp"]
    flow = flow_rate_lph if flow_rate_lph else collector.rated_flow_per_collector
    mass_flow_s = (flow / 3600.0) * fp["rho"] / 1000.0   # kg/s

    G = irradiance
    T_m = t_inlet + 5.0   # initial guess

    for _ in range(max_iter):
        x = (T_m - t_ambient) / G
        eta = collector.eta0 - collector.a1 * x - collector.a2 * (x ** 2) * G
        eta = float(np.clip(eta, 0.0, collector.eta0))

        Q_useful = eta * G * collector.aperture_area
        Q_loss = (collector.a1 * (T_m - t_ambient) + collector.a2 * (T_m - t_ambient) ** 2) * collector.aperture_area

        if mass_flow_s > 1e-6:
            dT = Q_useful / (mass_flow_s * cp)
        else:
            dT = 0.0

        T_m_new = t_inlet + dT / 2.0
        if abs(T_m_new - T_m) < tolerance:
            T_m = T_m_new
            break
        T_m = T_m_new

    result.efficiency_pct = eta * 100.0
    result.delta_t_c = dT
    result.temp_out_c = t_inlet + dT
    result.useful_heat_w = Q_useful
    result.heat_loss_w = Q_loss
    result.reduced_temp = x
    return result


# ─────────────────────────────────────────────
#  SYSTEM SIZING ENGINE
# ─────────────────────────────────────────────

def calculate_thermal_load(process: ProcessRequirements) -> dict:
    """Calculate daily and hourly thermal load."""
    fp = get_fluid_props("Water")
    dT = process.required_temp_c - process.inlet_temp_c
    daily_energy_kwh = (process.daily_volume_lpd * fp["cp"] * dT) / 3_600_000.0
    hourly_power_kw = daily_energy_kwh / process.operating_hours_per_day
    annual_energy_kwh = daily_energy_kwh * process.operating_days_per_year
    return {
        "dT_c": dT,
        "daily_energy_kwh": daily_energy_kwh,
        "hourly_power_kw": hourly_power_kw,
        "annual_energy_kwh": annual_energy_kwh,
        "daily_volume_lpd": process.daily_volume_lpd,
    }


def size_collector_field(
    collector: CollectorParams,
    process: ProcessRequirements,
    solar: SolarResourceData,
    safety_factor: float = 1.15,
    target_solar_fraction: float = 0.70,
) -> dict:
    """
    Size the solar collector field for a given process load.
    Returns number of collectors, areas, flow rate.
    """
    load = calculate_thermal_load(process)
    avg_irradiance = float(np.mean(solar.monthly_irradiance))
    avg_ambient = float(np.mean(solar.monthly_ambient))
    psh = solar.peak_sun_hours

    # Energy to be covered by solar
    target_energy_kwh = load["daily_energy_kwh"] * target_solar_fraction * safety_factor

    # Estimate single collector daily yield (kWh)
    result_1 = solve_collector_thermal(
        collector, process.inlet_temp_c, avg_irradiance, avg_ambient
    )
    single_daily_kwh = (result_1.useful_heat_w / 1000.0) * psh  # kWh/day

    if single_daily_kwh <= 0:
        single_daily_kwh = 0.1

    n_collectors = max(1, int(np.ceil(target_energy_kwh / single_daily_kwh)))

    total_aperture_m2 = n_collectors * collector.aperture_area
    total_gross_m2 = n_collectors * collector.gross_area
    total_flow_lph = n_collectors * collector.rated_flow_per_collector

    # Recalculate with final field
    field_result = solve_collector_thermal(
        collector,
        process.inlet_temp_c,
        avg_irradiance,
        avg_ambient,
        flow_rate_lph=total_flow_lph
    )
    field_daily_kwh = (field_result.useful_heat_w / 1000.0) * psh * n_collectors
    solar_fraction = min(1.0, field_daily_kwh / load["daily_energy_kwh"]) if load["daily_energy_kwh"] > 0 else 0.0

    return {
        "n_collectors": n_collectors,
        "total_aperture_m2": total_aperture_m2,
        "total_gross_m2": total_gross_m2,
        "total_flow_lph": total_flow_lph,
        "total_flow_lpm": total_flow_lph / 60.0,
        "solar_fraction_pct": solar_fraction * 100.0,
        "field_daily_kwh": field_daily_kwh,
        "avg_collector_efficiency_pct": field_result.efficiency_pct,
        "field_outlet_temp_c": field_result.temp_out_c,
        "single_daily_kwh": single_daily_kwh,
        "thermal_load": load,
        "n_rows": max(1, n_collectors // 5),
        "collectors_per_row": min(5, n_collectors),
    }


# ─────────────────────────────────────────────
#  MONTHLY PERFORMANCE PROFILE
# ─────────────────────────────────────────────

def monthly_performance(
    collector: CollectorParams,
    process: ProcessRequirements,
    solar: SolarResourceData,
    n_collectors: int,
) -> list:
    """Return month-by-month performance dict list."""
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fp = get_fluid_props("Water")
    dT = process.required_temp_c - process.inlet_temp_c
    daily_load_kwh = (process.daily_volume_lpd * fp["cp"] * dT) / 3_600_000.0
    total_flow = n_collectors * collector.rated_flow_per_collector

    results = []
    for i, month in enumerate(months):
        G = solar.monthly_irradiance[i]
        T_amb = solar.monthly_ambient[i]
        r = solve_collector_thermal(collector, process.inlet_temp_c, G, T_amb, total_flow)
        solar_kwh = (r.useful_heat_w / 1000.0) * solar.peak_sun_hours * n_collectors
        sf = min(1.0, solar_kwh / daily_load_kwh) if daily_load_kwh > 0 else 0.0
        aux_kwh = max(0.0, daily_load_kwh - solar_kwh)
        results.append({
            "month": month,
            "irradiance_wm2": G,
            "efficiency_pct": r.efficiency_pct,
            "solar_yield_kwh": solar_kwh,
            "aux_energy_kwh": aux_kwh,
            "solar_fraction_pct": sf * 100.0,
            "outlet_temp_c": r.temp_out_c,
        })
    return results


# ─────────────────────────────────────────────
#  EFFICIENCY CURVE DATA
# ─────────────────────────────────────────────

def generate_efficiency_curve(collector: CollectorParams, irradiance: float = 800.0) -> dict:
    """Generate η vs (Tm-Ta)/G reduced temperature curve data."""
    x_vals = np.linspace(0.0, 0.30, 200)
    eta_vals = collector.eta0 - collector.a1 * x_vals - collector.a2 * x_vals ** 2 * irradiance
    eta_vals = np.clip(eta_vals, 0, collector.eta0) * 100.0
    return {"x": x_vals.tolist(), "eta": eta_vals.tolist()} 
"""
hydraulic_engine.py
Pipe sizing, pump selection, pressure drop, and hydraulic calculations
using Darcy-Weisbach equations with Colebrook friction factors.
"""

import numpy as np
import math


# ─────────────────────────────────────────────
#  PIPE SCHEDULE DATABASE
# ─────────────────────────────────────────────

PIPE_SCHEDULE = [
    {"dn": "DN15",  "id_mm": 15.8,  "od_mm": 21.3},
    {"dn": "DN20",  "id_mm": 20.9,  "od_mm": 26.9},
    {"dn": "DN25",  "id_mm": 26.6,  "od_mm": 33.7},
    {"dn": "DN32",  "id_mm": 35.1,  "od_mm": 42.4},
    {"dn": "DN40",  "id_mm": 40.9,  "od_mm": 48.3},
    {"dn": "DN50",  "id_mm": 52.5,  "od_mm": 60.3},
    {"dn": "DN65",  "id_mm": 68.8,  "od_mm": 76.1},
    {"dn": "DN80",  "id_mm": 80.9,  "od_mm": 88.9},
    {"dn": "DN100", "id_mm": 102.3, "od_mm": 114.3},
    {"dn": "DN125", "id_mm": 128.2, "od_mm": 139.7},
    {"dn": "DN150", "id_mm": 154.1, "od_mm": 168.3},
]

# ─────────────────────────────────────────────
#  PUMP SELECTION DATABASE
# ─────────────────────────────────────────────

PUMP_CATALOGUE = [
    {"model": "0.5 HP Centrifugal",  "power_hp": 0.5,  "max_flow_lpm": 30,   "max_head_m": 12},
    {"model": "1 HP Centrifugal",    "power_hp": 1.0,  "max_flow_lpm": 60,   "max_head_m": 18},
    {"model": "1.5 HP Centrifugal",  "power_hp": 1.5,  "max_flow_lpm": 90,   "max_head_m": 22},
    {"model": "2 HP Centrifugal",    "power_hp": 2.0,  "max_flow_lpm": 130,  "max_head_m": 28},
    {"model": "3 HP Centrifugal",    "power_hp": 3.0,  "max_flow_lpm": 200,  "max_head_m": 35},
    {"model": "5 HP Centrifugal",    "power_hp": 5.0,  "max_flow_lpm": 350,  "max_head_m": 42},
    {"model": "7.5 HP Centrifugal",  "power_hp": 7.5,  "max_flow_lpm": 500,  "max_head_m": 52},
    {"model": "10 HP Centrifugal",   "power_hp": 10.0, "max_flow_lpm": 700,  "max_head_m": 60},
    {"model": "15 HP Centrifugal",   "power_hp": 15.0, "max_flow_lpm": 1000, "max_head_m": 70},
    {"model": "20 HP Centrifugal",   "power_hp": 20.0, "max_flow_lpm": 1400, "max_head_m": 80},
]


# ─────────────────────────────────────────────
#  CORE HYDRAULIC FUNCTIONS
# ─────────────────────────────────────────────

def reynolds_number(velocity_ms: float, diameter_m: float, kinematic_viscosity: float = 1.0e-6) -> float:
    """Calculate Reynolds number Re = v·D / ν"""
    if diameter_m <= 0 or kinematic_viscosity <= 0:
        return 0.0
    return (velocity_ms * diameter_m) / kinematic_viscosity


def colebrook_friction_factor(Re: float, roughness_m: float = 4.5e-5, diameter_m: float = 0.05) -> float:
    """
    Colebrook-White equation solved via Swamee-Jain approximation.
    Valid for Re > 3000 and ε/D between 1e-6 and 0.05
    """
    if Re < 2300:
        return 64.0 / max(Re, 1e-6)   # Laminar
    eps_D = roughness_m / diameter_m
    # Swamee-Jain: f = 0.25 / [log10(ε/3.7D + 5.74/Re^0.9)]²
    denominator = math.log10(eps_D / 3.7 + 5.74 / (Re ** 0.9))
    f = 0.25 / (denominator ** 2)
    return max(f, 0.008)


def velocity_in_pipe(flow_lpm: float, inner_diameter_mm: float) -> float:
    """Calculate fluid velocity in m/s."""
    q_m3s = flow_lpm / 60_000.0
    area = math.pi * (inner_diameter_mm / 2000.0) ** 2
    return q_m3s / area if area > 0 else 0.0


def darcy_pressure_drop(
    flow_lpm: float,
    inner_diameter_mm: float,
    pipe_length_m: float,
    fluid_density: float = 998.0,
    kinematic_viscosity: float = 1.0e-6,
    roughness_m: float = 4.5e-5
) -> dict:
    """
    Darcy-Weisbach pressure drop:
    ΔP = f · (L/D) · (ρv²/2)
    Returns pressure drop in Pa, kPa, and head in meters.
    """
    D = inner_diameter_mm / 1000.0
    v = velocity_in_pipe(flow_lpm, inner_diameter_mm)
    Re = reynolds_number(v, D, kinematic_viscosity)
    f = colebrook_friction_factor(Re, roughness_m, D)

    dP = f * (pipe_length_m / D) * (fluid_density * v ** 2 / 2.0)
    head_m = dP / (fluid_density * 9.81)

    return {
        "velocity_ms": round(v, 3),
        "reynolds_number": round(Re, 0),
        "friction_factor": round(f, 5),
        "pressure_drop_pa": round(dP, 1),
        "pressure_drop_kpa": round(dP / 1000, 3),
        "head_m": round(head_m, 3),
        "flow_regime": "Laminar" if Re < 2300 else ("Transitional" if Re < 4000 else "Turbulent"),
    }


# ─────────────────────────────────────────────
#  PIPE SELECTION
# ─────────────────────────────────────────────

def select_pipe(flow_lpm: float, max_velocity_ms: float = 1.5) -> dict:
    """Select smallest pipe where velocity ≤ max_velocity_ms."""
    for pipe in PIPE_SCHEDULE:
        v = velocity_in_pipe(flow_lpm, pipe["id_mm"])
        if v <= max_velocity_ms:
            return {**pipe, "velocity_ms": round(v, 3)}
    # Return largest if all exceed limit
    largest = PIPE_SCHEDULE[-1]
    return {**largest, "velocity_ms": round(velocity_in_pipe(flow_lpm, largest["id_mm"]), 3)}


# ─────────────────────────────────────────────
#  PUMP SELECTION
# ─────────────────────────────────────────────

def select_pump(flow_lpm: float, required_head_m: float = 20.0) -> dict:
    """Select smallest pump meeting flow and head requirements."""
    margin_flow = flow_lpm * 1.15
    margin_head = required_head_m * 1.20
    for pump in PUMP_CATALOGUE:
        if pump["max_flow_lpm"] >= margin_flow and pump["max_head_m"] >= margin_head:
            return {**pump, "design_flow_lpm": round(flow_lpm, 1), "design_head_m": round(required_head_m, 1)}
    return {**PUMP_CATALOGUE[-1], "design_flow_lpm": round(flow_lpm, 1), "design_head_m": round(required_head_m, 1)}


# ─────────────────────────────────────────────
#  STORAGE & EXPANSION TANK
# ─────────────────────────────────────────────

def size_storage_tank(daily_volume_lpd: float, storage_factor: float = 1.2) -> dict:
    """Size the thermal buffer / storage tank."""
    capacity = daily_volume_lpd * storage_factor
    # Standard tank sizes
    standards = [500, 1000, 1500, 2000, 3000, 5000, 8000, 10000, 15000, 20000, 25000, 50000]
    selected = next((s for s in standards if s >= capacity), capacity)
    return {
        "recommended_capacity_l": round(capacity, 0),
        "standard_size_l": selected,
        "n_tanks": 1 if selected <= 10000 else math.ceil(capacity / 10000),
    }


def size_expansion_tank(
    system_volume_l: float,
    max_temp_c: float = 90.0,
    fill_temp_c: float = 20.0,
    max_pressure_bar: float = 6.0,
    fill_pressure_bar: float = 1.5,
) -> dict:
    """
    Expansion tank sizing using Wilo/Reflex formula.
    Ve = Vs · (n - 0.0) / (1 - Pf/Pe)
    """
    # Fluid expansion factor (water): approx 0.04 per 60°C rise
    expansion_coeff = 0.00021 * (max_temp_c - fill_temp_c)
    Vs = system_volume_l
    Vexp = Vs * expansion_coeff
    # Tank size: Vt = Vexp / (1 - Pfill_abs / Pmax_abs)
    Pf_abs = fill_pressure_bar + 1.013
    Pe_abs = max_pressure_bar + 1.013
    Vt = Vexp / (1 - Pf_abs / Pe_abs) if Pe_abs > Pf_abs else Vexp * 2.5
    return {
        "expansion_volume_l": round(Vexp, 1),
        "expansion_tank_l": round(Vt * 1.25, 1),   # 25% safety margin
        "recommended_size_l": round(Vt * 1.5, 0),
    }


# ─────────────────────────────────────────────
#  HEAT EXCHANGER SIZING
# ─────────────────────────────────────────────

def size_heat_exchanger(
    thermal_load_kw: float,
    lmtd_c: float = 10.0,
    u_value: float = 3500.0    # W/(m²·K) for plate HX
) -> dict:
    """Size plate heat exchanger by LMTD method."""
    Q_w = thermal_load_kw * 1000.0
    area_m2 = Q_w / (u_value * lmtd_c)
    # Round to standard plate HX area increments of 0.5 m²
    std_area = math.ceil(area_m2 / 0.5) * 0.5
    return {
        "required_area_m2": round(area_m2, 3),
        "selected_area_m2": std_area,
        "u_value_wm2k": u_value,
        "lmtd_c": lmtd_c,
        "type": "Gasketed Plate Heat Exchanger",
    }


# ─────────────────────────────────────────────
#  FULL HYDRAULIC PACKAGE
# ─────────────────────────────────────────────

def full_hydraulic_sizing(
    flow_lpm: float,
    pipe_length_m: float = 50.0,
    daily_volume_lpd: float = 5000.0,
    thermal_load_kw: float = 50.0,
    system_volume_l: float = 500.0,
    max_system_temp: float = 90.0,
) -> dict:
    pipe = select_pipe(flow_lpm)
    dp = darcy_pressure_drop(flow_lpm, pipe["id_mm"], pipe_length_m)
    total_head = dp["head_m"] + 5.0   # Add static head & fittings allowance
    pump = select_pump(flow_lpm, total_head)
    tank = size_storage_tank(daily_volume_lpd)
    exp = size_expansion_tank(system_volume_l, max_system_temp)
    hx = size_heat_exchanger(thermal_load_kw)

    return {
        "pipe": pipe,
        "pressure_drop": dp,
        "pump": pump,
        "storage_tank": tank,
        "expansion_tank": exp,
        "heat_exchanger": hx,
        "total_head_m": round(total_head, 2),
    } 
"""
layout_engine.py
Solar field layout calculations: row spacing using winter solstice shadow geometry,
land area, maintenance corridors, and collector matrix.
"""

import numpy as np
import math


def solar_declination_winter_solstice() -> float:
    """Winter solstice solar declination = -23.45°"""
    return -23.45


def solar_altitude_at_noon(latitude_deg: float, declination_deg: float = -23.45) -> float:
    """
    Solar altitude angle at solar noon (degrees above horizon).
    α = 90 - |φ - δ|
    """
    lat_rad = math.radians(latitude_deg)
    dec_rad = math.radians(declination_deg)
    sin_alt = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad)
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))


def shadow_length(collector_height_m: float, tilt_deg: float, altitude_deg: float) -> float:
    """
    Horizontal shadow length of a tilted collector.
    L_shadow = H_col · cos(tilt) + H_col · sin(tilt) / tan(altitude)
    where H_col is the height of the top edge above ground.
    """
    if altitude_deg <= 2.0:
        altitude_deg = 2.0
    h_top = collector_height_m * math.sin(math.radians(tilt_deg))  # top edge height
    l_h = collector_height_m * math.cos(math.radians(tilt_deg))    # horizontal projection
    shadow = l_h + h_top / math.tan(math.radians(altitude_deg))
    return shadow


def optimum_tilt(latitude_deg: float) -> float:
    """
    Recommended collector tilt angle = latitude + 10° for winter optimization
    Clamped between 10° and 55°.
    """
    return float(np.clip(abs(latitude_deg) + 10.0, 10.0, 55.0))


def calculate_row_spacing(
    collector_height_m: float,
    collector_width_m: float,
    tilt_deg: float,
    latitude_deg: float,
    maintenance_gap_m: float = 0.8,
) -> dict:
    """
    Full row spacing calculation based on winter solstice shadow avoidance.
    Returns pitch (row-to-row), maintenance access, etc.
    """
    decl = solar_declination_winter_solstice()
    alt = solar_altitude_at_noon(latitude_deg, decl)
    shadow = shadow_length(collector_height_m, tilt_deg, alt)
    pitch = shadow + maintenance_gap_m
    ground_clearance = collector_height_m * math.sin(math.radians(tilt_deg))

    return {
        "winter_solstice_altitude_deg": round(alt, 2),
        "shadow_length_m": round(shadow, 3),
        "row_pitch_m": round(pitch, 3),
        "ground_clearance_m": round(ground_clearance, 3),
        "tilt_deg": round(tilt_deg, 1),
        "maintenance_corridor_m": maintenance_gap_m,
        "horizontal_projection_m": round(collector_height_m * math.cos(math.radians(tilt_deg)), 3),
    }


def calculate_field_layout(
    n_collectors: int,
    collector_width_m: float,
    collector_height_m: float,
    tilt_deg: float,
    latitude_deg: float,
    collectors_per_row: int = 5,
    side_margin_m: float = 1.5,
    end_margin_m: float = 3.0,
    maintenance_gap_m: float = 0.8,
) -> dict:
    """
    Full field layout: rows, columns, spacing, total land area.
    """
    spacing = calculate_row_spacing(collector_height_m, collector_width_m, tilt_deg, latitude_deg, maintenance_gap_m)
    n_rows = math.ceil(n_collectors / collectors_per_row)
    actual_per_row = math.ceil(n_collectors / n_rows)

    # Field dimensions
    field_width_m = actual_per_row * collector_width_m + (actual_per_row - 1) * 0.1 + 2 * side_margin_m
    row_depth_m = spacing["horizontal_projection_m"]
    total_depth_m = n_rows * spacing["row_pitch_m"] + row_depth_m + 2 * end_margin_m

    land_area_m2 = field_width_m * total_depth_m
    packing_ratio = (n_collectors * collector_width_m * collector_height_m) / land_area_m2

    return {
        "n_collectors": n_collectors,
        "n_rows": n_rows,
        "collectors_per_row": actual_per_row,
        "field_width_m": round(field_width_m, 2),
        "field_depth_m": round(total_depth_m, 2),
        "land_area_m2": round(land_area_m2, 1),
        "land_area_sqft": round(land_area_m2 * 10.764, 0),
        "row_pitch_m": spacing["row_pitch_m"],
        "ground_clearance_m": spacing["ground_clearance_m"],
        "winter_altitude_deg": spacing["winter_solstice_altitude_deg"],
        "shadow_length_m": spacing["shadow_length_m"],
        "packing_ratio": round(packing_ratio, 3),
        "tilt_deg": tilt_deg,
        "side_margin_m": side_margin_m,
        "end_margin_m": end_margin_m,
    }


def generate_layout_svg(layout: dict) -> str:
    """
    Generate an ASCII/SVG-like schematic string for the field layout.
    Returns a text-based layout representation for display.
    """
    n_rows = layout["n_rows"]
    per_row = layout["collectors_per_row"]
    rows = []
    collector_id = 1
    for r in range(n_rows):
        row_str = f"  Row {r+1:>2}:  "
        for c in range(per_row):
            if collector_id <= layout["n_collectors"]:
                row_str += f"[C{collector_id:02d}] "
                collector_id += 1
        rows.append(row_str)
    rows.append(f"\n  Field: {layout['field_width_m']} m (W) × {layout['field_depth_m']} m (D)")
    rows.append(f"  Land Area: {layout['land_area_m2']} m²  |  Row Pitch: {layout['row_pitch_m']} m")
    rows.append(f"  Tilt: {layout['tilt_deg']}°  |  Winter Solar Altitude: {layout['winter_altitude_deg']}°")
    return "\n".join(rows)
"""
financial_engine.py
Financial analysis: capex, opex, payback, IRR, NPV, CO2 reduction, ROI.
"""

import numpy as np


# ─────────────────────────────────────────────
#  FUEL CALORIFIC VALUES AND EMISSIONS
# ─────────────────────────────────────────────

FUEL_DATABASE = {
    "Diesel": {
        "calorific_value_mj_l": 34.4,
        "efficiency": 0.80,
        "co2_kg_per_l": 2.68,
        "unit": "Litre",
        "energy_per_unit_kwh": 9.55,   # kWh/litre
        "default_cost_inr": 95.0,
    },
    "Natural Gas": {
        "calorific_value_mj_l": 38.5,
        "efficiency": 0.85,
        "co2_kg_per_scm": 1.96,
        "unit": "SCM",
        "energy_per_unit_kwh": 9.72,   # kWh/SCM
        "default_cost_inr": 55.0,
    },
    "LPG": {
        "calorific_value_mj_l": 46.0,
        "efficiency": 0.80,
        "co2_kg_per_kg": 2.98,
        "unit": "kg",
        "energy_per_unit_kwh": 12.78,  # kWh/kg
        "default_cost_inr": 90.0,
    },
    "Furnace Oil": {
        "calorific_value_mj_l": 38.6,
        "efficiency": 0.78,
        "co2_kg_per_l": 3.15,
        "unit": "Litre",
        "energy_per_unit_kwh": 10.16,
        "default_cost_inr": 75.0,
    },
    "Electric Heater": {
        "calorific_value_mj_l": 3.6,
        "efficiency": 0.98,
        "co2_kg_per_kwh": 0.82,
        "unit": "kWh",
        "energy_per_unit_kwh": 1.0,
        "default_cost_inr": 8.0,
    },
    "Coal": {
        "calorific_value_mj_l": 24.0,
        "efficiency": 0.72,
        "co2_kg_per_kg": 2.42,
        "unit": "kg",
        "energy_per_unit_kwh": 4.8,
        "default_cost_inr": 12.0,
    },
}


# ─────────────────────────────────────────────
#  CAPEX ESTIMATOR
# ─────────────────────────────────────────────

COST_RATES = {
    "Flat Plate": 12_000,         # ₹/m² aperture area
    "ETC": 14_500,
    "Thermosiphon": 11_000,
    "Concentrating": 18_000,
}

def estimate_capex(
    collector_type: str,
    total_aperture_m2: float,
    include_installation: bool = True,
    include_civil: bool = True,
    contingency_pct: float = 10.0,
) -> dict:
    base_rate = COST_RATES.get(collector_type, 13_000)
    equipment_cost = total_aperture_m2 * base_rate
    installation_cost = equipment_cost * 0.18 if include_installation else 0
    civil_cost = equipment_cost * 0.08 if include_civil else 0
    subtotal = equipment_cost + installation_cost + civil_cost
    contingency = subtotal * contingency_pct / 100.0
    total = subtotal + contingency

    return {
        "equipment_cost_inr": round(equipment_cost, 0),
        "installation_cost_inr": round(installation_cost, 0),
        "civil_cost_inr": round(civil_cost, 0),
        "contingency_inr": round(contingency, 0),
        "total_capex_inr": round(total, 0),
        "cost_per_m2_inr": round(total / total_aperture_m2, 0) if total_aperture_m2 > 0 else 0,
    }


# ─────────────────────────────────────────────
#  ANNUAL SAVINGS
# ─────────────────────────────────────────────

def calculate_annual_savings(
    annual_solar_energy_kwh: float,
    fuel_type: str,
    fuel_cost_inr_per_unit: float,
) -> dict:
    fuel = FUEL_DATABASE.get(fuel_type, FUEL_DATABASE["Diesel"])
    boiler_eff = fuel.get("efficiency", 0.80)
    energy_per_unit = fuel.get("energy_per_unit_kwh", 10.0)

    # Fuel units displaced per year
    fuel_units_saved = annual_solar_energy_kwh / (energy_per_unit * boiler_eff)
    annual_savings_inr = fuel_units_saved * fuel_cost_inr_per_unit

    # CO2 reduction
    co2_factor_key = [k for k in fuel.keys() if k.startswith("co2_kg_per_")]
    if co2_factor_key:
        co2_per_unit = fuel[co2_factor_key[0]]
        co2_tonnes = (fuel_units_saved * co2_per_unit) / 1000.0
    else:
        co2_tonnes = annual_solar_energy_kwh * 0.82 / 1000.0

    return {
        "annual_solar_energy_kwh": round(annual_solar_energy_kwh, 1),
        "fuel_units_saved": round(fuel_units_saved, 1),
        "fuel_unit_label": fuel["unit"],
        "annual_savings_inr": round(annual_savings_inr, 0),
        "co2_reduction_tonnes": round(co2_tonnes, 2),
        "co2_equivalent_trees": round(co2_tonnes * 45, 0),  # ~45 trees per tonne CO2/yr
        "fuel_type": fuel_type,
    }


# ─────────────────────────────────────────────
#  PAYBACK & ROI
# ─────────────────────────────────────────────

def calculate_payback(capex_inr: float, annual_savings_inr: float, fuel_escalation_pct: float = 5.0) -> dict:
    """Simple payback and discounted payback calculation."""
    if annual_savings_inr <= 0:
        return {"simple_payback_years": 99, "discounted_payback_years": 99, "roi_pct": 0}

    simple_payback = capex_inr / annual_savings_inr

    # Discounted payback at fuel escalation rate
    balance = capex_inr
    disc_pb = simple_payback
    savings = annual_savings_inr
    for year in range(1, 26):
        balance -= savings
        if balance <= 0:
            disc_pb = year
            break
        savings *= (1 + fuel_escalation_pct / 100.0)

    roi_10yr = ((annual_savings_inr * 10 - capex_inr) / capex_inr) * 100.0

    return {
        "simple_payback_years": round(simple_payback, 2),
        "discounted_payback_years": disc_pb,
        "roi_10yr_pct": round(roi_10yr, 1),
    }


def cashflow_projection(
    capex_inr: float,
    annual_savings_inr: float,
    project_life_years: int = 20,
    fuel_escalation_pct: float = 5.0,
    discount_rate_pct: float = 10.0,
    subsidy_pct: float = 30.0,
) -> dict:
    """Year-by-year cashflow, cumulative savings, NPV."""
    dr = discount_rate_pct / 100.0
    fe = fuel_escalation_pct / 100.0
    effective_capex = capex_inr * (1 - subsidy_pct / 100.0)

    years = list(range(1, project_life_years + 1))
    annual = []
    cumulative = []
    npv_vals = []
    savings = annual_savings_inr
    cum = -effective_capex
    npv = -effective_capex

    for yr in years:
        cum += savings
        disc_savings = savings / ((1 + dr) ** yr)
        npv += disc_savings
        annual.append(round(savings, 0))
        cumulative.append(round(cum, 0))
        npv_vals.append(round(npv, 0))
        savings *= (1 + fe)

    return {
        "years": years,
        "annual_savings": annual,
        "cumulative_savings": cumulative,
        "npv_series": npv_vals,
        "final_npv_inr": npv_vals[-1] if npv_vals else 0,
        "effective_capex_inr": round(effective_capex, 0),
        "subsidy_inr": round(capex_inr * subsidy_pct / 100.0, 0),
    }
"""
integration_engine.py
Industrial solar thermal system integration module.
Generates integration recommendations, hydraulic logic, control strategy,
and integration topology based on existing plant infrastructure.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExistingPlantInfo:
    """Existing plant infrastructure data."""
    has_boiler: bool = True
    boiler_type: str = "Fire Tube"             # Fire Tube | Water Tube | Steam | Hot Water
    boiler_capacity_kw: float = 500.0
    boiler_fuel: str = "Diesel"
    boiler_inlet_temp_c: float = 25.0
    boiler_outlet_temp_c: float = 90.0
    boiler_efficiency_pct: float = 80.0

    has_existing_tank: bool = True
    existing_tank_l: float = 5000.0
    existing_tank_material: str = "SS 304"

    process_loop_type: str = "Direct"          # Direct | Indirect
    process_pressure_bar: float = 4.0
    process_medium: str = "Hot Water"          # Hot Water | Steam | Thermal Oil

    has_existing_pump: bool = True
    existing_pump_hp: float = 2.0

    existing_pipe_material: str = "GI"         # GI | SS | CPVC | MS
    existing_pipe_insulated: bool = True

    utility_voltage: str = "415V 3Ph"
    has_backup_power: bool = False

    roof_type: str = "RCC Flat"                # RCC Flat | Metal Sheet | Sloped | Ground Mount
    available_roof_area_m2: float = 500.0


@dataclass
class IntegrationRecommendation:
    """Output integration strategy."""
    topology: str = ""
    preheating_strategy: str = ""
    hx_required: bool = True
    buffer_tank_logic: str = ""
    control_strategy: str = ""
    valve_recommendations: list = field(default_factory=list)
    dtc_settings: dict = field(default_factory=dict)
    safety_notes: list = field(default_factory=list)
    integration_steps: list = field(default_factory=list)
    electrical_requirements: str = ""
    om_recommendations: list = field(default_factory=list)


def generate_integration_strategy(
    plant: ExistingPlantInfo,
    solar_field_outlet_temp: float,
    process_required_temp: float,
    solar_fraction_pct: float,
) -> IntegrationRecommendation:
    """
    Generates complete integration strategy based on existing plant inputs
    and solar system outputs.
    """
    rec = IntegrationRecommendation()

    # ── TOPOLOGY SELECTION ─────────────────────────────────────────
    if plant.process_loop_type == "Indirect" or plant.process_pressure_bar > 6.0:
        rec.topology = "Indirect Circuit via Plate Heat Exchanger (Primary Solar Loop + Secondary Process Loop)"
        rec.hx_required = True
    elif solar_field_outlet_temp > process_required_temp + 5:
        rec.topology = "Direct Preheat Loop — Solar field feeds directly into buffer tank before boiler"
        rec.hx_required = False
    else:
        rec.topology = "Hybrid Indirect Loop — Solar field charges buffer tank via HX; boiler tops up to setpoint"
        rec.hx_required = True

    # ── PREHEATING STRATEGY ────────────────────────────────────────
    temp_gap = process_required_temp - solar_field_outlet_temp
    if temp_gap <= 0:
        rec.preheating_strategy = (
            f"FULL SOLAR COVERAGE: Solar field outlet ({solar_field_outlet_temp:.1f}°C) meets or exceeds "
            f"process setpoint ({process_required_temp:.1f}°C). Boiler operates only as emergency backup."
        )
    elif temp_gap < 15:
        rec.preheating_strategy = (
            f"HIGH SOLAR FRACTION: Solar preheats feed to ~{solar_field_outlet_temp:.1f}°C. "
            f"Boiler requires only a {temp_gap:.1f}°C top-up, reducing fuel consumption by >{solar_fraction_pct:.0f}%."
        )
    else:
        rec.preheating_strategy = (
            f"SOLAR PREHEAT MODE: Solar raises inlet temperature from {plant.boiler_inlet_temp_c:.0f}°C to "
            f"~{solar_field_outlet_temp:.1f}°C. Boiler supplements the remaining {temp_gap:.1f}°C rise."
        )

    # ── BUFFER TANK LOGIC ──────────────────────────────────────────
    if plant.has_existing_tank and plant.existing_tank_l > 0:
        rec.buffer_tank_logic = (
            f"Existing {plant.existing_tank_l:.0f} L {plant.existing_tank_material} tank to be repurposed as solar buffer. "
            f"Recommend adding internal coil or external HX to separate solar glycol loop from process water. "
            f"Install 3-zone thermocouples (top/mid/bottom) for stratification monitoring."
        )
    else:
        rec.buffer_tank_logic = (
            "No existing tank detected. Install new insulated SS 304 buffer tank sized per daily demand × 1.2 factor. "
            "Stratified tank design recommended with top draw-off and bottom solar charge."
        )

    # ── CONTROL STRATEGY ──────────────────────────────────────────
    rec.control_strategy = (
        "Differential Temperature Controller (DTC) based on Resol or Steca platform:\n"
        "  • Sensor T1: Solar collector outlet (Pt1000)\n"
        "  • Sensor T2: Buffer tank bottom (Pt1000)\n"
        "  • ON logic: T1 - T2 > ΔT_on (recommended 8°C)\n"
        "  • OFF logic: T1 - T2 < ΔT_off (recommended 3°C)\n"
        "  • High-temp protection: Shut pump if T_collector > 95°C\n"
        "  • Frost protection: Run pump if T_collector < 5°C\n"
        "  • Boiler enable: T_tank_top < (setpoint - 5°C)"
    )

    rec.dtc_settings = {
        "dt_on_c": 8,
        "dt_off_c": 3,
        "max_collector_temp_c": 95,
        "frost_protection_c": 5,
        "boiler_enable_temp_c": process_required_temp - 5,
        "controller_type": "Resol DeltaSol BS Plus or equivalent",
    }

    # ── VALVE RECOMMENDATIONS ──────────────────────────────────────
    rec.valve_recommendations = [
        "CV-101: 2-way modulating valve on solar primary loop (Belimo or Siemens)",
        "CV-102: 3-way diverting valve — solar to buffer / bypass",
        "CV-103: Boiler isolation valve (interlocked with DTC)",
        "PRV-101: Pressure relief valve on solar primary loop (set at max collector pressure - 0.5 bar)",
        "ARV-101: Auto air vent at highest point of solar circuit",
        "NRV-101: Non-return valve on pump discharge to prevent thermosiphon reverse flow",
        "BV-101..104: Isolation ball valves on all major equipment connections (service isolation)",
    ]

    # ── INTEGRATION STEPS ─────────────────────────────────────────
    rec.integration_steps = [
        "Step 1: Install solar collector array on roof per layout drawing. Secure to mounting structure with anti-corrosion hardware.",
        "Step 2: Run solar primary loop piping (insulated 50mm mineral wool) from roof to plant room.",
        "Step 3: Install primary circulation pump (P-101A) with bypass and service isolation valves.",
        f"Step 4: {'Install plate HX between solar loop and process loop' if rec.hx_required else 'Connect solar loop directly to buffer tank charging coil'}.",
        "Step 5: Install / modify buffer storage tank with thermocouples at 3 levels.",
        "Step 6: Connect buffer tank discharge to existing boiler cold water inlet via bypass manifold.",
        "Step 7: Install DTC controller panel with sensors at collector outlet and tank bottom.",
        "Step 8: Wire pump starter to DTC output relay. Set DTC parameters per control strategy.",
        "Step 9: Fill and pressurize solar primary loop. Flush, deaerate, and check for leaks.",
        "Step 10: Commission DTC, verify differential logic, perform thermal performance test at steady irradiance.",
    ]

    # ── SAFETY NOTES ──────────────────────────────────────────────
    rec.safety_notes = [
        "⚠️ Install overheat drain-back or stagnation management if collectors face risk of unshaded peak summer radiation above 1000 W/m².",
        "⚠️ Use glycol antifreeze in primary loop if site ambient drops below 5°C. Typical 30–40% propylene glycol solution.",
        "⚠️ All roof penetrations must be waterproofed and sealed. Use proprietary roof-penetration boots.",
        "⚠️ Electrical connections must comply with IS 732 / IE Rules. All outdoor wiring in UV-resistant conduit.",
        "⚠️ Pressure test entire solar loop at 1.5× operating pressure before commissioning.",
        "⚠️ Install vacuum breaker at highest point if system is not fully sealed pressurized design.",
    ]

    # ── ELECTRICAL REQUIREMENTS ────────────────────────────────────
    rec.electrical_requirements = (
        f"Power supply: {plant.utility_voltage}\n"
        "DTC Controller: 230V AC, 5A dedicated MCB\n"
        "Solar Loop Pump: As per selected pump motor rating, DOL or VFD starter\n"
        "Cable routing: Sensor cables (shielded, 2-core 0.5mm²) in separate conduit from power cables\n"
        f"{'Backup power for DTC recommended — add UPS 500VA' if not plant.has_backup_power else 'Existing backup power available — extend to DTC panel'}"
    )

    # ── O&M RECOMMENDATIONS ────────────────────────────────────────
    rec.om_recommendations = [
        "Monthly: Check glycol concentration and pH (target pH 7–8.5). Top up if concentration drops.",
        "Monthly: Inspect collector glazing for soiling. Clean with soft cloth and mild detergent (no abrasives).",
        "Quarterly: Check all valve positions, pump operation, and DTC log files.",
        "Quarterly: Inspect pipe insulation integrity. Replace if damaged or showing UV degradation.",
        "Annually: Full system pressure test. Drain, flush, and refill solar primary loop.",
        "Annually: Inspect collector frame and mounting for corrosion. Touch up with anti-rust paint.",
        "Annually: Verify DTC calibration with calibrated PT1000 reference thermometer.",
        "5-yearly: Replace pump mechanical seal and bearings as preventive maintenance.",
    ]

    return rec


def format_integration_report(rec: IntegrationRecommendation, plant: ExistingPlantInfo) -> str:
    """Format integration recommendation as a readable text report."""
    lines = [
        "=" * 70,
        "   SYSTEM INTEGRATION ENGINEERING REPORT",
        "=" * 70,
        "",
        f"INTEGRATION TOPOLOGY:  {rec.topology}",
        f"HEAT EXCHANGER REQUIRED: {'Yes' if rec.hx_required else 'No'}",
        "",
        "PREHEATING STRATEGY:",
        f"  {rec.preheating_strategy}",
        "",
        "BUFFER TANK LOGIC:",
        f"  {rec.buffer_tank_logic}",
        "",
        "CONTROL & INSTRUMENTATION:",
        rec.control_strategy,
        "",
        "VALVE SCHEDULE:",
    ]
    for v in rec.valve_recommendations:
        lines.append(f"  • {v}")
    lines += ["", "INTEGRATION STEPS:"]
    for s in rec.integration_steps:
        lines.append(f"  {s}")
    lines += ["", "SAFETY & COMPLIANCE NOTES:"]
    for n in rec.safety_notes:
        lines.append(f"  {n}")
    lines += ["", "ELECTRICAL REQUIREMENTS:"]
    for ln in rec.electrical_requirements.split("\n"):
        lines.append(f"  {ln}")
    lines += ["", "O&M SCHEDULE:"]
    for o in rec.om_recommendations:
        lines.append(f"  • {o}")
    lines.append("=" * 70)
    return "\n".join(lines)        