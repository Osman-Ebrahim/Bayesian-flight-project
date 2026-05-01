# ui/layout.py

import streamlit as st
from models.globals import risk_model

ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin123"

def render_header():
    admin=st.session_state.admin_logged_in
    ab='<span class="admin-badge">Admin</span>' if admin else ""
    db=(f'<span class="live-badge">NTSB · {risk_model.n_training:,} records</span>'
        if risk_model.trained_on_data else '<span class="proto-badge">Prototype Mode</span>')
    st.markdown(f"""
    <div style="padding:1.2rem 2rem;margin-bottom:1rem;border-radius:16px;
        background:linear-gradient(135deg,#1e293b,#0f172a);
        border:1px solid rgba(148,163,184,.2);box-shadow:0 10px 30px rgba(0,0,0,.25);">
        <h2 style="margin:0;color:white;display:inline;">
            ✈️ Bayesian Aviation Decision-Support System
        </h2>{ab}{db}
        <p style="margin:0;color:#cbd5e1;font-size:.95rem;">
            Final Year Project • Aviation Risk, Fuel Efficiency, Emissions &amp; Route Optimisation
        </p>
    </div>""", unsafe_allow_html=True)
    _,btn=st.columns([6,1])
    with btn:
        if admin:
            if st.button("Logout",use_container_width=True):
                st.session_state.admin_logged_in=False; st.session_state.show_admin_login=False; st.rerun()
        else:
            if st.button("Admin Login",use_container_width=True):
                st.session_state.show_admin_login=not st.session_state.show_admin_login; st.rerun()
    if st.session_state.show_admin_login and not admin:
        _,fc,_=st.columns([2,2,2])
        with fc:
            st.markdown('<div class="auth-card"><h4 style="margin-top:0;text-align:center;">Admin Sign In</h4></div>',unsafe_allow_html=True)
            with st.form("alf"):
                u=st.text_input("Username"); pw=st.text_input("Password",type="password")
                ok=st.form_submit_button("Sign In",use_container_width=True)
            if ok:
                if u==ADMIN_USERNAME and pw==ADMIN_PASSWORD:
                    st.session_state.admin_logged_in=True; st.session_state.show_admin_login=False; st.rerun()
                else: st.error("Incorrect credentials.")

def get_pages():
    pub=["Home","Risk Analysis","Fuel Efficiency","Emissions Analysis","Aircraft Explorer","Scenario History","Ethics & Implications"]
    return pub+["Route Planner","Testing & Evaluation"] if st.session_state.admin_logged_in else pub

def render_nav(pages):
    return st.radio("Navigation",pages,horizontal=True,label_visibility="collapsed")


# ================================================================
# HOME  — Route Planner removed, now just noted as admin-only in data sources
