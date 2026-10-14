"""Reference ET0 methods (pure Python, no dependencies). Units: deg C, kPa, m/s, MJ m-2 day-1, mm."""
import math

def sat_vp(t):            # FAO-56 eq. 11
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))

def _decl(doy): return 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)

def _sunset_angle(lat, doy):
    x = -math.tan(math.radians(lat)) * math.tan(_decl(doy))
    return math.acos(max(-1.0, min(1.0, x)))   # clamped for polar day/night

def daylight_hours(lat, doy):
    return 24 / math.pi * _sunset_angle(lat, doy)

def extraterrestrial_radiation(lat, doy):
    """Ra in MJ m-2 day-1 (FAO-56 eq. 21)."""
    phi, d, ws = math.radians(lat), _decl(doy), _sunset_angle(lat, doy)
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    return 24 * 60 / math.pi * 0.0820 * dr * (ws * math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.sin(ws))

def wind_at_2m(uz, z=10.0):
    return uz * 4.87 / math.log(67.8 * z - 5.42)

def penman_monteith(tmax, tmin, rh_max, rh_min, u2, lat, elev, doy, sunshine=None, rs=None, details=False, ea=None):
    """FAO-56 Penman-Monteith daily ET0 (mm/day). Give sunshine hours or rs (MJ m-2 day-1)."""
    tmean = (tmax + tmin) / 2
    p = 101.3 * ((293 - 0.0065 * elev) / 293) ** 5.26
    gamma = 0.000665 * p
    delta = 4098 * sat_vp(tmean) / (tmean + 237.3) ** 2
    es = (sat_vp(tmax) + sat_vp(tmin)) / 2
    if ea is None:
        ea = (sat_vp(tmin) * rh_max / 100 + sat_vp(tmax) * rh_min / 100) / 2
    ra, n_day = extraterrestrial_radiation(lat, doy), daylight_hours(lat, doy)
    if rs is None:
        rs = (0.25 + 0.50 * min(sunshine / n_day, 1.0)) * ra
    rso = (0.75 + 2e-5 * elev) * ra
    rns = 0.77 * rs
    rel = min(rs / rso, 1.0) if rso > 0 else 0.5
    rnl = 4.903e-9 * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * math.sqrt(ea)) * (1.35 * rel - 0.35)
    rn = rns - rnl
    et0 = (0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2))
    et0 = max(et0, 0.0)
    if details:
        return dict(et0=et0, tmean=tmean, P=p, gamma=gamma, delta=delta, es=es, ea=ea, Ra=ra, N=n_day, Rs=rs, Rso=rso, Rns=rns, Rnl=rnl, Rn=rn)
    return et0

def hargreaves(tmax, tmin, lat, doy):
    """Hargreaves-Samani daily ET0 (mm/day); temperature only."""
    return max(0.0023 * ((tmax + tmin) / 2 + 17.8) * math.sqrt(max(tmax - tmin, 0)) * 0.408 * extraterrestrial_radiation(lat, doy), 0.0)

_MID = [15, 45, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]   # mid-month day of year
_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def thornthwaite(monthly_tmean, lat):
    """Thornthwaite PET for 12 monthly mean temperatures -> list of mm/month."""
    heat = sum((t / 5) ** 1.514 for t in monthly_tmean if t > 0)
    a = 6.75e-7 * heat**3 - 7.71e-5 * heat**2 + 1.792e-2 * heat + 0.49239
    out = []
    for m, t in enumerate(monthly_tmean):
        if t <= 0 or heat == 0: pet = 0.0
        elif t < 26.5: pet = 16 * (10 * t / heat) ** a
        else: pet = -415.85 + 32.24 * t - 0.43 * t * t
        out.append(pet * daylight_hours(lat, _MID[m]) / 12 * _DAYS[m] / 30)
    return out

def penman_monteith_temp_only(tmax, tmin, lat, elev, doy, u2=2.0, krs=0.16, k0=2.0):
    """FAO-56 for stations with temperature only: Rs from the daily range, dew point = Tmin - k0, default wind."""
    rs = krs * math.sqrt(max(tmax - tmin, 0)) * extraterrestrial_radiation(lat, doy)
    return penman_monteith(tmax, tmin, 0, 0, u2, lat, elev, doy, rs=rs, ea=sat_vp(tmin - k0))

def priestley_taylor(tmax, tmin, rh_max, rh_min, u2, lat, elev, doy, sunshine=None, rs=None, alpha=1.26):
    """Priestley-Taylor ET (mm/day): radiation term only, scaled by alpha."""
    d = penman_monteith(tmax, tmin, rh_max, rh_min, u2, lat, elev, doy, sunshine=sunshine, rs=rs, details=True)
    return max(alpha * d["delta"] / (d["delta"] + d["gamma"]) * 0.408 * d["Rn"], 0.0)

def blaney_criddle(tmax, tmin, lat, doy):
    """Simple Blaney-Criddle ET (mm/day): p (0.46 T + 8.13), p = day's % of annual daylight hours."""
    year = sum(daylight_hours(lat, j) for j in range(1, 366))
    return max(100 * daylight_hours(lat, doy) / year * (0.46 * (tmax + tmin) / 2 + 8.13), 0.0)

def fit_hargreaves_coefficient(pm_values, hargreaves_values):
    """Least-squares factor k so that k * Hargreaves best matches Penman-Monteith."""
    return sum(p * h for p, h in zip(pm_values, hargreaves_values)) / sum(h * h for h in hargreaves_values)
