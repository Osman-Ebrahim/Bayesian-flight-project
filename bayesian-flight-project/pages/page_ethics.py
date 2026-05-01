# pages/page_ethics.py
import streamlit as st

def page_ethics():
    st.title("Ethics & Professional Implications")
    st.markdown('<div class="glass-card">Addresses <b>Objective 7</b>: ethical and professional implications of AI-driven decision-support in aviation. Covers BCS Code of Conduct, GDPR, EU AI Act, and DO-178C.</div>',unsafe_allow_html=True)
    sections=[
        ("1. Transparency & Explainability","Why it matters in aviation AI",
         "Aviation is safety-critical. The Naive Bayes classifier in this system exposes its full reasoning through log-posterior probabilities. Every prediction shows the exact posterior for each risk class and contributing factors, satisfying the <b>BCS Code of Conduct</b> principle of transparency. A real deployment would require DO-178C certification and regulatory approval before any operational use."),
        ("2. Data Bias & Fairness","NTSB dataset and representational bias",
         "The NTSB dataset predominantly records <b>US domestic accidents</b>. This creates geographic bias — likelihoods may not generalise to European, African, or Asian aviation contexts. Aircraft age (engine type proxy) may not reflect maintenance culture differences across airlines. Mitigation: Laplace smoothing prevents zero-probability predictions; limitations are explicitly documented."),
        ("3. Accountability & Liability","Who is responsible when AI advises on flight safety?",
         "The <b>EU AI Act (2024)</b> classifies aviation AI as <b>high-risk</b>, requiring conformity assessments and human oversight. This prototype has not undergone DO-178C software certification or EASA CS-25 airworthiness review. It is explicitly labelled as advisory-only with no operational connectivity or autonomous decision capability."),
        ("4. Conflict Zone Intelligence","Use of EASA CZIB data in routing",
         "The Route Planner uses <b>EASA Conflict Zone Information Bulletins (CZIBs)</b> — the same advisories used by all European-certificated airlines. Current closures (Iran, Iraq, Syria, Israel, Ukraine as of CZIB 2026-03-R5) are hardcoded with polygons drawn on the Folium map. This is academically citable and more rigorous than commercial APIs for a research prototype."),
        ("5. Privacy & Data Governance","GDPR and OpenSky flightlist data",
         "OpenSky callsigns can in some cases identify aircraft operators. Under <b>GDPR Article 4</b>, this may constitute personal data. This prototype uses only aggregated route statistics; no individual callsigns are stored. A production system would require a DPIA under GDPR Article 35."),
        ("6. Environmental Responsibility","Aviation's climate impact",
         "Aviation accounts for ≈2.5% of global CO₂ emissions and ≈3.5% of effective radiative forcing (Lee et al., 2021). The fuel efficiency and emissions modules make environmental cost visible. <b>Non-CO₂ effects</b> (contrails, NOₓ) are not modelled — a production system should include these. This aligns with the BCS public interest duty."),
        ("7. Professional Standards","BCS Code of Conduct alignment",
         "<b>Public interest:</b> Risk, fuel efficiency, and emissions outputs serve safer/sustainable aviation.<br><b>Competence:</b> All sources cited, limitations documented, no overclaiming.<br><b>Duty to profession:</b> Advances Bayesian methods in safety-critical AI.<br><b>Relevant authority:</b> EASA, FAA, ICAO, EU AI Act frameworks acknowledged."),
    ]
    for title,subtitle,body in sections:
        st.subheader(title)
        st.markdown(f'<div class="ethics-card"><h4>{subtitle}</h4><p>{body}</p></div>',unsafe_allow_html=True)

    st.subheader("8. Ethical Risk Assessment")
    rows=[("Data bias (US-centric NTSB)","Medium","Documented; Laplace smoothing; prototype label"),
          ("Overreliance on model output","High","Disclaimer on every page; advisory-only framing"),
          ("Lack of DO-178C certification","High","Explicitly not an operational system"),
          ("Privacy (OpenSky callsigns)","Medium","No callsigns stored; aggregated stats only"),
          ("Incomplete environmental model","Medium","CO₂ only; contrails/NOₓ limitation stated"),
          ("Conflict zone data currency","Medium","EASA CZIBs hardcoded — require manual update for new NOTAMs"),
          ("EU AI Act accountability gap","High","Human-in-the-loop; no autonomous capability"),]
    row_html="".join(f'<tr style="border-bottom:1px solid rgba(148,163,184,.1);"><td style="padding:.6rem;color:#e5e7eb;">{r}</td><td style="padding:.6rem;color:{"#ef4444" if s=="High" else ("#f59e0b" if s=="Medium" else "#22c55e")};">{s}</td><td style="padding:.6rem;color:#e5e7eb;">{m}</td></tr>' for r,s,m in rows)
    st.markdown(f'<div class="glass-card"><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:1px solid rgba(148,163,184,.3);"><th style="text-align:left;padding:.6rem;color:#93c5fd;">Risk</th><th style="text-align:left;padding:.6rem;color:#93c5fd;">Severity</th><th style="text-align:left;padding:.6rem;color:#93c5fd;">Mitigation</th></tr></thead><tbody>{row_html}</tbody></table></div>',unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="border-left:3px solid #3b82f6;">
        <b>References</b><br>
        <span style="color:#94a3b8;font-size:.88rem;">
        • BCS Code of Conduct (2022). British Computer Society.<br>
        • EU Artificial Intelligence Act (2024). European Parliament Regulation 2024/1689.<br>
        • EASA CZIB 2026-03-R5 (28 Feb 2026). Conflict Zone Information Bulletin — Middle East.<br>
        • ICAO Annex 19 — Safety Management Systems (3rd Ed., 2023).<br>
        • Lee, D.S. et al. (2021). The contribution of global aviation to anthropogenic climate forcing. <em>Atmospheric Environment</em>, 244.<br>
        • RTCA DO-178C (2011). Software Considerations in Airborne Systems and Equipment Certification.<br>
        • GDPR Articles 4 &amp; 35 (2018). EU General Data Protection Regulation.
        </span>
    </div>""", unsafe_allow_html=True)


# ================================================================
# TESTING & EVALUATION
# ================================================================
