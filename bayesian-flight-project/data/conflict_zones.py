# data/conflict_zones.py

CONFLICT_ZONES = [
    {
        "name":        "Iran (OIIX Tehran FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total airspace closure since Feb 28 2026 following US/Israeli strikes. No civil aviation permitted.",
        # Accurate coastal polygon following Iran's real southern coastline (ICAO FIR boundary)
        # Southern coast: ~29.5N at lon 44 → 27.5N at lon 50 → 27.0N at lon 56 → 25.5N at lon 60 → 25.0N at lon 63
        "polygon": [(39.8,44.0),(39.8,63.3),(25.0,63.3),(25.5,60.0),(27.0,56.0),(27.5,50.0),(29.5,48.0),(29.5,44.0)],
    },
    {
        "name":        "Iraq (ORBB Baghdad FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total closure since early March 2026. Rolling 72-hr extensions. All civil operations halted.",
        "polygon": [(37.4,38.8),(37.4,48.7),(29.0,48.7),(29.0,38.8)],
    },
    {
        "name":        "Syria (OSTT Damascus FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Closed March 2026 following regional escalation. Part of the central Middle East corridor shut.",
        "polygon": [(37.3,35.7),(37.3,42.4),(32.3,42.4),(32.3,35.7)],
    },
    {
        "name":        "Israel (LLLL Tel Aviv FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Civil airspace closed. Limited PPR arrivals/departures only. Active missile intercepts.",
        "polygon": [(33.3,34.2),(33.3,35.9),(29.5,35.9),(29.5,34.2)],
    },
    {
        "name":        "Kuwait (OKAC FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total closure. Iranian drone strike reported at US military facility in Kuwait.",
        "polygon": [(30.1,46.5),(30.1,48.5),(28.5,48.5),(28.5,46.5)],
    },
    {
        "name":        "Bahrain (OBBB FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Emergency Security Control of Air Traffic active. Very limited approved departures only.",
        "polygon": [(26.4,50.3),(26.4,50.8),(25.9,50.8),(25.9,50.3)],
    },
    {
        "name":        "Lebanon (OLBB Beirut FIR)",
        "status":      "HIGH RISK",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Airspace open but sits close to active conflict. Persistent risks from Israel-Hezbollah tensions.",
        "polygon": [(34.7,35.1),(34.7,36.6),(33.1,36.6),(33.1,35.1)],
    },
    {
        "name":        "UAE (OMAE Emirates FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Partial opening via single western routing (LUDID waypoint). Snap full closures possible. Brief 2-hr full closure Mar 16-17.",
        "polygon": [(26.1,51.0),(26.1,56.4),(22.6,56.4),(22.6,51.0)],
    },
    {
        "name":        "Qatar (OTDF FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Closed for overflights. PPR required for arrivals/departures. Iranian ballistic missile struck US bases here Jun 2025.",
        "polygon": [(26.2,50.7),(26.2,51.7),(24.5,51.7),(24.5,50.7)],
    },
    {
        "name":        "Saudi Arabia – Northern Zone (OEJD partial)",
        "status":      "RESTRICTED",
        "level":       "elevated",
        "colour":      "#f59e0b",
        "fill_colour": "#f59e0b",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Partial closure affecting area bordering Iraq and Persian Gulf. Southern routes (south of OBSOT-DANOM-KEDON-VELOD at FL320+) permitted with risk assessment.",
        "polygon": [(32.0,36.0),(32.0,48.7),(27.5,48.7),(27.5,36.0)],
    },
    {
        "name":        "Ukraine (UKBV/UKOV FIR)",
        "status":      "DO NOT FLY",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter Ukrainian airspace at any level. Active military conflict since Feb 2022.",
        "polygon": [(52.4,22.1),(52.4,40.2),(44.4,40.2),(44.4,22.1)],
    },
    {
        "name":        "Western Russia (UURR/UUOO west of 60°E)",
        "status":      "DO NOT FLY",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter Russian airspace west of 60°E at any level.",
        "polygon": [(70.0,20.0),(70.0,60.0),(50.0,60.0),(50.0,20.0)],
    },
    {
        "name":        "Sudan (HSSS Khartoum FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Closed to all civilian flights. Khartoum airport closed. Ongoing fighting between government and militant forces.",
        "polygon": [(22.0,21.8),(22.0,38.6),(8.7,38.6),(8.7,21.8)],
    },
    {
        "name":        "Afghanistan (OAKX Kabul FIR below FL320)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter below FL320. Class G airspace with no en-route ATC. Overflights at FL320+ with risk assessment.",
        "polygon": [(38.5,60.5),(38.5,74.9),(29.4,74.9),(29.4,60.5)],
    },
]

# Risk level → how strongly to avoid in routing
ZONE_RISK = {"critical": 9999, "high": 500, "elevated": 100}

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
# EXPANDED AIRCRAFT — Boeing and Airbus families
