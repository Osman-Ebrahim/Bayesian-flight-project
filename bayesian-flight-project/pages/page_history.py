# pages/page_history.py
import streamlit as st
import pandas as pd

def page_history():
    st.title("Scenario History")
    st.markdown('<div class="glass-card">Review and export all analysed scenarios.</div>',unsafe_allow_html=True)
    if st.session_state.history:
        for i,item in enumerate(st.session_state.history,1):
            st.markdown(f'<div class="glass-card" style="margin-bottom:.75rem;"><h4 style="margin-top:0;">Scenario {i}</h4><b>Type:</b> {item["Type"]}<br><b>Aircraft:</b> {item["Aircraft"]}<br><b>Distance (km):</b> {item["Distance (km)"]}<br><b>Risk Class / Mode:</b> {item["Risk Class"]}<br><b>Risk Score:</b> {item["Risk Score"]}<br><b>CO₂ (kg):</b> {item["CO2 (kg)"]}</div>',unsafe_allow_html=True)
        csv=pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV",data=csv,file_name="scenario_history.csv",mime="text/csv")
        if st.button("Clear History"): st.session_state.history=[]; st.rerun()
    else:
        st.info("No scenarios saved yet.")


# ================================================================
# ETHICS
# ================================================================
