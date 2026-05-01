# pages/page_aircraft.py
import streamlit as st
from data.aircraft import AIRCRAFT_CATALOGUE
import streamlit.components.v1 as components

def page_aircraft():
    st.title("Aircraft Explorer")
    st.markdown('<div class="glass-card">Interactive 360° engine model. Select any aircraft for its specifications and EASA emissions context.</div>',unsafe_allow_html=True)
    choice=st.selectbox("Choose Model",["Airplane Engine"]+[f"{ac} (coming soon)" for ac in["Airbus A380","Boeing 787","Airbus A320","Boeing 777"]])
    st.subheader(f"360° Model: {choice}")
    if choice=="Airplane Engine":
        components.html("""<div class="sketchfab-embed-wrapper"><iframe title="Airplane engine" width="100%" height="500" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share src="https://sketchfab.com/models/bb658020350e461aa8d915bc58cd6ef9/embed"></iframe><p style="font-size:13px;color:#d1d5db;margin-top:6px;"><a href="https://sketchfab.com/3d-models/airplane-engine-bb658020350e461aa8d915bc58cd6ef9" target="_blank" style="color:#38bdf8;font-weight:700;">Airplane engine</a> by Ely HADDAD on Sketchfab</p></div>""",height=570)
    else:
        st.info("A 360° model will be added once a public Sketchfab embed is selected.")
    ac_key=choice.replace(" (coming soon)","").replace("Airbus ","A").replace("Boeing ","B").replace("A380","A380").replace("B787","B787-9").replace("A320","A320").replace("B777","B777-300ER")
    d=AIRCRAFT_CATALOGUE.get(ac_key,{})
    if d:
        st.markdown(f'<div class="glass-card"><b>Family:</b> {d.get("maker","")} — {d.get("family","")}<br><b>Seats:</b> {d.get("seats","N/A")} · <b>Range:</b> {d.get("range_km","N/A"):,} km<br><b>Engines:</b> {d.get("engines","N/A")}<br><b>CO₂ Factor:</b> {d.get("co2_km","N/A")} kg/km (EASA EDB v31)</div>',unsafe_allow_html=True)


# ================================================================
# SCENARIO HISTORY
# ================================================================
