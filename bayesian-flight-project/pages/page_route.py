# pages/page_route.py
import streamlit as st
from models.globals import emissions_model, AC_LIST, _flight_df, add_history
from data.aircraft import AIRCRAFT_CATALOGUE
from data.airports import AIRPORTS, COUNTRIES
from data.conflict_zones import CONFLICT_ZONES
import folium
import streamlit.components.v1 as components
from routing.geo_utils import (haversine, great_circle_points, avoidance_route,
    _build_safe_waypoints, point_in_conflict_zone, route_passes_through_zones,
    folium_to_html, add_history)

from routing.geo_utils import (haversine,great_circle_points,avoidance_route,
    _build_safe_waypoints,point_in_conflict_zone,route_passes_through_zones,
    folium_to_html,add_history)
from data.airports import AIRPORTS,COUNTRIES

def page_route():
    st.title("Route Planner")

    # Live conflict zone status banner
    closed = [z for z in CONFLICT_ZONES if z["status"] == "CLOSED"]
    st.markdown(f"""
    <div class="glass-card" style="border-left:4px solid #ef4444;">
        <b>📡 Live Airspace Intelligence — EASA CZIB 2026-03-R5 (28 Feb 2026)</b><br>
        <span style="color:#ef4444;font-weight:700;">CLOSED:</span>
        {", ".join(z["name"].split(" (")[0] for z in closed)}<br>
        <span style="color:#f97316;font-weight:700;">RESTRICTED:</span>
        UAE, Qatar, Bahrain, Lebanon, Afghanistan<br>
        <span style="color:#f59e0b;font-weight:700;">ELEVATED RISK:</span>
        Saudi Arabia northern zone, Jordan<br>
        <span style="color:#94a3b8;font-size:.85rem;">
        Source: EASA Conflict Zone Information Bulletins (CZIBs) — the authoritative advisories used by all European-certificated airlines.
        Conflict zones are drawn on the map and automatically avoided by the Safer/Balanced routing modes.
        </span>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    sorted_countries = sorted(COUNTRIES.keys())
    with c1:
        oc=st.selectbox("Origin Country",sorted_countries,
                        help=f"Choose from {len(sorted_countries)} countries · {len(AIRPORTS)} airports")
        oa=st.selectbox("Origin Airport",sorted(COUNTRIES[oc]))
    with c2:
        _uae_idx = sorted_countries.index("UAE") if "UAE" in sorted_countries else 0
        dc=st.selectbox("Destination Country",sorted_countries,index=_uae_idx,
                        help=f"Choose from {len(sorted_countries)} countries · {len(AIRPORTS)} airports")
        da=st.selectbox("Destination Airport",sorted(COUNTRIES[dc]))

    ac=st.selectbox("Aircraft Type",AC_LIST)
    mode=st.selectbox("Route Preference",[
        "Shortest — Direct great-circle (may cross conflict zones)",
        "Safer — Avoids all EASA conflict zones (recommended for Middle East/Ukraine)",
        "Greener — Minimises CO₂, light conflict avoidance",
        "Balanced — Compromise between distance, safety, and emissions",
    ])
    mode_key=mode.split(" —")[0]

    if st.button("Plan Route"):
        if oa==da: st.warning("Origin and destination cannot be the same."); return

        o_lat,o_lon=AIRPORTS[oa]["coords"]
        d_lat,d_lon=AIRPORTS[da]["coords"]
        o_icao=AIRPORTS[oa]["icao"]
        d_icao=AIRPORTS[da]["icao"]

        # Direct great-circle
        direct_pts=great_circle_points(o_lat,o_lon,d_lat,d_lon,n=80)
        direct_km=haversine(o_lat,o_lon,d_lat,d_lon)

        # Check if direct route hits conflict zones
        direct_hits=route_passes_through_zones(direct_pts)
        critical_hits=[z for z in direct_hits if z["level"]=="critical"]

        # Build adjusted route using real conflict-zone-aware waypoints
        if mode_key == "Shortest":
            adj_pts       = direct_pts
            adj_hits      = direct_hits
            safe_route_name = "Direct great-circle"
            adj_km        = direct_km
        else:
            safe_waypoints, safe_route_name, adj_factor = _build_safe_waypoints(
                o_lat, o_lon, d_lat, d_lon, direct_hits, mode_key
            )
            adj_pts  = avoidance_route(o_lat, o_lon, d_lat, d_lon, safe_waypoints)
            adj_hits = route_passes_through_zones(adj_pts)
            adj_km   = round(direct_km * adj_factor)

        extra_km = adj_km - direct_km

        base_co2,factor=emissions_model.estimate(ac,direct_km)
        adj_co2,_=emissions_model.estimate(ac,adj_km)
        extra_co2=round(adj_co2-base_co2,2)
        base_int=emissions_model.interpret(base_co2,direct_km)
        adj_int=emissions_model.interpret(adj_co2,adj_km)

        risk_risk={"Shortest":("Higher","Moderate"),"Safer":("Higher","Lower"),
                   "Greener":("Moderate","Moderate"),"Balanced":("Higher","Reduced")}
        base_risk,adj_risk=risk_risk[mode_key]

        # OpenSky lookup
        real_flights=0; real_types=""
        if _flight_df is not None:
            rf=_flight_df[(_flight_df["origin"]==o_icao)&(_flight_df["destination"]==d_icao)]
            real_flights=len(rf)
            if real_flights>0:
                top_tc=rf["typecode"].dropna().value_counts().head(3).index.tolist()
                real_types=", ".join(top_tc) if top_tc else "N/A"

        add_history({"Type":f"Route — {mode_key}","Aircraft":ac,"Distance (km)":adj_km,
                     "Risk Class":adj_risk,"Risk Score":"-","CO2 (kg)":adj_co2})

        # ── Conflict zone warning
        if direct_hits and mode_key=="Shortest":
            zones_str=", ".join(f'<b>{z["name"].split(" (")[0]}</b>' for z in direct_hits)
            st.markdown(f"""
            <div class="glass-card" style="border-left:4px solid #ef4444;">
                ⛔ <b>Direct route crosses active conflict zones:</b> {zones_str}<br>
                <span style="color:#94a3b8;font-size:.87rem;">
                Real airlines are currently avoiding or rerouting around these FIRs.
                Switch to <b>Safer</b> or <b>Balanced</b> mode to see the avoidance route.
                </span>
            </div>""", unsafe_allow_html=True)
        elif mode_key != "Shortest" and not adj_hits:
            st.markdown(f"""
            <div class="glass-card" style="border-left:4px solid #22c55e;">
                ✅ <b>{mode_key} route avoids all active conflict zones</b><br>
                <span style="color:#94a3b8;font-size:.87rem;">
                Routing via {safe_route_name}. This adds {extra_km:,} km but avoids EASA CZIB-restricted airspace.
                </span>
            </div>""", unsafe_allow_html=True)

        # ── Metrics
        st.subheader("Route Comparison")
        m1,m2,m3=st.columns(3)
        m1.metric("Direct Distance",f"{direct_km:,} km")
        m2.metric("Adjusted Distance",f"{adj_km:,} km")
        m3.metric("Extra Distance",f"{extra_km:,} km")
        m4,m5,m6=st.columns(3)
        m4.metric("Baseline CO₂",f"{base_co2:,.0f} kg")
        m5.metric("Adjusted CO₂",f"{adj_co2:,.0f} kg")
        m6.metric("Extra CO₂",f"{extra_co2:,.0f} kg")
        ce1,ce2=st.columns(2)
        with ce1: st.markdown(f'<div class="glass-card"><b>Baseline Emission Level:</b> <span style="color:{base_int["colour"]};font-weight:700;">{base_int["level"]}</span></div>',unsafe_allow_html=True)
        with ce2: st.markdown(f'<div class="glass-card"><b>Adjusted Emission Level:</b> <span style="color:{adj_int["colour"]};font-weight:700;">{adj_int["level"]}</span></div>',unsafe_allow_html=True)

        if _flight_df is not None:
            bd="#22c55e" if real_flights>0 else "#475569"
            body=(f"Found <b>{real_flights}</b> recorded flights on <b>{o_icao}→{d_icao}</b>. Types: <b>{real_types}</b>" if real_flights>0 else f"No flights found for {o_icao}→{d_icao} in sample.")
            st.markdown(f'<div class="glass-card" style="border-left:3px solid {bd};"><b>📡 OpenSky Flight Data (Jan–May 2019)</b><br>{body}</div>',unsafe_allow_html=True)

        st.subheader("Risk Comparison")
        st.markdown(f'<div class="glass-card"><b>Direct Route Risk:</b> {base_risk}<br><b>Adjusted Route Risk:</b> {adj_risk}</div>',unsafe_allow_html=True)

        # ── FOLIUM MAP with conflict zones
        st.subheader("Route Map")
        m=folium.Map(location=[(o_lat+d_lat)/2,(o_lon+d_lon)/2],zoom_start=3,tiles="CartoDB dark_matter")

        # Draw conflict zone polygons
        for zone in CONFLICT_ZONES:
            if zone["level"]=="critical": fill_op,weight=0.25,2
            elif zone["level"]=="high":   fill_op,weight=0.15,1.5
            else:                         fill_op,weight=0.10,1
            folium.Polygon(
                locations=zone["polygon"],
                color=zone["colour"],
                weight=weight,
                fill=True,
                fill_color=zone["fill_colour"],
                fill_opacity=fill_op,
                tooltip=f"⚠ {zone['name']} — {zone['status']}\n{zone['detail']}\nSource: {zone['source']}",
                popup=folium.Popup(
                    f"<b>{zone['name']}</b><br><b>Status:</b> {zone['status']}<br>"
                    f"{zone['detail']}<br><i>Source: {zone['source']}</i>",
                    max_width=300
                )
            ).add_to(m)

        # Airport dots
        for ap_name,ap_info in AIRPORTS.items():
            folium.CircleMarker(location=ap_info["coords"],radius=3,color="#475569",
                fill=True,fill_color="#475569",fill_opacity=0.6,tooltip=ap_name).add_to(m)

        # Origin / destination markers
        folium.Marker(location=(o_lat,o_lon),
            popup=folium.Popup(f"<b>Origin</b><br>{oa}",max_width=220),tooltip=f"Origin: {oa}",
            icon=folium.Icon(color="blue",icon="plane",prefix="fa")).add_to(m)
        folium.Marker(location=(d_lat,d_lon),
            popup=folium.Popup(f"<b>Destination</b><br>{da}",max_width=220),tooltip=f"Destination: {da}",
            icon=folium.Icon(color="red",icon="map-marker",prefix="fa")).add_to(m)

        # Direct route (always shown — dashed if it hits conflict zones)
        folium.PolyLine(direct_pts,color="#3b82f6",weight=2.5,opacity=0.7,
            dash_array="6" if direct_hits else None,
            tooltip=f"Direct: {direct_km:,} km{'  ⚠ CONFLICT ZONES' if direct_hits else ''}").add_to(m)

        # Adjusted route
        if mode_key!="Shortest":
            folium.PolyLine(adj_pts,color="#22c55e",weight=3,opacity=0.9,
                tooltip=f"{mode_key} route: {adj_km:,} km (avoidance)").add_to(m)

        components.html(folium_to_html(m),height=560,scrolling=False)

        # ── Map legend
        leg_zones=[(z["colour"],z["name"].split(" (")[0],z["status"]) for z in CONFLICT_ZONES[:6]]
        leg_html="".join(f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.2rem;"><div style="width:14px;height:14px;background:{c};border-radius:2px;"></div><span style="font-size:.8rem;color:#e5e7eb;">{n} — {s}</span></div>' for c,n,s in leg_zones)
        st.markdown(f'<div class="glass-card"><b>Map Legend</b><br><div style="display:flex;align-items:center;gap:.5rem;margin:.4rem 0;"><div style="width:20px;height:3px;background:#3b82f6;"></div><span style="font-size:.82rem;">Direct route</span>&nbsp;&nbsp;<div style="width:20px;height:3px;background:#22c55e;"></div><span style="font-size:.82rem;">{mode_key} route</span></div>{leg_html}<span style="color:#64748b;font-size:.78rem;">Click any shaded zone for details. Source: EASA CZIB 2026-03-R5.</span></div>',unsafe_allow_html=True)

        st.subheader("Interpretation")
        d_ac=AIRCRAFT_CATALOGUE.get(ac,{})
        st.markdown(f"""
        <div class="glass-card">
            <b>Route:</b> {oa} → {da} ({direct_km:,} km direct · {adj_km:,} km {mode_key.lower()})<br>
            <b>Aircraft:</b> {d_ac.get("maker","")} {ac} — {d_ac.get("engines","")}<br>
            <b>CO₂ Factor (EASA EDB v31):</b> {factor} kg/km<br><br>
            {'<b>⚠ Direct route conflicts:</b> ' + ", ".join(z["name"].split(" (")[0] for z in direct_hits) + "<br>" if direct_hits else ""}
            {'<b>✅ Adjusted route:</b> ' + safe_route_name + "<br>" if mode_key!="Shortest" else ""}
            <br>The {mode_key.lower()} route adds <b>{extra_km:,} km</b> and approximately
            <b>{extra_co2:,.0f} kg of extra CO₂</b> but {"reduces exposure to EASA-restricted conflict zones." if mode_key in ("Safer","Balanced") else "maintains the shortest path."}
        </div>""", unsafe_allow_html=True)


# ================================================================
# AIRCRAFT EXPLORER
# ================================================================
