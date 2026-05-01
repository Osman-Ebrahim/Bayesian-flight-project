# pages/page_risk.py
import streamlit as st
from models.globals import risk_model, AC_LIST_SHORT, risk_colour, add_history
from data.aircraft import AIRCRAFT_CATALOGUE

from utils.api_client import (lookup_flight,_iata_to_aircraft_key,
    _map_status_to_congestion,_distance_from_airport_codes,
    _route_complexity_from_distance)

def page_risk():
    st.title("Risk Analysis")
    src = (f"<span class='live-badge'>NTSB · {risk_model.n_training:,} records</span>"
           if risk_model.trained_on_data else "<span class='proto-badge'>Prototype</span>")
    st.markdown(f'''<div class="glass-card">
        <b>Unified Bayesian Model</b> — estimates both accident probability AND expected CO₂
        in a single inference pass. {src}<br>
        <code>log P(C|X) = log P(C) + Σ log P(xᵢ|C)</code> &nbsp;·&nbsp;
        <code>CO₂_expected = Σ P(C|X) × base_CO₂ × overhead(C)</code><br>
        <span style="color:#94a3b8;font-size:.87rem;">
        Risk-weighted emissions account for the extra fuel burned during holding
        patterns, diversions, and emergency procedures in higher-risk scenarios.
        </span>
    </div>''', unsafe_allow_html=True)

    # ── Input mode toggle
    input_mode = st.radio(
        "How would you like to enter flight details?",
        ["Enter a Flight Number (e.g. BA249, EK002)", "Enter Details Manually"],
        horizontal=True,
    )

    # ── Default values — restore from session_state if a flight was looked up
    prefill = {
        "aircraft": "A320", "distance_km": 2500,
        "weather": "low", "maintenance": "good", "age": "new",
        "complexity": "low", "congestion": "low",
        "flight_info": None,
    }
    # If a previous lookup succeeded, auto-apply its values to prefill
    if "flight_prefill" in st.session_state:
        _fp = st.session_state["flight_prefill"]
        _ac = _iata_to_aircraft_key(_fp.get("aircraft_type",""))
        _delay = int(_fp.get("dep_delay",0) or 0)
        _status = _fp.get("status","") or ""
        # Auto-calculate real distance — works with IATA codes (LHR, DOH) from API
        _real_dist = _distance_from_airport_codes(
            _fp.get("origin_iata",""), _fp.get("dest_iata","")
        )
        prefill["aircraft"]    = _ac
        prefill["congestion"]  = _map_status_to_congestion(_status, _delay)
        prefill["flight_info"] = _fp
        if _real_dist:
            prefill["distance_km"] = _real_dist
            # Auto-set route complexity based on distance
            prefill["complexity"]  = _route_complexity_from_distance(_real_dist)
        elif _delay > 30:
            prefill["complexity"] = "high"

    # Hardcoded API key (100 free calls/month on this project account)
    _AVSTACK_KEY = "3688b076ea335a772a99c7f75225a5ad"
    _API_EXHAUSTED = False   # flip to True manually if quota runs out

    if "Enter a Flight Number" in input_mode:
        if _API_EXHAUSTED:
            st.markdown('''<div class="glass-card" style="border-left:3px solid #ef4444;">
                <b>⚠ Flight lookup quota reached for this month</b><br>
                <span style="color:#94a3b8;">
                The 100 free monthly API calls for this prototype have been used up.
                You can still use the <b>Enter Details Manually</b> option, or generate
                your own free key at
                <a href="https://aviationstack.com" target="_blank" style="color:#60a5fa;">aviationstack.com</a>
                and paste it below. The quota resets at the start of each month.
                </span>
            </div>''', unsafe_allow_html=True)
            # Allow power users to paste their own key
            own_key = st.text_input("Your AviationStack key (optional)", type="password",
                                    placeholder="Paste your own key to continue…")
            _AVSTACK_KEY = own_key if own_key.strip() else ""
        else:
            st.markdown('''<div class="glass-card" style="border-left:3px solid #22c55e;">
                <b>✈ Real-Time Flight Lookup</b><br>
                <span style="color:#94a3b8;font-size:.87rem;">
                Enter any IATA flight number (e.g. <b>BA249</b>, <b>EK002</b>, <b>QR8</b>)
                and the system will automatically fetch the route, aircraft type, and
                current status to pre-fill the risk analysis form.
                Powered by AviationStack — live data updated every 30–60 seconds.
                </span>
            </div>''', unsafe_allow_html=True)

        flight_num = st.text_input("Flight Number", placeholder="e.g. BA249, EK002, QR8, LH400")

        if st.button("Look Up Flight", use_container_width=False):
            if not flight_num.strip():
                st.error("Please enter a flight number.")
            elif not _AVSTACK_KEY:
                st.error("No API key available. Please use manual entry or paste your own key.")
            else:
                with st.spinner(f"Looking up {flight_num.strip().upper()}…"):
                    info = lookup_flight(flight_num, _AVSTACK_KEY)
                if info is None:
                    st.warning(
                        f"Flight **{flight_num.strip().upper()}** not found. "
                        "It may not be operating today, or try a different format (e.g. BA0249). "
                        "You can still enter details manually below."
                    )
                else:
                    st.session_state["flight_prefill"] = info
                    st.rerun()   # rerun so prefill card + form render immediately

        # Show fetched flight card if available
        if "flight_prefill" in st.session_state:
            info = st.session_state["flight_prefill"]
            ac_key = _iata_to_aircraft_key(info.get("aircraft_type",""))
            delay  = int(info.get("dep_delay", 0) or 0)
            status = info.get("status","") or ""
            cong   = _map_status_to_congestion(status, delay)

            delay_str = f"+{delay} min delay" if delay > 0 else "On time"
            status_col = "#ef4444" if status in ("cancelled","diverted") else ("#f59e0b" if delay > 20 else "#22c55e")

            st.markdown(f'''<div class="glass-card" style="border-left:3px solid #3b82f6;">
                <b>✈ {info["flight_iata"]}</b> — {info["airline"]}<br>
                <b>Route:</b> {info["origin_name"]} ({info["origin_iata"]})
                → {info["dest_name"]} ({info["dest_iata"]})<br>
                <b>Aircraft:</b> {info["aircraft_type"] or "Unknown"} → mapped to <b>{ac_key}</b><br>
                <b>Route:</b> {_distance_from_airport_codes(info.get("origin_iata",""), info.get("dest_iata","")) or "⚠ airport not in local database"} km (auto-calculated · {info.get("origin_iata","")}→{info.get("dest_iata","")})<br>
                <b>Status:</b> <span style="color:{status_col};font-weight:700;">{status.title()}</span>
                · <b>Departure:</b> {delay_str}<br>
                <span style="color:#94a3b8;font-size:.85rem;">
                Aircraft type, status, delay, and <b>route distance auto-calculated</b>
                from airport coordinates. Route complexity set from distance.
                You can adjust any field below before running the analysis.
                </span>
            </div>''', unsafe_allow_html=True)

            prefill["aircraft"]   = ac_key
            prefill["congestion"] = cong
            prefill["flight_info"] = info
            if delay > 30:
                prefill["complexity"] = "high"

        st.markdown("---")
        if "flight_prefill" in st.session_state:
            if st.button("Clear / search a different flight"):
                del st.session_state["flight_prefill"]
                st.rerun()
        st.markdown("**Review or adjust the auto-filled parameters:**")

    # ── Main analysis form (always shown)
    with st.form("rf"):
        c1, c2 = st.columns(2)
        with c1:
            _pf_ac = prefill.get("aircraft","A320")
            _ac_idx = AC_LIST_SHORT.index(_pf_ac) if _pf_ac in AC_LIST_SHORT else 0
            ac = st.selectbox("Aircraft Type", AC_LIST_SHORT, index=_ac_idx)
            km = st.number_input("Route Distance (km)", 100, 20000,
                                 prefill["distance_km"], 100)
            weather     = st.selectbox("Weather Severity",
                                       ["low","medium","high"],
                                       index=["low","medium","high"].index(prefill.get("weather","low")) if prefill.get("weather","low") in ["low","medium","high"] else 0)
            maintenance = st.selectbox("Maintenance Status",
                                       ["good","fair","poor"],
                                       index=["good","fair","poor"].index(prefill.get("maintenance","good")) if prefill.get("maintenance","good") in ["good","fair","poor"] else 0)
        with c2:
            age         = st.selectbox("Aircraft Age", ["new","mid","old"],
                                       index=["new","mid","old"].index(prefill.get("age","new")) if prefill.get("age","new") in ["new","mid","old"] else 0)
            complexity  = st.selectbox("Route Complexity", ["low","medium","high"],
                                       index=["low","medium","high"].index(prefill.get("complexity","low")) if prefill.get("complexity","low") in ["low","medium","high"] else 0)
            congestion  = st.selectbox("Traffic Congestion", ["low","medium","high"],
                                       index=["low","medium","high"].index(prefill.get("congestion","low")) if prefill.get("congestion","low") in ["low","medium","high"] else 0)
        sub = st.form_submit_button("Run Unified Analysis")

    if sub:
        inputs = {
            "weather": weather, "maintenance": maintenance,
            "aircraft_age": age, "route_complexity": complexity,
            "congestion": congestion,
        }
        # Single unified call — returns BOTH risk and emissions
        res = risk_model.predict(inputs, aircraft=ac, distance_km=km)

        add_history({
            "Type":         "Unified Analysis",
            "Aircraft":     ac,
            "Distance (km)": km,
            "Risk Class":   res["class"],
            "Risk Score":   res["score"],
            "CO2 (kg)":     res["expected_co2"],
        })

        # ── Unified output header
        st.markdown("## Unified Model Output")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Risk Category",    res["class"])
        m2.metric("Risk Score",       f"{res['score']}/100")
        m3.metric("Expected CO₂",     f"{res['expected_co2']:,.0f} kg")
        m4.metric("CO₂ Risk Overhead",f"+{res['co2_risk_overhead']:,.0f} kg")

        # Dual badge — risk + emissions side by side
        rc_col = risk_colour(res["class"])
        st.markdown(f'''
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:.75rem 0;">
            <div style="padding:12px 20px;border-radius:14px;background:{rc_col};
                        color:white;font-weight:bold;box-shadow:0 12px 24px rgba(0,0,0,.18);">
                ⚠ {res["class"]} Operational Risk
            </div>
            <div style="padding:12px 20px;border-radius:14px;background:{res["em_colour"]};
                        color:white;font-weight:bold;box-shadow:0 12px 24px rgba(0,0,0,.18);">
                🌿 {res["em_level"]} Emission Level
            </div>
        </div>''', unsafe_allow_html=True)

        # ── How the unified model works
        st.markdown('''<div class="glass-card" style="border-left:3px solid #3b82f6;">
            <b>How the Unified Model Works</b><br>
            <span style="color:#e5e7eb;">
            The Bayesian posteriors P(Low|X), P(Medium|X), P(High|X) are computed first.
            These same probabilities then weight the emissions estimate:<br><br>
            <code>CO₂_expected = Σ P(class|features) × base_CO₂ × overhead(class)</code><br><br>
            Overhead factors: Low=×1.00 · Medium=×1.05 · High=×1.14<br>
            (Based on ICAO contingency fuel studies — higher-risk operations require
            more fuel for holding, diversions, and emergency procedures.)
            </span>
        </div>''', unsafe_allow_html=True)

        # ── Risk posteriors
        st.subheader("Risk Posteriors")
        st.caption("log P(C|X) = log P(C) + Σ log P(xᵢ|C) — trained on NTSB data")
        for lbl, key in [("Low Risk","Low"),("Medium Risk","Medium"),("High Risk","High")]:
            p = res["probabilities"][key]
            st.write(f"{lbl}: **{p*100:.2f}%**")
            st.progress(p)

        # ── Emissions breakdown
        st.subheader("Unified Emissions Estimate")
        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Baseline CO₂",       f"{res['base_co2']:,.0f} kg",
                   help="EASA EDB v31 factor × distance, no risk adjustment")
        ec2.metric("Risk-Adjusted CO₂",  f"{res['expected_co2']:,.0f} kg",
                   help="Bayesian-weighted: accounts for extra fuel in non-normal ops")
        ec3.metric("Risk Overhead",       f"+{res['co2_risk_overhead']:,.0f} kg",
                   help="Extra CO₂ attributable to the risk level of this flight")

        st.markdown(f'''<div class="glass-card">
            🚗 ≈ <b>{res["cars_equivalent"]:,} years</b> of UK car driving &nbsp;·&nbsp;
            🌳 ≈ <b>{res["trees_equivalent"]:,} trees</b> needed for one year<br>
            <b>CO₂ Factor (EASA EDB v31):</b> {res["co2_factor"]} kg/km for {ac}
        </div>''', unsafe_allow_html=True)

        # ── Explanation
        st.subheader("Interpretation")
        st.markdown(f'<div class="glass-card">{res["explanation"]}</div>',
                    unsafe_allow_html=True)

        with st.expander("View Bayesian Computation Detail", expanded=False):
            st.caption("Full log-posterior values before normalisation:")
            for cls, lp in res["log_posteriors"].items():
                st.write(f"**{cls}**: log P = `{lp:.4f}` "
                         f"→ posterior = `{res['probabilities'][cls]*100:.2f}%`"
                         f" → CO₂ contribution: `{res['probabilities'][cls]*res['base_co2']*risk_model.CO2_OVERHEAD[cls]:,.0f} kg`")
            note = (f"Trained on {risk_model.n_training:,} NTSB records with Laplace smoothing α=1."
                    if risk_model.trained_on_data else "Prototype likelihoods.")
            st.caption(note)

        # ── Scenario summary
        fi = prefill.get("flight_info")
        st.subheader("Scenario Summary")
        fn_str = f"<b>Flight:</b> {fi['flight_iata']} ({fi['airline']})<br>" if fi else ""
        st.markdown(f'''<div class="glass-card">
            {fn_str}
            <b>Aircraft:</b> {ac} &nbsp;·&nbsp; <b>Distance:</b> {km:,} km<br>
            <b>Weather:</b> {weather} &nbsp;·&nbsp; <b>Maintenance:</b> {maintenance}<br>
            <b>Age:</b> {age} &nbsp;·&nbsp; <b>Complexity:</b> {complexity} &nbsp;·&nbsp;
            <b>Congestion:</b> {congestion}
        </div>''', unsafe_allow_html=True)


# ================================================================
# FUEL EFFICIENCY
# ================================================================
