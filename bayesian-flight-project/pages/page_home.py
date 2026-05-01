# pages/page_home.py
import streamlit as st
from models.globals import (
    risk_model, fuel_model, AC_LIST, AIRCRAFT_CATALOGUE,
    _flight_df, _ntsb_df, _flight_err, AVIATION_CSV,
    AIRPORTS, COUNTRIES
)

# ── Reusable card renderer ────────────────────────────────────────────────────
def _card(body, border="#3b82f6", pad=".9rem 1.2rem"):
    st.markdown(
        f'<div class="glass-card" style="border-left:3px solid {border};padding:{pad};">'
        f'{body}</div>', unsafe_allow_html=True)

def page_home():

    trained = risk_model.trained_on_data

    # ── Hero ──────────────────────────────────────────────────────────────────
    mode   = "🟢 Live NTSB Data" if trained else "🟡 Prototype Mode"
    n_recs = f"{risk_model.n_training:,}" if trained else "—"
    st.markdown(f"""
    <div class="hero-card">
        <h1>✈️ Bayesian Aviation Decision-Support System</h1>
        <p style="color:#94a3b8;font-size:1.05rem;margin:.4rem 0 1rem;">
            Real NTSB accident data · Bayesian inference · Fuel efficiency ·
            CO₂ emissions · Live conflict zone routing
        </p>
        <span style="background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.3);
            color:#60a5fa;font-size:.8rem;padding:.2rem .8rem;border-radius:20px;">
            {mode} &nbsp;·&nbsp; {n_recs} records &nbsp;·&nbsp;
            {len(AIRPORTS):,} airports &nbsp;·&nbsp; {len(AIRCRAFT_CATALOGUE)} aircraft types
        </span>
    </div>""", unsafe_allow_html=True)

    # ── Live stats ────────────────────────────────────────────────────────────
    if trained:
        rd = risk_model.risk_dist
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("NTSB Records",     f"{risk_model.n_training:,}")
        c2.metric("High-Risk Events", f"{rd.get('High',0):,}")
        c3.metric("Med-Risk Events",  f"{rd.get('Medium',0):,}")
        c4.metric("Low-Risk Events",  f"{rd.get('Low',0):,}")
    else:
        c1,c2,c3 = st.columns(3)
        c1.metric("Core Modules","6")
        c2.metric("Methods","Bayesian + Haversine")
        c3.metric("Mode","Prototype")

    # ── Flight data stats (only if OpenSky loaded) ────────────────────────────
    if _flight_df is not None:
        fc1,fc2,fc3 = st.columns(3)
        fc1.metric("Flight Records", f"{len(_flight_df):,}")
        valid = _flight_df[_flight_df["origin"] != _flight_df["destination"]]
        top   = valid.groupby(["origin","destination"]).size().nlargest(1).reset_index()
        if len(top):
            fc2.metric("Busiest Route",
                       f"{top.iloc[0]['origin']}→{top.iloc[0]['destination']}")
        fc3.metric("Aircraft Types", str(len(AIRCRAFT_CATALOGUE)))

    # ── System modules grid ───────────────────────────────────────────────────
    st.markdown("### ⚙️ System Modules")
    MODULES = [
        ("🎯","Risk Analysis",
         f"Naive Bayes on {'real NTSB data' if trained else 'prototype values'} — "
         "Low / Medium / High posteriors."),
        ("⛽","Fuel Efficiency",
         f"L/100pkm, ASK/kg, CO₂/pax across {len(AIRCRAFT_CATALOGUE)} variants (EASA EDB v31)."),
        ("🌍","Emissions Analysis",
         "CO₂ per route with car-year & tree equivalents for context."),
        ("🗺️","Route Planner",
         "14 EASA CZIB conflict zones — Safer / Balanced / Greener corridors."),
        ("✈️","Aircraft Explorer",
         "360° engine model with type-specific specs and emissions data."),
        ("📊","Scenario History",
         "Review and export all analysed scenarios as CSV."),
    ]
    for row in [MODULES[:3], MODULES[3:]]:
        cols = st.columns(3)
        for col,(icon,title,desc) in zip(cols,row):
            with col:
                st.markdown(
                    f'<div class="glass-card" style="min-height:130px;">'
                    f'<div style="font-size:1.4rem;margin-bottom:.4rem;">{icon}</div>'
                    f'<b style="color:#e2e8f0;">{title}</b>'
                    f'<p style="color:#64748b;font-size:.83rem;margin:.3rem 0 0;">{desc}</p>'
                    f'</div>', unsafe_allow_html=True)

    # ── Data sources ──────────────────────────────────────────────────────────
    st.markdown("### 📦 Data Sources")
    SOURCES = [
        ("NTSB AviationData.csv",
         "88,000+ accident records — injury, weather, phase of flight",
         "Risk model training", trained),
        ("OpenSky Flightlist CSVs",
         "Real ICAO routes (Jan–May 2019)",
         "Route cross-reference", _flight_df is not None),
        ("EASA/ICAO EDB v31",
         "Engine fuel consumption — 500+ variants",
         "CO₂ factors + fuel efficiency", True),
        ("EASA CZIBs 2026-03-R5",
         "Live conflict zone advisories — Iran, Iraq, Syria, Ukraine etc.",
         "Route Planner conflict avoidance", True),
    ]
    for name,desc,use,ok in SOURCES:
        clr = "#22c55e" if ok else "#ef4444"
        ico = "✓" if ok else "✗"
        _card(
            f'<span style="color:{clr};font-weight:700;">{ico} {name}</span><br>'
            f'<span style="color:#94a3b8;font-size:.85rem;">{desc}</span>'
            f'&nbsp;·&nbsp;<em style="color:#60a5fa;font-size:.82rem;">Used for: {use}</em>',
            border=clr)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    _card("<b>ℹ️ Academic Disclaimer</b><br>"
          "<span style='color:#64748b;font-size:.85rem;'>"
          "This prototype is for academic purposes only. It does not constitute "
          "certified aviation guidance and must not replace licensed systems or personnel."
          "</span>")