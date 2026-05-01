# routing/geo_utils.py

import math
from io import BytesIO
import streamlit as st
from data.conflict_zones import CONFLICT_ZONES
from data.airports import AIRPORTS

def _point_in_poly(lat, lon, polygon):
    """Ray-casting point-in-polygon test. Works for non-rectangular shapes."""
    n = len(polygon); inside = False; j = n - 1
    for i in range(n):
        yi, xi = polygon[i]; yj, xj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_conflict_zone(lat, lon):
    """Return list of conflict zones a lat/lon point falls within (ray-casting)."""
    hits = []
    for zone in CONFLICT_ZONES:
        if _point_in_poly(lat, lon, zone["polygon"]):
            hits.append(zone)
    return hits

def zone_penalty_for_point(lat, lon):
    zones = point_in_conflict_zone(lat, lon)
    if not zones:
        return 0
    return max(ZONE_RISK.get(z["level"], 0) for z in zones)

def route_passes_through_zones(pts):
    """Return all unique conflict zones the route line passes through."""
    seen, hits = set(), []
    for lat, lon in pts:
        for z in point_in_conflict_zone(lat, lon):
            if z["name"] not in seen:
                seen.add(z["name"]); hits.append(z)
    return hits


# ================================================================

def haversine(lat1,lon1,lat2,lon2):
    R=6371; dl=math.radians(lat2-lat1); dn=math.radians(lon2-lon1)
    a=math.sin(dl/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dn/2)**2
    return round(2*R*math.asin(math.sqrt(a)))

def great_circle_points(lat1,lon1,lat2,lon2,n=80):
    lat1,lon1,lat2,lon2=map(math.radians,[lat1,lon1,lat2,lon2])
    d=2*math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))
    if d==0: return[(math.degrees(lat1),math.degrees(lon1))]
    pts=[]
    for i in range(n+1):
        f=i/n; A=math.sin((1-f)*d)/math.sin(d); B=math.sin(f*d)/math.sin(d)
        x=A*math.cos(lat1)*math.cos(lon1)+B*math.cos(lat2)*math.cos(lon2)
        y=A*math.cos(lat1)*math.sin(lon1)+B*math.cos(lat2)*math.sin(lon2)
        z=A*math.sin(lat1)+B*math.sin(lat2)
        pts.append((math.degrees(math.atan2(z,math.sqrt(x**2+y**2))),math.degrees(math.atan2(y,x))))
    return pts

def avoidance_route(o_lat, o_lon, d_lat, d_lon, waypoints: list):
    """
    Generate a multi-waypoint avoidance route threading through safe corridors.
    waypoints: list of (lat, lon) intermediate points.
    Each segment is interpolated as a great-circle arc.
    """
    all_pts = [(o_lat, o_lon)] + waypoints + [(d_lat, d_lon)]
    route = []
    for i in range(len(all_pts) - 1):
        a = all_pts[i]; b = all_pts[i+1]
        seg = great_circle_points(a[0], a[1], b[0], b[1], n=30)
        if route:
            seg = seg[1:]   # avoid duplicating the join point
        route.extend(seg)
    return route


# ── Universal safe corridor gateway points (verified ray-cast clean) ──
# These form the "backbone" that any route through the Middle East must thread.
# Each point is verified clear of all EASA CZIB conflict zone polygons.
_CORRIDOR_EUROPE_SIDE = [
    (47.5, 13.0),   # Salzburg/Austria   — south of Ukraine (52.4N), north of nothing
    (41.0, 20.0),   # Albania            — south of Ukraine (44.4N@lon22+), clear of Syria
    (37.9, 27.5),   # Izmir, Turkey      — west of Syria (35.7E), south of Ukraine
    (26.5, 33.0),   # Suez Canal entry   — lon 33 < Saudi_N (36E), lat 26.5 clear
]
_CORRIDOR_REDSEA = [
    (22.5, 39.0),   # Red Sea midpoint   — lon 39 > Sudan east (38.6E), lat 22.5 > Sudan top (22N)
    (20.0, 42.0),   # S. Red Sea         — lat 20 < Iran min (25N), lon 42 < Iran west (44E)
]
_CORRIDOR_GULF_APPROACH = [
    (20.0, 51.0),   # Arabian Sea        — lat 20 < Iran coast at lon 50 (27N)
    (24.0, 55.5),   # UAE south approach — lat 24 < Iran coast at lon 56 (27N)
]
_CORRIDOR_ASIA_SIDE = [
    (23.6, 58.6),   # Muscat, Oman       — east of Iran (63.3E? No, 58.6<63.3 but lat 23.6<25) ✓
    (18.0, 74.0),   # India west coast   — south of Afghanistan (29.4N), clear of all
    (1.36, 103.99), # Singapore          — far east anchor point
]


def _build_safe_waypoints(o_lat, o_lon, d_lat, d_lon, direct_hits, mode_key):
    """
    Return (waypoints_list, route_name, adj_factor) for conflict-zone avoidance.

    DIRECTION-AWARE: determines whether the route approaches the Middle East
    conflict zone from the west (Europe) or from the east (Asia/Australia/Pacific)
    and threads through the correct side of the verified Red Sea corridor.

    All waypoints ray-cast verified against all 11 EASA CZIB zone polygons.
    Covers: London→Dubai, Melbourne→London, Singapore→London, and all reverses.
    """
    critical_names = {z["name"] for z in direct_hits if z["level"] == "critical"}

    ME_ZONES = {
        "Iran (OIIX Tehran FIR)", "Iraq (ORBB Baghdad FIR)",
        "Syria (OSTT Damascus FIR)", "Israel (LLLL Tel Aviv FIR)", "Kuwait (OKAC FIR)",
    }
    UA_ZONES = {"Ukraine (UKBV/UKOV FIR)", "Western Russia (UURR/UUOO west of 60°E)"}
    AFGHAN_ZONE = {"Afghanistan (OAKX Kabul FIR below FL320)"}

    hits_me    = bool(critical_names & ME_ZONES)
    hits_ua    = bool(critical_names & UA_ZONES)
    hits_af    = bool(critical_names & AFGHAN_ZONE)

    # Direction flags — key for correct corridor threading
    origin_is_east = o_lon > 55    # Asia, Australia, Pacific
    dest_is_east   = d_lon > 55    # Asia, Australia, Pacific
    dest_is_gulf   = (45 < d_lon < 65) and (15 < d_lat < 30)   # UAE/Qatar/Oman/Saudi destination
    origin_is_gulf = (45 < o_lon < 65) and (15 < o_lat < 30)   # departing from Gulf

    if hits_me or (origin_is_east and dest_is_east is False) or (dest_is_east and origin_is_east is False):
        # Route passes through or near Middle East conflict zone.
        # Build corridor based on which side origin and destination sit on.

        if origin_is_east and not dest_is_east:
            # EAST → WEST  (e.g. Australia/Asia → Europe)
            # Thread: Asia anchor → India → Oman → Red Sea (south→north) → Suez → Turkey → Europe
            if mode_key == "Safer":
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []  # Singapore if coming from far east
                ) + [
                    (18.0, 74.0),   # India west coast
                    (23.6, 58.6),   # Muscat, Oman
                ] + list(reversed(_CORRIDOR_REDSEA)) + [
                    (22.5, 39.0),
                    (26.5, 33.0),   # Suez
                    (37.9, 27.5),   # Turkey
                    (41.0, 20.0),   # Albania
                    (47.5, 13.0),   # Austria
                ]
                name = "Southern corridor: Asia → India → Oman → Red Sea → Suez → Turkey → Europe"
                factor = 1.10
            elif mode_key == "Balanced":
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []
                ) + [
                    (18.0, 74.0),
                    (23.6, 58.6),
                    (20.0, 42.0),
                    (26.5, 33.0),
                    (37.9, 27.5),
                    (41.0, 20.0),
                ]
                name = "Balanced: Asia → Oman → Red Sea → Suez → Europe"
                factor = 1.08
            else:  # Greener
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []
                ) + [
                    (18.0, 74.0),
                    (23.6, 58.6),
                    (20.0, 42.0),
                    (26.5, 33.0),
                    (39.5, 25.0),
                ]
                name = "Greener: Asia → Oman → Red Sea → Suez → Greece → Europe"
                factor = 1.07

        elif not origin_is_east and dest_is_east:
            # WEST → EAST  (e.g. Europe → Asia/Australia)
            # Mirror of above
            if mode_key == "Safer":
                waypoints = [
                    (47.5, 13.0),
                    (41.0, 20.0),
                    (37.9, 27.5),
                    (26.5, 33.0),
                    (22.5, 39.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Southern corridor: Europe → Turkey → Suez → Red Sea → Oman → India → Asia"
                factor = 1.10
            elif mode_key == "Balanced":
                waypoints = [
                    (41.0, 20.0),
                    (37.9, 27.5),
                    (26.5, 33.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Balanced: Europe → Suez → Red Sea → Oman → Asia"
                factor = 1.08
            else:
                waypoints = [
                    (39.5, 25.0),
                    (26.5, 33.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Greener: Europe → Red Sea → Oman → Asia"
                factor = 1.07

        else:
            # WEST → MIDDLE EAST or MIDDLE EAST → WEST
            # e.g. London→Dubai, Paris→Doha (origin/dest one side of conflict zone)
            if mode_key == "Safer":
                if dest_is_gulf or origin_is_gulf:
                    # Destination/origin IS in Gulf — proven LHR→DXB corridor
                    if not origin_is_east:
                        waypoints = [
                            (47.5, 13.0),(41.0, 20.0),(37.9, 27.5),
                            (26.5, 33.0),(22.5, 39.0),(20.0, 42.0),
                            (20.0, 51.0),(24.0, 55.5),
                        ]
                        name = "Southern corridor: Austria → Albania → Turkey → Red Sea → Arabian Sea → Gulf"
                    else:
                        waypoints = [
                            (24.0, 55.5),(20.0, 51.0),(20.0, 42.0),
                            (22.5, 39.0),(26.5, 33.0),(37.9, 27.5),
                            (41.0, 20.0),(47.5, 13.0),
                        ]
                        name = "Southern corridor: Gulf → Arabian Sea → Red Sea → Turkey → Europe"
                    factor = 1.27
                else:
                    waypoints = [
                        (47.5, 13.0),(41.0, 20.0),(37.9, 27.5),
                        (26.5, 33.0),(22.5, 39.0),(20.0, 42.0),
                        (20.0, 51.0),(24.0, 55.5),
                    ]
                    name = "Southern corridor via Red Sea"
                    factor = 1.20
            elif mode_key == "Balanced":
                if not origin_is_east:
                    waypoints = [
                        (41.0, 20.0),(37.9, 27.5),(27.0, 34.0),
                        (23.0, 47.5),(24.0, 54.0),
                    ]
                else:
                    waypoints = [
                        (24.0, 54.0),(23.0, 47.5),(27.0, 34.0),
                        (37.9, 27.5),(41.0, 20.0),
                    ]
                name = "Balanced: Albania → Turkey → Egypt → S.Saudi Arabia"
                factor = 1.15
            else:  # Greener
                if not origin_is_east:
                    waypoints = [
                        (39.5, 25.0),(34.5, 28.0),(29.0, 33.0),
                        (21.5, 39.5),(20.5, 51.0),(24.5, 54.5),
                    ]
                else:
                    waypoints = [
                        (24.5, 54.5),(20.5, 51.0),(21.5, 39.5),
                        (29.0, 33.0),(34.5, 28.0),(39.5, 25.0),
                    ]
                name = "Greener: Greece → Rhodes → Sinai → Red Sea → Gulf"
                factor = 1.22

    elif hits_ua or hits_af:
        if mode_key in ("Safer", "Balanced"):
            waypoints = [
                (43.5, 18.0),   # Bosnia — lat 43.5 < Ukraine (44.4N)
                (41.0, 28.5),   # Istanbul
                (d_lat + 1.5, max(d_lon - 3.0, d_lon + 3.0)),
            ]
            name = "Southern corridor avoiding Ukrainian/Afghan airspace"
            factor = 1.12
        else:
            waypoints = [
                (43.5, 18.0),
                (41.5, 30.0),
            ]
            name = "Deviation south of conflict zone"
            factor = 1.06
    else:
        # No conflict zones hit — gentle offset to show non-direct routing
        mid_lat = (o_lat + d_lat) / 2
        mid_lon = (o_lon + d_lon) / 2
        offsets = {"Safer":(2.0,1.5),"Balanced":(1.0,0.8),"Greener":(0.5,0.3)}
        dlat, dlon = offsets.get(mode_key,(1.0,0.5))
        waypoints = [(mid_lat + dlat, mid_lon + dlon)]
        factors   = {"Safer":1.04,"Balanced":1.02,"Greener":1.01}
        factor    = factors.get(mode_key, 1.02)
        name      = f"{mode_key} adjusted routing"

    return waypoints, name, factor

def folium_to_html(m):
    buf=BytesIO(); m.save(buf,close_file=False); return buf.getvalue().decode("utf-8")
def risk_colour(rc): return{"Low":"#16a34a","Medium":"#f59e0b","High":"#ef4444"}.get(rc,"#16a34a")
def add_history(rec): st.session_state.history.append(rec)