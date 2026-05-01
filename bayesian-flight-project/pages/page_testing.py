# pages/page_testing.py
import streamlit as st
from models.globals import risk_model, fuel_model, AVIATION_CSV
from data.aircraft import AIRCRAFT_CATALOGUE
from data.conflict_zones import CONFLICT_ZONES


def page_testing():
    st.title("Testing & Evaluation")

    if risk_model.trained_on_data:
        rd = risk_model.risk_dist
        st.markdown(
            f'<div class="glass-card" style="border-left:3px solid #22c55e;">' +
            f'<b>✓ Data-Driven</b> — {risk_model.n_training:,} NTSB records, Laplace α=1. ' +
            f'High:{rd.get("High",0):,} · Med:{rd.get("Medium",0):,} · Low:{rd.get("Low",0):,}' +
            '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="glass-card" style="border-left:3px solid #f59e0b;">' +
            f'<b>⚠ Prototype Mode</b> — NTSB CSV not found at {AVIATION_CSV}</div>',
            unsafe_allow_html=True)

    st.subheader("Risk Model Tests")
    for s in [
        {"name":"Safe",      "weather":"low",    "maintenance":"good","aircraft_age":"new","route_complexity":"low",   "congestion":"low",   "expected":"Low"},
        {"name":"Moderate",  "weather":"medium", "maintenance":"fair","aircraft_age":"mid","route_complexity":"medium","congestion":"medium","expected":"Medium"},
        {"name":"High Risk", "weather":"high",   "maintenance":"poor","aircraft_age":"old","route_complexity":"high",  "congestion":"high",  "expected":"High"},
    ]:
        inp = {k: s[k] for k in ["weather","maintenance","aircraft_age","route_complexity","congestion"]}
        res = risk_model.predict(inp)
        passed = "✅" if res["class"] == s["expected"] else "⚠️"
        st.markdown(
            f'<div class="glass-card" style="margin-bottom:.75rem;">' +
            f'<b>{s["name"]}</b> · Expected: {s["expected"]} · Got: {res["class"]} · Score: {res["score"]}/100 · {passed}<br>' +
            f'Posteriors: Low={res["probabilities"]["Low"]*100:.1f}% | Med={res["probabilities"]["Medium"]*100:.1f}% | High={res["probabilities"]["High"]*100:.1f}%' +
            '</div>', unsafe_allow_html=True)

    st.subheader("Fuel Efficiency Tests")
    for a in ["A320neo","A350-900","B787-9","B777-300ER","A380"]:
        m = fuel_model.compute(a, 5000, 0.85)
        st.markdown(
            f'<div class="glass-card" style="margin-bottom:.5rem;">' +
            f'<b>{a}</b> · 5,000 km · 85% load → {m["l100"]} L/100pkm · {m["co2_pax"]} kg CO₂/pax · {m["rating"]}' +
            '</div>', unsafe_allow_html=True)

    st.subheader("Conflict Zone Coverage")
    for z in CONFLICT_ZONES:
        col = {"critical":"#ef4444","high":"#f97316","elevated":"#f59e0b"}.get(z["level"],"#94a3b8")
        st.markdown(
            f'<div class="glass-card" style="margin-bottom:.4rem;border-left:3px solid {col};padding:.7rem 1rem;">' +
            f'<b>{z["name"]}</b> · <span style="color:{col};">{z["status"]}</span><br>' +
            f'<span style="color:#94a3b8;font-size:.83rem;">{z["source"]} — {z["detail"][:100]}…</span>' +
            '</div>', unsafe_allow_html=True)

    st.subheader("Aims & Objectives Checklist")
    for icon, aim, ev in [
        ("✅","Bayesian model for accident probability","Naive Bayes, NTSB-trained, log-probabilities, Laplace smoothing"),
        ("✅","Fuel efficiency & emissions component",f"Fuel Efficiency page: L/100pkm, ASK/kg, CO₂/pax across {len(AIRCRAFT_CATALOGUE)} aircraft variants"),
        ("✅","Interactive Streamlit dashboard","Multi-page app with Folium map, charts, metrics"),
        ("✅","Collect & preprocess aviation datasets","NTSB, OpenSky, EASA EDB v31, EASA CZIBs integrated"),
        ("✅","Bayesian network for accident probability","Implemented — see Risk Analysis"),
        ("✅","Emissions estimation model","EmissionsModel — EASA-derived CO₂ per aircraft/km"),
        ("✅","Unified framework","Single app — Risk, Fuel, Emissions, Route all connected"),
        ("✅","Streamlit interface","This application"),
        ("✅","Validate with real-world data","NTSB test scenarios + OpenSky cross-reference + EASA CZIBs"),
        ("✅","Ethical & professional implications","Ethics page — BCS, GDPR, EU AI Act, DO-178C, conflict zone accountability"),
    ]:
        st.markdown(
            f'<div class="glass-card" style="padding:.8rem 1.1rem;margin-bottom:.5rem;">' +
            f'{icon} <b>{aim}</b><br><span style="color:#94a3b8;font-size:.85rem;">→ {ev}</span>' +
            '</div>', unsafe_allow_html=True)
