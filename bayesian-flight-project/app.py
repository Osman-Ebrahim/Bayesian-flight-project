"""
Bayesian Aviation Decision-Support System
BSc Computer Science FYP — Osman Ebrahim, 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import math,os,gzip,glob
import folium
import streamlit.components.v1 as components
from io import BytesIO

st.set_page_config(page_title="Bayesian Flight Project",layout="wide")

# ================================================================
# SESSION STATE
# ================================================================
for _k, _v in [("admin_logged_in", False), ("show_admin_login", False), ("history", [])]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ================================================================
# PATH RESOLUTION

from ui.styles import inject_css; inject_css()
from ui.layout import render_header,get_pages,render_nav
from pages.page_home      import page_home
from pages.page_risk      import page_risk
from pages.page_fuel      import page_fuel
from pages.page_emissions import page_emissions
from pages.page_route     import page_route
from pages.page_aircraft  import page_aircraft
from pages.page_history   import page_history
from pages.page_ethics    import page_ethics
from pages.page_testing   import page_testing

render_header()
pages=get_pages()
page=render_nav(pages)

if   page=="Home":                  page_home()
elif page=="Risk Analysis":         page_risk()
elif page=="Fuel Efficiency":       page_fuel()
elif page=="Emissions Analysis":    page_emissions()
elif page=="Route Planner":         page_route()
elif page=="Aircraft Explorer":     page_aircraft()
elif page=="Scenario History":      page_history()
elif page=="Ethics & Implications": page_ethics()
elif page=="Testing & Evaluation":  page_testing()

st.markdown("""<hr style="margin-top:2rem;"><div style="text-align:center;padding:1rem;color:#94a3b8;font-size:.85rem;">© 2026 Osman Ebrahim — All Rights Reserved<br>Developed as part of a BSc Computer Science Final Year Project.<br>This system is a prototype for academic and research purposes only.</div>""",unsafe_allow_html=True)