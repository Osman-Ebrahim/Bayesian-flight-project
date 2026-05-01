# pages/page_emissions.py
import streamlit as st
from models.globals import emissions_model, AC_LIST, add_history
from data.aircraft import AIRCRAFT_CATALOGUE

def page_emissions():
    st.title("Emissions Analysis")
    st.markdown('<div class="glass-card">CO₂ factors from <b>ICAO/EASA EDB v31</b> for all Boeing and Airbus variants. Results classified Low / Moderate / High.</div>',unsafe_allow_html=True)
    with st.form("emf"):
        c1,c2=st.columns(2)
        with c1: ac=st.selectbox("Aircraft Type",AC_LIST,key="em_ac")
        with c2: km=st.number_input("Route Distance (km)",100,20000,3000,100,key="em_km")
        sub=st.form_submit_button("Estimate Emissions")
    if sub:
        co2,factor=emissions_model.estimate(ac,km)
        interp=emissions_model.interpret(co2,km)
        add_history({"Type":"Emissions","Aircraft":ac,"Distance (km)":km,"Risk Class":interp["level"],"Risk Score":"-","CO2 (kg)":co2})
        c1,c2,c3=st.columns(3)
        c1.metric("Estimated CO₂",f"{co2:,.2f} kg"); c2.metric("Factor",f"{factor} kg/km"); c3.metric("Level",interp["level"])
        st.markdown(f'<div style="padding:12px 16px;border-radius:14px;background:{interp["colour"]};color:white;font-weight:bold;width:fit-content;margin:.75rem 0;">{interp["level"]} Emission Level</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card">{interp["message"]}<br><br>🚗 ≈ <b>{interp["cars_equivalent"]:,} years</b> of UK car driving &nbsp;·&nbsp; 🌳 ≈ <b>{interp["trees_equivalent"]:,} trees</b> needed for one year</div>',unsafe_allow_html=True)
        st.subheader("Aircraft Comparison")
        sample_ac=["A319","A320neo","A321neo","A330neo","A350-900","A380","B737 MAX 8","B787-9","B777-300ER"]
        max_co2=max(emissions_model.estimate(a,km)[0] for a in sample_ac) or 1
        for a in sorted(sample_ac,key=lambda x:emissions_model.estimate(x,km)[0]):
            c,_=emissions_model.estimate(a,km); pct=c/max_co2
            hi="background:linear-gradient(90deg,#2563eb,#7c3aed);" if a==ac else "background:rgba(255,255,255,.07);"
            st.markdown(f'<div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.4rem;"><span style="width:110px;font-size:.8rem;color:{"#fff" if a==ac else "#94a3b8"};">{a}</span><div style="flex:1;height:24px;background:rgba(255,255,255,.04);border-radius:6px;overflow:hidden;"><div style="width:{pct*100:.0f}%;height:100%;{hi}border-radius:6px;display:flex;align-items:center;padding-left:.5rem;"><span style="color:white;font-size:.75rem;font-weight:600;">{c:,.0f} kg</span></div></div></div>',unsafe_allow_html=True)


# ================================================================
# ROUTE PLANNER  (admin only — with EASA conflict zones)
# ================================================================
