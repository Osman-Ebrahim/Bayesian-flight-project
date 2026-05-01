# pages/page_fuel.py
import streamlit as st
from models.globals import fuel_model, AC_LIST, add_history
from data.aircraft import AIRCRAFT_CATALOGUE

def page_fuel():
    st.title("Fuel Efficiency Analysis")
    st.markdown('<div class="glass-card">Fuel efficiency across all Boeing and Airbus variants using <b>ICAO/EASA EDB v31</b> data. Key metric: <b>L/100 passenger-km</b> (lower = better).</div>',unsafe_allow_html=True)
    with st.form("fef"):
        c1,c2,c3=st.columns(3)
        with c1: ac=st.selectbox("Aircraft Type",AC_LIST)
        with c2: km=st.number_input("Route Distance (km)",100,15000,3000,100)
        with c3: lf=st.slider("Load Factor (%)",50,100,85)/100
        sub=st.form_submit_button("Calculate")
    if sub:
        m=fuel_model.compute(ac,km,lf)
        add_history({"Type":"Fuel Efficiency","Aircraft":ac,"Distance (km)":km,"Risk Class":m["rating"],"Risk Score":f"{m['l100']} L/100pkm","CO2 (kg)":m["co2_pax"]})
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Total Fuel Burn",f"{m['total_kg']:,.0f} kg")
        c2.metric("Fuel / Passenger",f"{m['fuel_pax']} kg")
        c3.metric("L / 100 pax-km",f"{m['l100']} L")
        c4.metric("CO₂ / Passenger",f"{m['co2_pax']} kg")
        st.markdown(f'<div style="padding:12px 18px;border-radius:14px;background:{m["rc"]};color:white;font-weight:bold;font-size:1.1rem;width:fit-content;margin:.75rem 0;">Efficiency: {m["rating"]}</div>',unsafe_allow_html=True)
        d=AIRCRAFT_CATALOGUE[ac]
        st.markdown(f'<div class="glass-card"><b>Aircraft:</b> {d["maker"]} {ac} · {d["family"]}<br><b>Engines:</b> {m["engines"]}<br><b>Seats:</b> {m["seats"]} · <b>Pax at {m["lf_pct"]}% load:</b> {m["pax"]}<br><b>Cruise:</b> {m["speed"]} km/h · <b>Duration:</b> {m["hrs"]} hrs · <b>Fuel burn:</b> {m["burn"]:,} kg/hr<br><b>ASK/kg index:</b> {m["ask_kg"]} (higher = better)</div>',unsafe_allow_html=True)
        st.subheader(f"All-Aircraft Comparison at {km:,} km")
        all_m=fuel_model.compare_all(km,lf)
        sorted_ac=sorted(all_m.items(),key=lambda x:x[1]["l100"])
        max_l=max(v["l100"] for _,v in sorted_ac) or 1
        for a,mv in sorted_ac:
            pct=mv["l100"]/max_l
            hi="background:linear-gradient(90deg,#2563eb,#7c3aed);" if a==ac else f"background:{AIRCRAFT_CATALOGUE[a].get('colour','rgba(255,255,255,.08)')}22;"
            bold="color:#fff;font-weight:800;" if a==ac else "color:#94a3b8;"
            st.markdown(f'<div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.4rem;"><span style="width:120px;font-size:.8rem;{bold}">{a}</span><div style="flex:1;height:24px;background:rgba(255,255,255,.04);border-radius:6px;overflow:hidden;"><div style="width:{pct*100:.0f}%;height:100%;{hi}border-radius:6px;display:flex;align-items:center;padding-left:.5rem;"><span style="color:white;font-size:.75rem;font-weight:600;">{mv["l100"]} L/100pkm · {mv["co2_pax"]} kg CO₂/pax</span></div></div></div>',unsafe_allow_html=True)
        best_ac=sorted_ac[0][0]; best_m=sorted_ac[0][1]
        saving=round(all_m[ac]["l100"]-best_m["l100"],2)
        if ac == best_ac:
            eff_msg = "<b>This is the most fuel-efficient option for this route.</b>"
        else:
            eff_msg = f"Most efficient: <b>{best_ac}</b> at {best_m['l100']} L/100pkm — saves <b>{saving} L/100pkm</b> vs {ac}."
        st.markdown(f'<div class="glass-card">{eff_msg}<br><b>Thresholds:</b> Excellent &lt;3.0 L · Good &lt;4.0 L · Moderate &lt;5.5 L · Poor ≥5.5 L<br><b>Source:</b> ICAO/EASA Engine Emissions Databank v31</div>',unsafe_allow_html=True)


# ================================================================
# EMISSIONS
# ================================================================
