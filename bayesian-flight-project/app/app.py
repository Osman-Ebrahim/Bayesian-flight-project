"""
Bayesian Aviation Decision-Support System
BSc Computer Science Final Year Project — Osman Ebrahim, 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import math, os, gzip, glob
import folium
import streamlit.components.v1 as components
from io import BytesIO

st.set_page_config(page_title="Bayesian Flight Project", layout="wide")

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
# ================================================================
def _find_data_raw():
    here = os.path.abspath(os.path.dirname(__file__))
    for candidate in [here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))]:
        p = os.path.join(candidate, "data", "raw")
        if os.path.isdir(p):
            return p
    return os.path.join(os.getcwd(), "data", "raw")

DATA_RAW     = _find_data_raw()
AVIATION_CSV = os.path.join(DATA_RAW, "archive", "AviationData.csv")
NTSB_CSV     = os.path.join(DATA_RAW, "archive", "NTSB_database.csv")
FLIGHT_GLOB  = os.path.join(DATA_RAW, "flightlist_*.csv")


# ================================================================
# CSS
# ================================================================
st.markdown("""
<style>
header{visibility:hidden;}footer{visibility:hidden;}
.stApp{background:linear-gradient(180deg,rgba(15,23,42,.96) 0%,rgba(10,15,26,.98) 100%);color:#f8fafc;}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;
    background:radial-gradient(circle at 12% 18%,rgba(59,130,246,.10),transparent 22%),
               radial-gradient(circle at 85% 8%,rgba(168,85,247,.08),transparent 20%),
               radial-gradient(circle at 50% 85%,rgba(14,165,233,.06),transparent 18%);z-index:0;}
.block-container{position:relative;z-index:1;max-width:100%;
    padding-top:.8rem!important;padding-bottom:2rem!important;
    padding-left:3rem!important;padding-right:3rem!important;}
html,body,[class*="css"],[class*="st-"]{font-family:"Inter","Segoe UI",sans-serif!important;}
h1,h2,h3,h4,h5,h6{color:#fff!important;letter-spacing:-.02em;font-weight:700!important;
    margin-top:.5rem!important;margin-bottom:.5rem!important;}
p,li,label,span,div{color:#e5e7eb;}
div[role="radiogroup"]{display:flex;justify-content:center;gap:1.2rem;padding:1.2rem 0 2rem 0;flex-wrap:wrap;}
div[role="radiogroup"] label{background:rgba(17,24,39,.95)!important;color:#fff!important;
    padding:.9rem 1.5rem!important;border-radius:16px!important;
    border:1px solid rgba(148,163,184,.2)!important;box-shadow:0 10px 24px rgba(0,0,0,.25);
    transition:all .25s ease!important;backdrop-filter:blur(10px);font-size:.95rem;}
div[role="radiogroup"] label:hover{transform:translateY(-3px) scale(1.05);
    background:linear-gradient(135deg,#2563eb,#7c3aed)!important;
    border:1px solid rgba(255,255,255,.22)!important;box-shadow:0 14px 28px rgba(37,99,235,.22);}
[data-testid="stMetric"]{background:rgba(15,23,42,.96);border:1px solid rgba(148,163,184,.16);
    padding:1rem;border-radius:18px;box-shadow:0 12px 28px rgba(0,0,0,.18);}
[data-testid="stMetricLabel"]{color:#cbd5e1!important;font-weight:600!important;}
[data-testid="stMetricValue"]{color:#fff!important;font-weight:800!important;}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:14px!important;
    padding:.7rem 1.25rem!important;background:linear-gradient(135deg,#2563eb,#7c3aed)!important;
    color:#fff!important;font-weight:700!important;border:1px solid rgba(255,255,255,.10)!important;
    box-shadow:0 12px 28px rgba(37,99,235,.20);transition:all .2s ease!important;}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover{
    transform:translateY(-2px);box-shadow:0 16px 34px rgba(124,58,237,.22);}
.stSelectbox{margin-bottom:1rem;}
.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextInput>div>div>input{
    background:rgba(15,23,42,.96)!important;border:1px solid rgba(148,163,184,.18)!important;
    color:#fff!important;border-radius:14px!important;}
/* ── Dropdown / Select — closed state: dark bg, white text ── */
div[data-baseweb="select"]{
    background:rgba(15,23,42,.98)!important;
    color:#f8fafc!important;
}
/* Every span/div inside the closed selector — white text */
div[data-baseweb="select"] *{color:#f8fafc!important;}
/* Override back to dark on the open list (below) */
div[data-baseweb="select"] input{
    color:#f8fafc!important;
    background:transparent!important;
    caret-color:#f8fafc!important;
}
/* ── Open dropdown list — WHITE background, NAVY text ── */
ul[role="listbox"],
div[role="listbox"],
[data-baseweb="menu"],
[data-baseweb="popover"] ul,
[data-baseweb="popover"] [role="listbox"]{
    background:#ffffff!important;
    border-radius:10px!important;
    border:1px solid #cbd5e1!important;
    box-shadow:0 8px 28px rgba(0,0,0,.22)!important;
    padding:4px 0!important;
}
/* Every list item — navy text, white background */
ul[role="listbox"] li,
div[role="listbox"] div[role="option"],
[data-baseweb="menu"] [role="option"],
[data-baseweb="popover"] [role="option"],
li[role="option"]{
    color:#0f172a!important;
    background:#ffffff!important;
    font-weight:500!important;
    font-size:.92rem!important;
}
/* Hover and selected state — teal highlight */
ul[role="listbox"] li:hover,
div[role="listbox"] div[role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
li[role="option"]:hover,
li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"]{
    background:#0e7490!important;
    color:#ffffff!important;
}
/* Catch all text nodes inside options */
ul[role="listbox"] li *,
li[role="option"] *,
div[role="option"] *{
    color:inherit!important;
}
/* Also target the number input specifically */
.stNumberInput>div>div>input{
    background:rgba(15,23,42,.96)!important;
    border:1px solid rgba(148,163,184,.18)!important;
    color:#f8fafc!important;
    border-radius:14px!important;
}
label[data-testid="stWidgetLabel"] p{color:#f8fafc!important;font-weight:600!important;}
[data-testid="stAlert"]{border-radius:16px!important;background:rgba(15,23,42,.94)!important;
    border:1px solid rgba(148,163,184,.16)!important;color:#fff!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,#22c55e,#3b82f6,#8b5cf6)!important;}
.glass-card{padding:1.15rem 1.2rem;border-radius:20px;background:rgba(15,23,42,.95);
    border:1px solid rgba(148,163,184,.15);box-shadow:0 12px 30px rgba(0,0,0,.20);
    color:#f8fafc!important;backdrop-filter:blur(10px);margin-bottom:1rem;}
.glass-card h3,.glass-card h4,.glass-card b{color:#fff!important;}
.glass-card p,.glass-card span,.glass-card div{color:#e5e7eb!important;}
.hero-card{padding:2.25rem;border-radius:24px;
    background:linear-gradient(135deg,rgba(15,23,42,.98),rgba(30,41,59,.96),rgba(30,64,175,.88));
    color:white;margin-bottom:1.6rem;border:1px solid rgba(255,255,255,.08);
    box-shadow:0 20px 46px rgba(0,0,0,.26);}
.hero-card h1{color:#fff!important;margin-bottom:.55rem;font-size:2.4rem;}
.hero-card p{color:#f1f5f9!important;font-size:1.08rem;line-height:1.7;max-width:920px;}
hr{border:none;height:1px;background:rgba(148,163,184,.14);}
.auth-card{padding:2rem 2.2rem;border-radius:22px;background:rgba(15,23,42,.97);
    border:1px solid rgba(148,163,184,.18);box-shadow:0 20px 50px rgba(0,0,0,.30);backdrop-filter:blur(12px);}
.admin-badge{display:inline-block;padding:.2rem .8rem;border-radius:100px;font-size:.75rem;
    font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-left:.5rem;vertical-align:middle;
    background:rgba(168,85,247,.2);color:#c084fc;border:1px solid rgba(168,85,247,.35);}
.live-badge{display:inline-block;padding:.18rem .7rem;border-radius:100px;font-size:.7rem;
    font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-left:.5rem;
    background:rgba(34,197,94,.15);color:#22c55e;border:1px solid rgba(34,197,94,.3);}
.proto-badge{display:inline-block;padding:.18rem .7rem;border-radius:100px;font-size:.7rem;
    font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-left:.5rem;
    background:rgba(245,158,11,.15);color:#f59e0b;border:1px solid rgba(245,158,11,.3);}
.warn-badge{display:inline-block;padding:.18rem .7rem;border-radius:100px;font-size:.7rem;
    font-weight:700;text-transform:uppercase;letter-spacing:.05em;
    background:rgba(239,68,68,.15);color:#ef4444;border:1px solid rgba(239,68,68,.3);}
.ethics-card{padding:1.4rem 1.6rem;border-radius:18px;background:rgba(15,23,42,.95);
    border-left:4px solid #3b82f6;margin-bottom:1rem;box-shadow:0 8px 24px rgba(0,0,0,.18);}
.ethics-card h4{color:#93c5fd!important;margin-top:0!important;}
.ethics-card p,.ethics-card span{color:#cbd5e1!important;}
/* ── Expander: targeted fix for overlapping label text ── */
/* Outer shell */
[data-testid="stExpander"]{
    background:rgba(17,24,39,.92)!important;
    border:1px solid rgba(148,163,184,.18)!important;
    border-radius:14px!important;
    margin-bottom:.9rem!important;
}
/* The summary (label) element — stop glass-card p/div/span rules cascading in */
[data-testid="stExpander"] summary {
    background:rgba(17,24,39,.92)!important;
    border-radius:14px!important;
    padding:.65rem 1.4rem!important;
    border:none!important;
    box-shadow:none!important;
    cursor:pointer!important;
}
/* The <p> Streamlit puts inside summary for the label text */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary div {
    color:#f1f5f9!important;
    font-size:.93rem!important;
    font-weight:600!important;
    line-height:1.4!important;
    background:transparent!important;
    border:none!important;
    box-shadow:none!important;
    padding:0!important;
    margin:0!important;
    border-radius:0!important;
    display:inline!important;
}
[data-testid="stExpander"] summary:hover {
    background:rgba(37,99,235,.12)!important;
}
/* Expander body — strip glass-card overrides */
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background:transparent!important;
    border:none!important;
    box-shadow:none!important;
    padding:.5rem .6rem!important;
    border-radius:0 0 14px 14px!important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] > div,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] > div > div {
    background:transparent!important;
    border:none!important;
    box-shadow:none!important;
    padding:0!important;
    margin:0!important;
    border-radius:0!important;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# EXPANDED AIRPORTS — major global hubs
# ================================================================
AIRPORTS = {
    # ════════════════════════════════════════════════════════
    # UNITED KINGDOM
    # ════════════════════════════════════════════════════════
    "London Heathrow (LHR)":            {"coords":(51.4700,-0.4543),  "country":"United Kingdom","icao":"EGLL"},
    "London Gatwick (LGW)":             {"coords":(51.1481,-0.1903),  "country":"United Kingdom","icao":"EGKK"},
    "London Stansted (STN)":            {"coords":(51.8850, 0.2350),  "country":"United Kingdom","icao":"EGSS"},
    "London Luton (LTN)":               {"coords":(51.8747,-0.3683),  "country":"United Kingdom","icao":"EGGW"},
    "London City (LCY)":                {"coords":(51.5048, 0.0495),  "country":"United Kingdom","icao":"EGLC"},
    "Manchester (MAN)":                 {"coords":(53.3537,-2.2750),  "country":"United Kingdom","icao":"EGCC"},
    "Birmingham (BHX)":                 {"coords":(52.4539,-1.7480),  "country":"United Kingdom","icao":"EGBB"},
    "Edinburgh (EDI)":                  {"coords":(55.9500,-3.3725),  "country":"United Kingdom","icao":"EGPH"},
    "Glasgow (GLA)":                    {"coords":(55.8719,-4.4330),  "country":"United Kingdom","icao":"EGPF"},
    "Bristol (BRS)":                    {"coords":(51.3827,-2.7191),  "country":"United Kingdom","icao":"EGGD"},
    "Newcastle (NCL)":                  {"coords":(55.0375,-1.6917),  "country":"United Kingdom","icao":"EGNT"},
    "Leeds Bradford (LBA)":             {"coords":(53.8659,-1.6606),  "country":"United Kingdom","icao":"EGNM"},
    "Belfast International (BFS)":      {"coords":(54.6575,-6.2158),  "country":"United Kingdom","icao":"EGAA"},
    "Aberdeen (ABZ)":                   {"coords":(57.2019,-2.1978),  "country":"United Kingdom","icao":"EGPD"},
    "Liverpool (LPL)":                  {"coords":(53.3336,-2.8497),  "country":"United Kingdom","icao":"EGGP"},
    "East Midlands (EMA)":              {"coords":(52.8311,-1.3281),  "country":"United Kingdom","icao":"EGNX"},
    "Southampton (SOU)":                {"coords":(50.9503,-1.3568),  "country":"United Kingdom","icao":"EGHI"},
    "Cardiff (CWL)":                    {"coords":(51.3967,-3.3433),  "country":"United Kingdom","icao":"EGFF"},
    "Inverness (INV)":                  {"coords":(57.5425,-4.0475),  "country":"United Kingdom","icao":"EGPE"},
    # ════════════════════════════════════════════════════════
    # IRELAND
    # ════════════════════════════════════════════════════════
    "Dublin (DUB)":                     {"coords":(53.4213,-6.2700),  "country":"Ireland","icao":"EIDW"},
    "Shannon (SNN)":                    {"coords":(52.7020,-8.9248),  "country":"Ireland","icao":"EINN"},
    "Cork (ORK)":                       {"coords":(51.8413,-8.4911),  "country":"Ireland","icao":"EICK"},
    "Knock (NOC)":                      {"coords":(53.9103,-8.8186),  "country":"Ireland","icao":"EIKN"},
    # ════════════════════════════════════════════════════════
    # FRANCE
    # ════════════════════════════════════════════════════════
    "Paris CDG (CDG)":                  {"coords":(49.0097, 2.5479),  "country":"France","icao":"LFPG"},
    "Paris Orly (ORY)":                 {"coords":(48.7233, 2.3794),  "country":"France","icao":"LFPO"},
    "Nice (NCE)":                       {"coords":(43.6584, 7.2159),  "country":"France","icao":"LFMN"},
    "Lyon (LYS)":                       {"coords":(45.7256, 5.0811),  "country":"France","icao":"LFLL"},
    "Marseille (MRS)":                  {"coords":(43.4393, 5.2214),  "country":"France","icao":"LFML"},
    "Bordeaux (BOD)":                   {"coords":(44.8283,-0.7156),  "country":"France","icao":"LFBD"},
    "Toulouse (TLS)":                   {"coords":(43.6293, 1.3638),  "country":"France","icao":"LFBO"},
    "Strasbourg (SXB)":                 {"coords":(48.5383, 7.6283),  "country":"France","icao":"LFST"},
    "Nantes (NTE)":                     {"coords":(47.1532,-1.6108),  "country":"France","icao":"LFRS"},
    "Montpellier (MPL)":                {"coords":(43.5762, 3.9630),  "country":"France","icao":"LFMT"},
    "Rennes (RNS)":                     {"coords":(48.0694,-1.7348),  "country":"France","icao":"LFRN"},
    "Brest (BES)":                      {"coords":(48.4479,-4.4183),  "country":"France","icao":"LFRB"},
    "Ajaccio (AJA)":                    {"coords":(41.9236, 8.8028),  "country":"France","icao":"LFKJ"},
    # ════════════════════════════════════════════════════════
    # GERMANY
    # ════════════════════════════════════════════════════════
    "Frankfurt (FRA)":                  {"coords":(50.0379, 8.5622),  "country":"Germany","icao":"EDDF"},
    "Munich (MUC)":                     {"coords":(48.3537,11.7750),  "country":"Germany","icao":"EDDM"},
    "Berlin Brandenburg (BER)":         {"coords":(52.3514,13.4939),  "country":"Germany","icao":"EDDB"},
    "Hamburg (HAM)":                    {"coords":(53.6304, 9.9882),  "country":"Germany","icao":"EDDH"},
    "Dusseldorf (DUS)":                 {"coords":(51.2895, 6.7668),  "country":"Germany","icao":"EDDL"},
    "Cologne Bonn (CGN)":               {"coords":(50.8659, 7.1427),  "country":"Germany","icao":"EDDK"},
    "Stuttgart (STR)":                  {"coords":(48.6899, 9.2219),  "country":"Germany","icao":"EDDS"},
    "Hanover (HAJ)":                    {"coords":(52.4611, 9.6850),  "country":"Germany","icao":"EDDV"},
    "Nuremberg (NUE)":                  {"coords":(49.4987,11.0669),  "country":"Germany","icao":"EDDN"},
    "Leipzig (LEJ)":                    {"coords":(51.4239,12.2364),  "country":"Germany","icao":"EDDP"},
    "Bremen (BRE)":                     {"coords":(53.0475, 8.7869),  "country":"Germany","icao":"EDDW"},
    "Dresden (DRS)":                    {"coords":(51.1328,13.7672),  "country":"Germany","icao":"EDDC"},
    # ════════════════════════════════════════════════════════
    # SPAIN
    # ════════════════════════════════════════════════════════
    "Madrid Barajas (MAD)":             {"coords":(40.4719,-3.5626),  "country":"Spain","icao":"LEMD"},
    "Barcelona (BCN)":                  {"coords":(41.2971, 2.0785),  "country":"Spain","icao":"LEBL"},
    "Palma Mallorca (PMI)":             {"coords":(39.5517, 2.7388),  "country":"Spain","icao":"LEPA"},
    "Malaga (AGP)":                     {"coords":(36.6749,-4.4991),  "country":"Spain","icao":"LEMG"},
    "Alicante (ALC)":                   {"coords":(38.2822,-0.5582),  "country":"Spain","icao":"LEAL"},
    "Valencia (VLC)":                   {"coords":(39.4893,-0.4816),  "country":"Spain","icao":"LEVC"},
    "Seville (SVQ)":                    {"coords":(37.4180,-5.8931),  "country":"Spain","icao":"LEZL"},
    "Bilbao (BIO)":                     {"coords":(43.3011,-2.9106),  "country":"Spain","icao":"LEBB"},
    "Gran Canaria (LPA)":               {"coords":(27.9319,-15.3866), "country":"Spain","icao":"GCLP"},
    "Tenerife South (TFS)":             {"coords":(28.0445,-16.5725), "country":"Spain","icao":"GCTS"},
    "Tenerife North (TFN)":             {"coords":(28.4827,-16.3414), "country":"Spain","icao":"GCXO"},
    "Lanzarote (ACE)":                  {"coords":(28.9455,-13.6052), "country":"Spain","icao":"GCRR"},
    "Fuerteventura (FUE)":              {"coords":(28.4527,-13.8638), "country":"Spain","icao":"GCFV"},
    "Santiago de Compostela (SCQ)":     {"coords":(42.8963,-8.4151),  "country":"Spain","icao":"LEST"},
    "Ibiza (IBZ)":                      {"coords":(38.8729, 1.3731),  "country":"Spain","icao":"LEIB"},
    "Menorca (MAH)":                    {"coords":(39.8626, 4.2186),  "country":"Spain","icao":"LEMH"},
    # ════════════════════════════════════════════════════════
    # PORTUGAL
    # ════════════════════════════════════════════════════════
    "Lisbon (LIS)":                     {"coords":(38.7813,-9.1359),  "country":"Portugal","icao":"LPPT"},
    "Porto (OPO)":                      {"coords":(41.2481,-8.6814),  "country":"Portugal","icao":"LPPR"},
    "Faro (FAO)":                       {"coords":(37.0144,-7.9659),  "country":"Portugal","icao":"LPFR"},
    "Funchal Madeira (FNC)":            {"coords":(32.6979,-16.7745), "country":"Portugal","icao":"LPMA"},
    "Ponta Delgada Azores (PDL)":       {"coords":(37.7412,-25.6981), "country":"Portugal","icao":"LPPD"},
    # ════════════════════════════════════════════════════════
    # ITALY
    # ════════════════════════════════════════════════════════
    "Rome Fiumicino (FCO)":             {"coords":(41.7999,12.2462),  "country":"Italy","icao":"LIRF"},
    "Milan Malpensa (MXP)":             {"coords":(45.6306, 8.7281),  "country":"Italy","icao":"LIMC"},
    "Milan Bergamo (BGY)":              {"coords":(45.6739, 9.7042),  "country":"Italy","icao":"LIME"},
    "Milan Linate (LIN)":               {"coords":(45.4456, 9.2767),  "country":"Italy","icao":"LIML"},
    "Venice Marco Polo (VCE)":          {"coords":(45.5053,12.3519),  "country":"Italy","icao":"LIPZ"},
    "Naples (NAP)":                     {"coords":(40.8860,14.2908),  "country":"Italy","icao":"LIRN"},
    "Catania (CTA)":                    {"coords":(37.4668,15.0664),  "country":"Italy","icao":"LICC"},
    "Bologna (BLQ)":                    {"coords":(44.5354,11.2887),  "country":"Italy","icao":"LIPE"},
    "Turin (TRN)":                      {"coords":(45.2006, 7.6497),  "country":"Italy","icao":"LIMF"},
    "Palermo (PMO)":                    {"coords":(38.1759,13.0910),  "country":"Italy","icao":"LICJ"},
    "Bari (BRI)":                       {"coords":(41.1389,16.7606),  "country":"Italy","icao":"LIBD"},
    "Florence (FLR)":                   {"coords":(43.8100,11.2051),  "country":"Italy","icao":"LIRQ"},
    "Pisa (PSA)":                       {"coords":(43.6839,10.3927),  "country":"Italy","icao":"LIRP"},
    "Cagliari (CAG)":                   {"coords":(39.2515, 9.0543),  "country":"Italy","icao":"LIEE"},
    "Verona (VRN)":                     {"coords":(45.3957,10.8885),  "country":"Italy","icao":"LIPX"},
    "Rome Ciampino (CIA)":              {"coords":(41.7994,12.5949),  "country":"Italy","icao":"LIRA"},
    # ════════════════════════════════════════════════════════
    # NETHERLANDS & BELGIUM & LUXEMBOURG
    # ════════════════════════════════════════════════════════
    "Amsterdam Schiphol (AMS)":         {"coords":(52.3086, 4.7639),  "country":"Netherlands","icao":"EHAM"},
    "Eindhoven (EIN)":                  {"coords":(51.4501, 5.3742),  "country":"Netherlands","icao":"EHEH"},
    "Rotterdam (RTM)":                  {"coords":(51.9569, 4.4372),  "country":"Netherlands","icao":"EHRD"},
    "Brussels (BRU)":                   {"coords":(50.9014, 4.4844),  "country":"Belgium","icao":"EBBR"},
    "Brussels Charleroi (CRL)":         {"coords":(50.4592, 4.4528),  "country":"Belgium","icao":"EBCI"},
    "Liege (LGG)":                      {"coords":(50.6374, 5.4432),  "country":"Belgium","icao":"EBLG"},
    "Luxembourg (LUX)":                 {"coords":(49.6233, 6.2044),  "country":"Luxembourg","icao":"ELLX"},
    # ════════════════════════════════════════════════════════
    # SWITZERLAND & AUSTRIA
    # ════════════════════════════════════════════════════════
    "Zurich (ZRH)":                     {"coords":(47.4647, 8.5492),  "country":"Switzerland","icao":"LSZH"},
    "Geneva (GVA)":                     {"coords":(46.2381, 6.1089),  "country":"Switzerland","icao":"LSGG"},
    "Basel (BSL)":                      {"coords":(47.5896, 7.5299),  "country":"Switzerland","icao":"LFSB"},
    "Vienna (VIE)":                     {"coords":(48.1103,16.5697),  "country":"Austria","icao":"LOWW"},
    "Salzburg (SZG)":                   {"coords":(47.7933,13.0043),  "country":"Austria","icao":"LOWS"},
    "Innsbruck (INN)":                  {"coords":(47.2602,11.3439),  "country":"Austria","icao":"LOWI"},
    "Graz (GRZ)":                       {"coords":(46.9911,15.4396),  "country":"Austria","icao":"LOWG"},
    "Linz (LNZ)":                       {"coords":(48.2332,14.1875),  "country":"Austria","icao":"LOWL"},
    # ════════════════════════════════════════════════════════
    # SCANDINAVIA
    # ════════════════════════════════════════════════════════
    "Copenhagen (CPH)":                 {"coords":(55.6180,12.6560),  "country":"Denmark","icao":"EKCH"},
    "Billund (BLL)":                    {"coords":(55.7403, 9.1519),  "country":"Denmark","icao":"EKBI"},
    "Aarhus (AAR)":                     {"coords":(56.3000,10.6192),  "country":"Denmark","icao":"EKAH"},
    "Oslo Gardermoen (OSL)":            {"coords":(60.1976,11.1004),  "country":"Norway","icao":"ENGM"},
    "Bergen (BGO)":                     {"coords":(60.2934, 5.2181),  "country":"Norway","icao":"ENBR"},
    "Stavanger (SVG)":                  {"coords":(58.8769, 5.6378),  "country":"Norway","icao":"ENZV"},
    "Trondheim (TRD)":                  {"coords":(63.4578,10.9239),  "country":"Norway","icao":"ENVA"},
    "Tromso (TOS)":                     {"coords":(69.6833,18.9189),  "country":"Norway","icao":"ENTC"},
    "Stockholm Arlanda (ARN)":          {"coords":(59.6519,17.9186),  "country":"Sweden","icao":"ESSA"},
    "Stockholm Skavsta (NYO)":          {"coords":(58.7886,16.9122),  "country":"Sweden","icao":"ESKN"},
    "Gothenburg (GOT)":                 {"coords":(57.6628,12.2798),  "country":"Sweden","icao":"ESGG"},
    "Malmo (MMX)":                      {"coords":(55.5363,13.3761),  "country":"Sweden","icao":"ESMS"},
    "Helsinki (HEL)":                   {"coords":(60.3172,24.9633),  "country":"Finland","icao":"EFHK"},
    "Turku (TKU)":                      {"coords":(60.5141,22.2628),  "country":"Finland","icao":"EFTU"},
    "Tampere (TMP)":                    {"coords":(61.4142,23.6044),  "country":"Finland","icao":"EFTP"},
    "Reykjavik Keflavik (KEF)":         {"coords":(63.9850,-22.6056), "country":"Iceland","icao":"BIKF"},
    "Reykjavik City (RKV)":             {"coords":(64.1300,-21.9406), "country":"Iceland","icao":"BIRK"},
    # ════════════════════════════════════════════════════════
    # EASTERN EUROPE
    # ════════════════════════════════════════════════════════
    "Warsaw Chopin (WAW)":              {"coords":(52.1657,20.9671),  "country":"Poland","icao":"EPWA"},
    "Warsaw Modlin (WMI)":              {"coords":(52.4511,20.6517),  "country":"Poland","icao":"EPMO"},
    "Krakow (KRK)":                     {"coords":(49.9683,19.7847),  "country":"Poland","icao":"EPKK"},
    "Gdansk (GDN)":                     {"coords":(54.3776,18.4662),  "country":"Poland","icao":"EPGD"},
    "Katowice (KTW)":                   {"coords":(50.4744,19.0800),  "country":"Poland","icao":"EPKT"},
    "Wroclaw (WRO)":                    {"coords":(51.1027,16.8858),  "country":"Poland","icao":"EPWR"},
    "Prague (PRG)":                     {"coords":(50.1008,14.2600),  "country":"Czech Republic","icao":"LKPR"},
    "Brno (BRQ)":                       {"coords":(49.1513,16.6944),  "country":"Czech Republic","icao":"LKTB"},
    "Budapest (BUD)":                   {"coords":(47.4298,19.2611),  "country":"Hungary","icao":"LHBP"},
    "Bucharest Henri Coanda (OTP)":     {"coords":(44.5711,26.0858),  "country":"Romania","icao":"LROP"},
    "Bucharest Baneasa (BBU)":          {"coords":(44.5032,26.1022),  "country":"Romania","icao":"LRBS"},
    "Cluj-Napoca (CLJ)":                {"coords":(46.7852,23.6861),  "country":"Romania","icao":"LRCL"},
    "Sofia (SOF)":                      {"coords":(42.6967,23.4114),  "country":"Bulgaria","icao":"LBSF"},
    "Athens (ATH)":                     {"coords":(37.9364,23.9445),  "country":"Greece","icao":"LGAV"},
    "Thessaloniki (SKG)":               {"coords":(40.5197,22.9709),  "country":"Greece","icao":"LGTS"},
    "Corfu (CFU)":                      {"coords":(39.6019,19.9117),  "country":"Greece","icao":"LGKR"},
    "Heraklion Crete (HER)":            {"coords":(35.3397,25.1803),  "country":"Greece","icao":"LGIR"},
    "Rhodes (RHO)":                     {"coords":(36.4053,28.0862),  "country":"Greece","icao":"LGRP"},
    "Mykonos (JMK)":                    {"coords":(37.4351,25.3481),  "country":"Greece","icao":"LGMK"},
    "Santorini (JTR)":                  {"coords":(36.3992,25.4793),  "country":"Greece","icao":"LGSR"},
    "Belgrade (BEG)":                   {"coords":(44.8184,20.3091),  "country":"Serbia","icao":"LYBE"},
    "Zagreb (ZAG)":                     {"coords":(45.7429,16.0688),  "country":"Croatia","icao":"LDZA"},
    "Split (SPU)":                      {"coords":(43.5389,16.2978),  "country":"Croatia","icao":"LDSP"},
    "Dubrovnik (DBV)":                  {"coords":(42.5614,18.2681),  "country":"Croatia","icao":"LDDU"},
    "Ljubljana (LJU)":                  {"coords":(46.2237,14.4576),  "country":"Slovenia","icao":"LJLJ"},
    "Sarajevo (SJJ)":                   {"coords":(43.8246,18.3314),  "country":"Bosnia","icao":"LQSA"},
    "Podgorica (TGD)":                  {"coords":(42.3594,19.2519),  "country":"Montenegro","icao":"LYPG"},
    "Tirana (TIA)":                     {"coords":(41.4147,19.7206),  "country":"Albania","icao":"LATI"},
    "Skopje (SKP)":                     {"coords":(41.9616,21.6214),  "country":"North Macedonia","icao":"LWSK"},
    "Pristina (PRN)":                   {"coords":(42.5728,21.0358),  "country":"Kosovo","icao":"BKPR"},
    "Riga (RIX)":                       {"coords":(56.9236,23.9711),  "country":"Latvia","icao":"EVRA"},
    "Tallinn (TLL)":                    {"coords":(59.4133,24.8328),  "country":"Estonia","icao":"EETN"},
    "Vilnius (VNO)":                    {"coords":(54.6341,25.2858),  "country":"Lithuania","icao":"EYVI"},
    "Minsk (MSQ)":                      {"coords":(53.8825,28.0322),  "country":"Belarus","icao":"UMMS"},
    "Chisinau (KIV)":                   {"coords":(46.9278,28.9308),  "country":"Moldova","icao":"LUKK"},
    # ════════════════════════════════════════════════════════
    # TURKEY
    # ════════════════════════════════════════════════════════
    "Istanbul (IST)":                   {"coords":(41.2753,28.7519),  "country":"Turkey","icao":"LTFM"},
    "Istanbul Sabiha (SAW)":            {"coords":(40.8986,29.3092),  "country":"Turkey","icao":"LTFJ"},
    "Ankara (ESB)":                     {"coords":(40.1281,32.9951),  "country":"Turkey","icao":"LTAC"},
    "Izmir (ADB)":                      {"coords":(38.2924,27.1569),  "country":"Turkey","icao":"LTBJ"},
    "Antalya (AYT)":                    {"coords":(36.8987,30.8003),  "country":"Turkey","icao":"LTAI"},
    "Bodrum (BJV)":                     {"coords":(37.2506,27.6644),  "country":"Turkey","icao":"LTFE"},
    "Dalaman (DLM)":                    {"coords":(36.7131,28.7925),  "country":"Turkey","icao":"LTBS"},
    "Adana (ADA)":                      {"coords":(36.9822,35.2803),  "country":"Turkey","icao":"LTAF"},
    "Trabzon (TZX)":                    {"coords":(40.9950,39.7897),  "country":"Turkey","icao":"LTCG"},
    "Gaziantep (GZT)":                  {"coords":(36.9472,37.4786),  "country":"Turkey","icao":"LTAJ"},
    "Kayseri (ASR)":                    {"coords":(38.7703,35.4953),  "country":"Turkey","icao":"LTAU"},
    # ════════════════════════════════════════════════════════
    # MIDDLE EAST & GULF
    # ════════════════════════════════════════════════════════
    "Dubai (DXB)":                      {"coords":(25.2532,55.3657),  "country":"UAE","icao":"OMDB"},
    "Dubai Al Maktoum (DWC)":           {"coords":(24.8963,55.1614),  "country":"UAE","icao":"OMDW"},
    "Abu Dhabi (AUH)":                  {"coords":(24.4330,54.6511),  "country":"UAE","icao":"OMAA"},
    "Sharjah (SHJ)":                    {"coords":(25.3285,55.5172),  "country":"UAE","icao":"OMSJ"},
    "Doha Hamad (DOH)":                 {"coords":(25.2609,51.6138),  "country":"Qatar","icao":"OTHH"},
    "Riyadh (RUH)":                     {"coords":(24.9578,46.6988),  "country":"Saudi Arabia","icao":"OERK"},
    "Jeddah (JED)":                     {"coords":(21.6796,39.1565),  "country":"Saudi Arabia","icao":"OEJN"},
    "Medina (MED)":                     {"coords":(24.5534,39.7051),  "country":"Saudi Arabia","icao":"OEMA"},
    "Dammam (DMM)":                     {"coords":(26.4712,49.7979),  "country":"Saudi Arabia","icao":"OEDF"},
    "Muscat (MCT)":                     {"coords":(23.5933,58.2844),  "country":"Oman","icao":"OOMS"},
    "Salalah (SLL)":                    {"coords":(17.0372,54.0913),  "country":"Oman","icao":"OOSA"},
    "Amman (AMM)":                      {"coords":(31.7226,35.9932),  "country":"Jordan","icao":"OJAM"},
    "Aqaba (AQJ)":                      {"coords":(29.6117,35.0181),  "country":"Jordan","icao":"OJAQ"},
    "Beirut (BEY)":                     {"coords":(33.8208,35.4883),  "country":"Lebanon","icao":"OLBA"},
    "Cairo (CAI)":                      {"coords":(30.1219,31.4056),  "country":"Egypt","icao":"HECA"},
    "Sharm el-Sheikh (SSH)":            {"coords":(27.9773,34.3950),  "country":"Egypt","icao":"HESH"},
    "Hurghada (HRG)":                   {"coords":(27.1783,33.7994),  "country":"Egypt","icao":"HEGN"},
    "Alexandria (HBE)":                 {"coords":(30.9172,29.6964),  "country":"Egypt","icao":"HEBA"},
    "Luxor (LXR)":                      {"coords":(25.6710,32.7066),  "country":"Egypt","icao":"HELX"},
    "Kuwait City (KWI)":                {"coords":(29.2266,47.9689),  "country":"Kuwait","icao":"OKBK"},
    "Bahrain (BAH)":                    {"coords":(26.2708,50.6336),  "country":"Bahrain","icao":"OBBI"},
    "Tel Aviv (TLV)":                   {"coords":(32.0114,34.8867),  "country":"Israel","icao":"LLBG"},
    "Sanaa (SAH)":                      {"coords":(15.4763,44.2197),  "country":"Yemen","icao":"OYSN"},
    "Aden (ADE)":                       {"coords":(12.8294,45.0289),  "country":"Yemen","icao":"OYAA"},
    # ════════════════════════════════════════════════════════
    # AFRICA — NORTH
    # ════════════════════════════════════════════════════════
    "Casablanca (CMN)":                 {"coords":(33.3675,-7.5898),  "country":"Morocco","icao":"GMMN"},
    "Marrakech (RAK)":                  {"coords":(31.6069,-8.0363),  "country":"Morocco","icao":"GMMX"},
    "Fes (FEZ)":                        {"coords":(33.9272,-4.9778),  "country":"Morocco","icao":"GMFF"},
    "Rabat (RBA)":                      {"coords":(34.0514,-6.7515),  "country":"Morocco","icao":"GMME"},
    "Tangier (TNG)":                    {"coords":(35.7269,-5.9169),  "country":"Morocco","icao":"GMTT"},
    "Agadir (AGA)":                     {"coords":(30.3250,-9.4131),  "country":"Morocco","icao":"GMAD"},
    "Algiers (ALG)":                    {"coords":(36.6910, 3.2153),  "country":"Algeria","icao":"DAAG"},
    "Oran (ORN)":                       {"coords":(35.6239,-0.6212),  "country":"Algeria","icao":"DAOO"},
    "Tunis (TUN)":                      {"coords":(36.8510,10.2272),  "country":"Tunisia","icao":"DTTA"},
    "Djerba (DJE)":                     {"coords":(33.8753,10.7755),  "country":"Tunisia","icao":"DTTJ"},
    "Tripoli (TIP)":                    {"coords":(32.6635,13.1590),  "country":"Libya","icao":"HLLT"},
    # ════════════════════════════════════════════════════════
    # AFRICA — EAST & HORN
    # ════════════════════════════════════════════════════════
    "Nairobi (NBO)":                    {"coords":(-1.3192,36.9275),  "country":"Kenya","icao":"HKJK"},
    "Mombasa (MBA)":                    {"coords":(-4.0348,39.5942),  "country":"Kenya","icao":"HKMO"},
    "Addis Ababa (ADD)":                {"coords":(8.9779,38.7993),   "country":"Ethiopia","icao":"HAAB"},
    "Djibouti (JIB)":                   {"coords":(11.5473,43.1594),  "country":"Djibouti","icao":"HDAM"},
    "Mogadishu (MGQ)":                  {"coords":(2.0144,45.3047),   "country":"Somalia","icao":"HCMM"},
    "Kigali (KGL)":                     {"coords":(-1.9686,30.1395),  "country":"Rwanda","icao":"HRYR"},
    "Entebbe (EBB)":                    {"coords":(0.0424,32.4435),   "country":"Uganda","icao":"HUEN"},
    "Dar es Salaam (DAR)":              {"coords":(-6.8781,39.2026),  "country":"Tanzania","icao":"HTDA"},
    "Kilimanjaro (JRO)":                {"coords":(-3.4294,37.0745),  "country":"Tanzania","icao":"HTKJ"},
    "Zanzibar (ZNZ)":                   {"coords":(-6.2220,39.2249),  "country":"Tanzania","icao":"HTZA"},
    "Antananarivo (TNR)":               {"coords":(-18.7969,47.4788), "country":"Madagascar","icao":"FMMI"},
    "Moroni (HAH)":                     {"coords":(-11.5337,43.2719), "country":"Comoros","icao":"FMCH"},
    # ════════════════════════════════════════════════════════
    # AFRICA — WEST
    # ════════════════════════════════════════════════════════
    "Lagos (LOS)":                      {"coords":(6.5774, 3.3212),   "country":"Nigeria","icao":"DNMM"},
    "Abuja (ABV)":                      {"coords":(9.0068, 7.2632),   "country":"Nigeria","icao":"DNAA"},
    "Accra (ACC)":                      {"coords":(5.6052,-0.1668),   "country":"Ghana","icao":"DGAA"},
    "Dakar (DKR)":                      {"coords":(14.7397,-17.4902), "country":"Senegal","icao":"GOOY"},
    "Abidjan (ABJ)":                    {"coords":(5.2614,-3.9262),   "country":"Ivory Coast","icao":"DIAP"},
    "Bamako (BKO)":                     {"coords":(12.5336,-7.9499),  "country":"Mali","icao":"GABS"},
    "Conakry (CKY)":                    {"coords":(9.5769,-13.6119),  "country":"Guinea","icao":"GUCY"},
    "Freetown (FNA)":                   {"coords":(8.6164,-13.1955),  "country":"Sierra Leone","icao":"GFLL"},
    "Monrovia (MLW)":                   {"coords":(6.2893,-10.7587),  "country":"Liberia","icao":"GLMR"},
    "Banjul (BJL)":                     {"coords":(13.3380,-16.6522), "country":"Gambia","icao":"GBYD"},
    "Ouagadougou (OUA)":                {"coords":(12.3533,-1.5125),  "country":"Burkina Faso","icao":"DFFD"},
    "Niamey (NIM)":                     {"coords":(13.4815, 2.1836),  "country":"Niger","icao":"DRRN"},
    "Douala (DLA)":                     {"coords":(4.0061, 9.7197),   "country":"Cameroon","icao":"FKKD"},
    "Yaounde (YAO)":                    {"coords":(3.8372,11.5233),   "country":"Cameroon","icao":"FKKY"},
    "Libreville (LBV)":                 {"coords":(0.4586, 9.4122),   "country":"Gabon","icao":"FOOL"},
    "Brazzaville (BZV)":                {"coords":(-4.2517,15.2531),  "country":"Congo","icao":"FCBB"},
    "Kinshasa (FIH)":                   {"coords":(-4.3857,15.4446),  "country":"DR Congo","icao":"FZAA"},
    # ════════════════════════════════════════════════════════
    # AFRICA — SOUTHERN
    # ════════════════════════════════════════════════════════
    "Johannesburg (JNB)":               {"coords":(-26.1367,28.2424), "country":"South Africa","icao":"FAOR"},
    "Cape Town (CPT)":                  {"coords":(-33.9648,18.6017), "country":"South Africa","icao":"FACT"},
    "Durban (DUR)":                     {"coords":(-29.6144,31.1197), "country":"South Africa","icao":"FALE"},
    "Pretoria (PRY)":                   {"coords":(-25.6536,28.2242), "country":"South Africa","icao":"FAWB"},
    "Port Elizabeth (PLZ)":             {"coords":(-33.9849,25.6173), "country":"South Africa","icao":"FAPE"},
    "Harare (HRE)":                     {"coords":(-17.9318,31.0928), "country":"Zimbabwe","icao":"FVHA"},
    "Lusaka (LUN)":                     {"coords":(-15.3308,28.4526), "country":"Zambia","icao":"FLLS"},
    "Lilongwe (LLW)":                   {"coords":(-13.7894,33.7814), "country":"Malawi","icao":"FWKI"},
    "Maputo (MPM)":                     {"coords":(-25.9208,32.5728), "country":"Mozambique","icao":"FQMA"},
    "Luanda (LAD)":                     {"coords":(-8.8583,13.2311),  "country":"Angola","icao":"FNLU"},
    "Windhoek (WDH)":                   {"coords":(-22.4799,17.4709), "country":"Namibia","icao":"FYWH"},
    "Gaborone (GBE)":                   {"coords":(-24.5553,25.9182), "country":"Botswana","icao":"FBSK"},
    "Mauritius (MRU)":                  {"coords":(-20.4302,57.6836), "country":"Mauritius","icao":"FIMP"},
    "Reunion (RUN)":                    {"coords":(-20.8872,55.5103), "country":"Reunion","icao":"FMEE"},
    "Seychelles (SEZ)":                 {"coords":(-4.6742,55.5219),  "country":"Seychelles","icao":"FSIA"},
    # ════════════════════════════════════════════════════════
    # CENTRAL ASIA & CAUCASUS
    # ════════════════════════════════════════════════════════
    "Baku (GYD)":                       {"coords":(40.4675,50.0467),  "country":"Azerbaijan","icao":"UBBB"},
    "Tbilisi (TBS)":                    {"coords":(41.6692,44.9547),  "country":"Georgia","icao":"UGTB"},
    "Yerevan (EVN)":                    {"coords":(40.1473,44.3959),  "country":"Armenia","icao":"UDYZ"},
    "Almaty (ALA)":                     {"coords":(43.3521,77.0405),  "country":"Kazakhstan","icao":"UAAA"},
    "Nur-Sultan (NQZ)":                 {"coords":(51.0222,71.4669),  "country":"Kazakhstan","icao":"UACC"},
    "Tashkent (TAS)":                   {"coords":(41.2579,69.2811),  "country":"Uzbekistan","icao":"UTTT"},
    "Samarkand (SKD)":                  {"coords":(39.7005,66.9838),  "country":"Uzbekistan","icao":"UTSS"},
    "Ashgabat (ASB)":                   {"coords":(37.9864,58.3611),  "country":"Turkmenistan","icao":"UTAA"},
    "Dushanbe (DYU)":                   {"coords":(38.5433,68.7750),  "country":"Tajikistan","icao":"UTDD"},
    "Bishkek (FRU)":                    {"coords":(43.0612,74.4776),  "country":"Kyrgyzstan","icao":"UAFM"},
    # ════════════════════════════════════════════════════════
    # SOUTH ASIA
    # ════════════════════════════════════════════════════════
    "Mumbai (BOM)":                     {"coords":(19.0896,72.8656),  "country":"India","icao":"VABB"},
    "Delhi (DEL)":                      {"coords":(28.5562,77.1000),  "country":"India","icao":"VIDP"},
    "Bangalore (BLR)":                  {"coords":(13.1986,77.7066),  "country":"India","icao":"VOBL"},
    "Chennai (MAA)":                    {"coords":(12.9900,80.1693),  "country":"India","icao":"VOMM"},
    "Hyderabad (HYD)":                  {"coords":(17.2403,78.4294),  "country":"India","icao":"VOHS"},
    "Kolkata (CCU)":                    {"coords":(22.6547,88.4467),  "country":"India","icao":"VECC"},
    "Pune (PNQ)":                       {"coords":(18.5822,73.9197),  "country":"India","icao":"VAPO"},
    "Ahmedabad (AMD)":                  {"coords":(23.0771,72.6347),  "country":"India","icao":"VAAH"},
    "Goa (GOI)":                        {"coords":(15.3808,73.8314),  "country":"India","icao":"VOGO"},
    "Kochi (COK)":                      {"coords":(10.1520,76.3999),  "country":"India","icao":"VOCI"},
    "Trivandrum (TRV)":                 {"coords":(8.4822,76.9192),   "country":"India","icao":"VOTV"},
    "Jaipur (JAI)":                     {"coords":(26.8242,75.8122),  "country":"India","icao":"VIJP"},
    "Guwahati (GAU)":                   {"coords":(26.1061,91.5856),  "country":"India","icao":"VEGT"},
    "Varanasi (VNS)":                   {"coords":(25.4524,82.8592),  "country":"India","icao":"VIBN"},
    "Amritsar (ATQ)":                   {"coords":(31.7096,74.7997),  "country":"India","icao":"VIAR"},
    "Colombo (CMB)":                    {"coords":(7.1800,79.8841),   "country":"Sri Lanka","icao":"VCBI"},
    "Dhaka (DAC)":                      {"coords":(23.8433,90.3978),  "country":"Bangladesh","icao":"VGZR"},
    "Kathmandu (KTM)":                  {"coords":(27.6966,85.3591),  "country":"Nepal","icao":"VNKT"},
    "Karachi (KHI)":                    {"coords":(24.9065,67.1608),  "country":"Pakistan","icao":"OPKC"},
    "Lahore (LHE)":                     {"coords":(31.5216,74.4036),  "country":"Pakistan","icao":"OPLA"},
    "Islamabad (ISB)":                  {"coords":(33.6167,73.0997),  "country":"Pakistan","icao":"OPIS"},
    "Peshawar (PEW)":                   {"coords":(33.9939,71.5146),  "country":"Pakistan","icao":"OPPS"},
    "Male (MLE)":                       {"coords":(4.1919,73.5292),   "country":"Maldives","icao":"VRMM"},
    "Bhutan (PBH)":                     {"coords":(27.4033,89.4664),  "country":"Bhutan","icao":"VQPR"},
    # ════════════════════════════════════════════════════════
    # SOUTHEAST ASIA
    # ════════════════════════════════════════════════════════
    "Singapore Changi (SIN)":           {"coords":(1.3644,103.9915),  "country":"Singapore","icao":"WSSS"},
    "Kuala Lumpur (KUL)":               {"coords":(2.7456,101.7072),  "country":"Malaysia","icao":"WMKK"},
    "Kuala Lumpur Subang (SZB)":        {"coords":(3.1306,101.5494),  "country":"Malaysia","icao":"WMSA"},
    "Penang (PEN)":                     {"coords":(5.2972,100.2769),  "country":"Malaysia","icao":"WMKP"},
    "Kota Kinabalu (BKI)":              {"coords":(5.9372,116.0508),  "country":"Malaysia","icao":"WBKK"},
    "Kuching (KCH)":                    {"coords":(1.4847,110.3428),  "country":"Malaysia","icao":"WBGG"},
    "Bangkok Suvarnabhumi (BKK)":       {"coords":(13.6811,100.7470), "country":"Thailand","icao":"VTBS"},
    "Bangkok Don Mueang (DMK)":         {"coords":(13.9126,100.6069), "country":"Thailand","icao":"VTBD"},
    "Phuket (HKT)":                     {"coords":(8.1132,98.3169),   "country":"Thailand","icao":"VTSP"},
    "Chiang Mai (CNX)":                 {"coords":(18.7668,98.9628),  "country":"Thailand","icao":"VTCC"},
    "Koh Samui (USM)":                  {"coords":(9.5478,100.0628),  "country":"Thailand","icao":"VTSM"},
    "Jakarta Soekarno (CGK)":           {"coords":(-6.1275,106.6537), "country":"Indonesia","icao":"WIII"},
    "Bali Denpasar (DPS)":              {"coords":(-8.7483,115.1670), "country":"Indonesia","icao":"WADD"},
    "Surabaya (SUB)":                   {"coords":(-7.3798,112.7869), "country":"Indonesia","icao":"WARR"},
    "Medan (KNO)":                      {"coords":(3.6422,98.8853),   "country":"Indonesia","icao":"WIMM"},
    "Makassar (UPG)":                   {"coords":(-5.0617,119.5544), "country":"Indonesia","icao":"WAAA"},
    "Lombok (LOP)":                     {"coords":(-8.7573,116.2767), "country":"Indonesia","icao":"WADL"},
    "Yogyakarta (JOG)":                 {"coords":(-7.7882,110.4317), "country":"Indonesia","icao":"WAHH"},
    "Manila (MNL)":                     {"coords":(14.5086,121.0194), "country":"Philippines","icao":"RPLL"},
    "Cebu (CEB)":                       {"coords":(10.3075,123.9791), "country":"Philippines","icao":"RPVM"},
    "Davao (DVO)":                      {"coords":(7.1255,125.6458),  "country":"Philippines","icao":"RPMD"},
    "Ho Chi Minh City (SGN)":           {"coords":(10.8188,106.6520), "country":"Vietnam","icao":"VVTS"},
    "Hanoi (HAN)":                      {"coords":(21.2212,105.8072), "country":"Vietnam","icao":"VVNB"},
    "Da Nang (DAD)":                    {"coords":(16.0439,108.1994), "country":"Vietnam","icao":"VVDN"},
    "Phnom Penh (PNH)":                 {"coords":(11.5466,104.8441), "country":"Cambodia","icao":"VDPP"},
    "Siem Reap (REP)":                  {"coords":(13.4108,103.8128), "country":"Cambodia","icao":"VDSR"},
    "Vientiane (VTE)":                  {"coords":(17.9883,102.5633), "country":"Laos","icao":"VLVT"},
    "Yangon (RGN)":                     {"coords":(16.9023,96.1332),  "country":"Myanmar","icao":"VYYY"},
    "Mandalay (MDL)":                   {"coords":(21.7021,95.9778),  "country":"Myanmar","icao":"VYMD"},
    "Brunei (BWN)":                     {"coords":(4.9442,114.9280),  "country":"Brunei","icao":"WBSB"},
    "Timor-Leste Dili (DIL)":           {"coords":(-8.5497,125.5247), "country":"Timor-Leste","icao":"WPDL"},
    # ════════════════════════════════════════════════════════
    # EAST ASIA
    # ════════════════════════════════════════════════════════
    "Beijing Capital (PEK)":            {"coords":(40.0799,116.6031), "country":"China","icao":"ZBAA"},
    "Beijing Daxing (PKX)":             {"coords":(39.5097,116.4105), "country":"China","icao":"ZBAD"},
    "Shanghai Pudong (PVG)":            {"coords":(31.1443,121.8083), "country":"China","icao":"ZSPD"},
    "Shanghai Hongqiao (SHA)":          {"coords":(31.1979,121.3364), "country":"China","icao":"ZSSS"},
    "Guangzhou (CAN)":                  {"coords":(23.3925,113.2988), "country":"China","icao":"ZGGG"},
    "Shenzhen (SZX)":                   {"coords":(22.6395,113.8145), "country":"China","icao":"ZGSZ"},
    "Chengdu Tianfu (TFU)":             {"coords":(30.3125,104.4442), "country":"China","icao":"ZUTF"},
    "Chengdu Shuangliu (CTU)":          {"coords":(30.5785,103.9473), "country":"China","icao":"ZUUU"},
    "Kunming (KMG)":                    {"coords":(24.9922,102.7433), "country":"China","icao":"ZPPP"},
    "Chongqing (CKG)":                  {"coords":(29.7192,106.6417), "country":"China","icao":"ZUCK"},
    "Hangzhou (HGH)":                   {"coords":(30.2295,120.4344), "country":"China","icao":"ZSHC"},
    "Wuhan (WUH)":                      {"coords":(30.7783,114.2081), "country":"China","icao":"ZHHH"},
    "Xiamen (XMN)":                     {"coords":(24.5440,118.1278), "country":"China","icao":"ZSAM"},
    "Nanjing (NKG)":                    {"coords":(31.7420,118.8622), "country":"China","icao":"ZSNJ"},
    "Xian (XIY)":                       {"coords":(34.4471,108.7517), "country":"China","icao":"ZLXY"},
    "Qingdao (TAO)":                    {"coords":(36.2661,120.3744), "country":"China","icao":"ZSQD"},
    "Shenyang (SHE)":                   {"coords":(41.6398,123.4836), "country":"China","icao":"ZYTX"},
    "Harbin (HRB)":                     {"coords":(45.6234,126.2500), "country":"China","icao":"ZYHB"},
    "Dalian (DLC)":                     {"coords":(38.9657,121.5386), "country":"China","icao":"ZYTL"},
    "Guiyang (KWE)":                    {"coords":(26.5386,106.8014), "country":"China","icao":"ZUGY"},
    "Zhengzhou (CGO)":                  {"coords":(34.5197,113.8408), "country":"China","icao":"ZHCC"},
    "Urumqi (URC)":                     {"coords":(43.9072,87.4742),  "country":"China","icao":"ZWWW"},
    "Lhasa (LXA)":                      {"coords":(29.2978,90.9119),  "country":"China","icao":"ZULS"},
    "Hong Kong (HKG)":                  {"coords":(22.3080,113.9185), "country":"Hong Kong","icao":"VHHH"},
    "Macau (MFM)":                      {"coords":(22.1496,113.5920), "country":"Macau","icao":"VMMC"},
    "Taipei Taoyuan (TPE)":             {"coords":(25.0777,121.2327), "country":"Taiwan","icao":"RCTP"},
    "Taipei Songshan (TSA)":            {"coords":(25.0694,121.5525), "country":"Taiwan","icao":"RCSS"},
    "Kaohsiung (KHH)":                  {"coords":(22.5771,120.3497), "country":"Taiwan","icao":"RCKH"},
    "Seoul Incheon (ICN)":              {"coords":(37.4602,126.4407), "country":"South Korea","icao":"RKSI"},
    "Seoul Gimpo (GMP)":                {"coords":(37.5583,126.7906), "country":"South Korea","icao":"RKSS"},
    "Busan (PUS)":                      {"coords":(35.1795,128.9381), "country":"South Korea","icao":"RKPK"},
    "Jeju (CJU)":                       {"coords":(33.5113,126.4930), "country":"South Korea","icao":"RKPC"},
    "Tokyo Narita (NRT)":               {"coords":(35.7653,140.3856), "country":"Japan","icao":"RJAA"},
    "Tokyo Haneda (HND)":               {"coords":(35.5494,139.7798), "country":"Japan","icao":"RJTT"},
    "Osaka Kansai (KIX)":               {"coords":(34.4347,135.2441), "country":"Japan","icao":"RJBB"},
    "Osaka Itami (ITM)":                {"coords":(34.7847,135.4386), "country":"Japan","icao":"RJOO"},
    "Nagoya (NGO)":                     {"coords":(34.8583,136.8050), "country":"Japan","icao":"RJGG"},
    "Sapporo (CTS)":                    {"coords":(42.7752,141.6922), "country":"Japan","icao":"RJCC"},
    "Fukuoka (FUK)":                    {"coords":(33.5858,130.4511), "country":"Japan","icao":"RJFF"},
    "Okinawa (OKA)":                    {"coords":(26.1958,127.6461), "country":"Japan","icao":"ROAH"},
    "Hiroshima (HIJ)":                  {"coords":(34.4361,132.9194), "country":"Japan","icao":"RJOA"},
    "Ulaanbaatar (ULN)":               {"coords":(47.8431,106.7664), "country":"Mongolia","icao":"ZMUB"},
    # ════════════════════════════════════════════════════════
    # RUSSIA (accessible routes — east of Urals, or neutral)
    # ════════════════════════════════════════════════════════
    "Moscow Sheremetyevo (SVO)":        {"coords":(55.9726,37.4146),  "country":"Russia","icao":"UUEE"},
    "Moscow Domodedovo (DME)":          {"coords":(55.4088,37.9063),  "country":"Russia","icao":"UUDD"},
    "Moscow Vnukovo (VKO)":             {"coords":(55.5915,37.2615),  "country":"Russia","icao":"UUWW"},
    "St Petersburg (LED)":             {"coords":(59.8003,30.2625),  "country":"Russia","icao":"ULLI"},
    "Novosibirsk (OVB)":               {"coords":(54.9633,82.6503),  "country":"Russia","icao":"UNNT"},
    "Vladivostok (VVO)":               {"coords":(43.3989,132.1481), "country":"Russia","icao":"UHWW"},
    "Irkutsk (IKT)":                   {"coords":(52.2681,104.3889), "country":"Russia","icao":"UIII"},
    "Yekaterinburg (SVX)":             {"coords":(56.7431,60.8028),  "country":"Russia","icao":"USSS"},
    "Kazan (KZN)":                     {"coords":(55.6063,49.2783),  "country":"Russia","icao":"UWKD"},
    # ════════════════════════════════════════════════════════
    # NORTH AMERICA — USA (East Coast)
    # ════════════════════════════════════════════════════════
    "New York JFK (JFK)":               {"coords":(40.6413,-73.7781), "country":"United States","icao":"KJFK"},
    "New York Newark (EWR)":            {"coords":(40.6895,-74.1745), "country":"United States","icao":"KEWR"},
    "New York LaGuardia (LGA)":         {"coords":(40.7772,-73.8726), "country":"United States","icao":"KLGA"},
    "Boston (BOS)":                     {"coords":(42.3656,-71.0096), "country":"United States","icao":"KBOS"},
    "Washington Dulles (IAD)":          {"coords":(38.9531,-77.4565), "country":"United States","icao":"KIAD"},
    "Washington Reagan (DCA)":          {"coords":(38.8512,-77.0402), "country":"United States","icao":"KDCA"},
    "Philadelphia (PHL)":               {"coords":(39.8721,-75.2411), "country":"United States","icao":"KPHL"},
    "Baltimore (BWI)":                  {"coords":(39.1754,-76.6683), "country":"United States","icao":"KBWI"},
    "Miami (MIA)":                      {"coords":(25.7959,-80.2870), "country":"United States","icao":"KMIA"},
    "Fort Lauderdale (FLL)":            {"coords":(26.0726,-80.1527), "country":"United States","icao":"KFLL"},
    "Orlando (MCO)":                    {"coords":(28.4312,-81.3081), "country":"United States","icao":"KMCO"},
    "Tampa (TPA)":                      {"coords":(27.9755,-82.5332), "country":"United States","icao":"KTPA"},
    "Charlotte (CLT)":                  {"coords":(35.2140,-80.9431), "country":"United States","icao":"KCLT"},
    "Atlanta (ATL)":                    {"coords":(33.6407,-84.4277), "country":"United States","icao":"KATL"},
    "Detroit (DTW)":                    {"coords":(42.2162,-83.3554), "country":"United States","icao":"KDTW"},
    "Pittsburgh (PIT)":                 {"coords":(40.4915,-80.2329), "country":"United States","icao":"KPIT"},
    # ════════════════════════════════════════════════════════
    # NORTH AMERICA — USA (Central & South)
    # ════════════════════════════════════════════════════════
    "Chicago O'Hare (ORD)":             {"coords":(41.9742,-87.9073), "country":"United States","icao":"KORD"},
    "Chicago Midway (MDW)":             {"coords":(41.7868,-87.7522), "country":"United States","icao":"KMDW"},
    "Minneapolis (MSP)":                {"coords":(44.8848,-93.2223), "country":"United States","icao":"KMSP"},
    "St Louis (STL)":                   {"coords":(38.7487,-90.3700), "country":"United States","icao":"KSTL"},
    "Kansas City (MCI)":                {"coords":(39.2976,-94.7139), "country":"United States","icao":"KMCI"},
    "Houston Intercontinental (IAH)":   {"coords":(29.9902,-95.3368), "country":"United States","icao":"KIAH"},
    "Houston Hobby (HOU)":              {"coords":(29.6454,-95.2789), "country":"United States","icao":"KHOU"},
    "Dallas Fort Worth (DFW)":          {"coords":(32.8998,-97.0403), "country":"United States","icao":"KDFW"},
    "Dallas Love Field (DAL)":          {"coords":(32.8471,-96.8517), "country":"United States","icao":"KDAL"},
    "New Orleans (MSY)":                {"coords":(29.9934,-90.2580), "country":"United States","icao":"KMSY"},
    "Denver (DEN)":                     {"coords":(39.8561,-104.6737),"country":"United States","icao":"KDEN"},
    "Salt Lake City (SLC)":             {"coords":(40.7884,-111.9778),"country":"United States","icao":"KSLC"},
    "Phoenix (PHX)":                    {"coords":(33.4373,-112.0078),"country":"United States","icao":"KPHX"},
    "Tucson (TUS)":                     {"coords":(32.1161,-110.9410),"country":"United States","icao":"KTUS"},
    # ════════════════════════════════════════════════════════
    # NORTH AMERICA — USA (West Coast & Pacific)
    # ════════════════════════════════════════════════════════
    "Los Angeles (LAX)":                {"coords":(33.9425,-118.4081),"country":"United States","icao":"KLAX"},
    "San Francisco (SFO)":              {"coords":(37.6213,-122.3790),"country":"United States","icao":"KSFO"},
    "San Jose (SJC)":                   {"coords":(37.3626,-121.9290),"country":"United States","icao":"KSJC"},
    "Oakland (OAK)":                    {"coords":(37.7213,-122.2208),"country":"United States","icao":"KOAK"},
    "Seattle (SEA)":                    {"coords":(47.4502,-122.3088),"country":"United States","icao":"KSEA"},
    "Portland (PDX)":                   {"coords":(45.5887,-122.5975),"country":"United States","icao":"KPDX"},
    "Las Vegas (LAS)":                  {"coords":(36.0840,-115.1537),"country":"United States","icao":"KLAS"},
    "San Diego (SAN)":                  {"coords":(32.7336,-117.1897),"country":"United States","icao":"KSAN"},
    "Sacramento (SMF)":                 {"coords":(38.6954,-121.5908),"country":"United States","icao":"KSMF"},
    "Honolulu (HNL)":                   {"coords":(21.3245,-157.9251),"country":"United States","icao":"PHNL"},
    "Maui (OGG)":                       {"coords":(20.8986,-156.4305),"country":"United States","icao":"PHOG"},
    "Anchorage (ANC)":                  {"coords":(61.1741,-149.9961),"country":"United States","icao":"PANC"},
    # ════════════════════════════════════════════════════════
    # CANADA
    # ════════════════════════════════════════════════════════
    "Toronto Pearson (YYZ)":            {"coords":(43.6777,-79.6248), "country":"Canada","icao":"CYYZ"},
    "Montreal Trudeau (YUL)":           {"coords":(45.4706,-73.7408), "country":"Canada","icao":"CYUL"},
    "Vancouver (YVR)":                  {"coords":(49.1967,-123.1815),"country":"Canada","icao":"CYVR"},
    "Calgary (YYC)":                    {"coords":(51.1215,-114.0132),"country":"Canada","icao":"CYYC"},
    "Edmonton (YEG)":                   {"coords":(53.3097,-113.5797),"country":"Canada","icao":"CYEG"},
    "Ottawa (YOW)":                     {"coords":(45.3225,-75.6692), "country":"Canada","icao":"CYOW"},
    "Quebec City (YQB)":                {"coords":(46.7911,-71.3933), "country":"Canada","icao":"CYQB"},
    "Winnipeg (YWG)":                   {"coords":(49.9100,-97.2398), "country":"Canada","icao":"CYWG"},
    "Halifax (YHZ)":                    {"coords":(44.8808,-63.5086), "country":"Canada","icao":"CYHZ"},
    "St. Johns (YYT)":                  {"coords":(47.6189,-52.7419), "country":"Canada","icao":"CYYT"},
    "Kelowna (YLW)":                    {"coords":(49.9561,-119.3778),"country":"Canada","icao":"CYLW"},
    "Victoria (YYJ)":                   {"coords":(48.6469,-123.4258),"country":"Canada","icao":"CYYJ"},
    # ════════════════════════════════════════════════════════
    # MEXICO & CENTRAL AMERICA
    # ════════════════════════════════════════════════════════
    "Mexico City (MEX)":                {"coords":(19.4363,-99.0721), "country":"Mexico","icao":"MMMX"},
    "Cancun (CUN)":                     {"coords":(21.0365,-86.8771), "country":"Mexico","icao":"MMUN"},
    "Guadalajara (GDL)":                {"coords":(20.5218,-103.3111),"country":"Mexico","icao":"MMGL"},
    "Monterrey (MTY)":                  {"coords":(25.7785,-100.1069),"country":"Mexico","icao":"MMMY"},
    "Los Cabos (SJD)":                  {"coords":(23.1518,-109.7211),"country":"Mexico","icao":"MMSD"},
    "Puerto Vallarta (PVR)":            {"coords":(20.6801,-105.2544),"country":"Mexico","icao":"MMPR"},
    "Mazatlan (MZT)":                   {"coords":(23.1614,-106.2661),"country":"Mexico","icao":"MMMZ"},
    "Merida (MID)":                     {"coords":(20.9370,-89.6577), "country":"Mexico","icao":"MMMD"},
    "Guatemala City (GUA)":             {"coords":(14.5833,-90.5275), "country":"Guatemala","icao":"MGGT"},
    "San Jose (SJO)":                   {"coords":(9.9939,-84.2089),  "country":"Costa Rica","icao":"MROC"},
    "Panama City (PTY)":                {"coords":(9.0714,-79.3834),  "country":"Panama","icao":"MPTO"},
    "Havana (HAV)":                     {"coords":(22.9892,-82.4091), "country":"Cuba","icao":"MUHA"},
    "Kingston (KIN)":                   {"coords":(17.9357,-76.7875), "country":"Jamaica","icao":"MKJP"},
    "Punta Cana (PUJ)":                 {"coords":(18.5674,-68.3634), "country":"Dominican Republic","icao":"MDPC"},
    "Santo Domingo (SDQ)":              {"coords":(18.4297,-69.6689), "country":"Dominican Republic","icao":"MDSD"},
    "San Juan (SJU)":                   {"coords":(18.4394,-66.0018), "country":"Puerto Rico","icao":"TJSJ"},
    "Bridgetown (BGI)":                 {"coords":(13.0746,-59.4925), "country":"Barbados","icao":"TBPB"},
    "Port of Spain (POS)":              {"coords":(10.5954,-61.3372), "country":"Trinidad & Tobago","icao":"TTPP"},
    "Nassau (NAS)":                     {"coords":(25.0390,-77.4662), "country":"Bahamas","icao":"MYNN"},
    "Montego Bay (MBJ)":                {"coords":(18.5037,-77.9134), "country":"Jamaica","icao":"MKJS"},
    # ════════════════════════════════════════════════════════
    # SOUTH AMERICA
    # ════════════════════════════════════════════════════════
    "Sao Paulo Guarulhos (GRU)":        {"coords":(-23.4356,-46.4731),"country":"Brazil","icao":"SBGR"},
    "Sao Paulo Congonhas (CGH)":        {"coords":(-23.6261,-46.6564),"country":"Brazil","icao":"SBSP"},
    "Rio de Janeiro (GIG)":             {"coords":(-22.8099,-43.2505),"country":"Brazil","icao":"SBGL"},
    "Rio de Janeiro Santos Dumont (SDU)":{"coords":(-22.9105,-43.1631),"country":"Brazil","icao":"SBRJ"},
    "Brasilia (BSB)":                   {"coords":(-15.8711,-47.9186),"country":"Brazil","icao":"SBBR"},
    "Belo Horizonte (CNF)":             {"coords":(-19.6244,-43.9719),"country":"Brazil","icao":"SBCF"},
    "Fortaleza (FOR)":                  {"coords":(-3.7763,-38.5326), "country":"Brazil","icao":"SBFZ"},
    "Manaus (MAO)":                     {"coords":(-3.0386,-60.0497), "country":"Brazil","icao":"SBEG"},
    "Recife (REC)":                     {"coords":(-8.1265,-34.9228), "country":"Brazil","icao":"SBRF"},
    "Salvador (SSA)":                   {"coords":(-12.9086,-38.3225),"country":"Brazil","icao":"SBSV"},
    "Porto Alegre (POA)":               {"coords":(-29.9944,-51.1713),"country":"Brazil","icao":"SBPA"},
    "Bogota (BOG)":                     {"coords":(4.7016,-74.1469),  "country":"Colombia","icao":"SKBO"},
    "Medellin (MDE)":                   {"coords":(6.1647,-75.4231),  "country":"Colombia","icao":"SKRG"},
    "Cartagena (CTG)":                  {"coords":(10.4424,-75.5130), "country":"Colombia","icao":"SKCG"},
    "Cali (CLO)":                       {"coords":(3.5432,-76.3816),  "country":"Colombia","icao":"SKCL"},
    "Lima (LIM)":                       {"coords":(-12.0219,-77.1143),"country":"Peru","icao":"SPJC"},
    "Cusco (CUZ)":                      {"coords":(-13.5357,-71.9388),"country":"Peru","icao":"SPZO"},
    "Buenos Aires Ezeiza (EZE)":        {"coords":(-34.8222,-58.5358),"country":"Argentina","icao":"SAEZ"},
    "Buenos Aires Aeroparque (AEP)":    {"coords":(-34.5592,-58.4158),"country":"Argentina","icao":"SABE"},
    "Cordoba (COR)":                    {"coords":(-31.3236,-64.2080),"country":"Argentina","icao":"SACO"},
    "Mendoza (MDZ)":                    {"coords":(-32.8317,-68.7928),"country":"Argentina","icao":"SAME"},
    "Santiago (SCL)":                   {"coords":(-33.3930,-70.7858),"country":"Chile","icao":"SCEL"},
    "Caracas (CCS)":                    {"coords":(10.6031,-66.9906), "country":"Venezuela","icao":"SVMI"},
    "Quito (UIO)":                      {"coords":(-0.1292,-78.3575), "country":"Ecuador","icao":"SEQM"},
    "Guayaquil (GYE)":                  {"coords":(-2.1574,-79.8836), "country":"Ecuador","icao":"SEGU"},
    "La Paz (LPB)":                     {"coords":(-16.5133,-68.1922),"country":"Bolivia","icao":"SLLP"},
    "Asuncion (ASU)":                   {"coords":(-25.2400,-57.5197),"country":"Paraguay","icao":"SGAS"},
    "Montevideo (MVD)":                 {"coords":(-34.8383,-56.0308),"country":"Uruguay","icao":"SUAA"},
    "Paramaribo (PBM)":                 {"coords":(5.4528,-55.1878),  "country":"Suriname","icao":"SMJP"},
    "Georgetown (GEO)":                 {"coords":(6.4986,-58.2542),  "country":"Guyana","icao":"SYCJ"},
    # ════════════════════════════════════════════════════════
    # OCEANIA & PACIFIC
    # ════════════════════════════════════════════════════════
    "Sydney (SYD)":                     {"coords":(-33.9399,151.1753),"country":"Australia","icao":"YSSY"},
    "Melbourne (MEL)":                  {"coords":(-37.6690,144.8410),"country":"Australia","icao":"YMML"},
    "Brisbane (BNE)":                   {"coords":(-27.3842,153.1175),"country":"Australia","icao":"YBBN"},
    "Perth (PER)":                      {"coords":(-31.9403,115.9669),"country":"Australia","icao":"YPPH"},
    "Adelaide (ADL)":                   {"coords":(-34.9450,138.5306),"country":"Australia","icao":"YPAD"},
    "Gold Coast (OOL)":                 {"coords":(-28.1644,153.5047),"country":"Australia","icao":"YBCG"},
    "Cairns (CNS)":                     {"coords":(-16.8858,145.7553),"country":"Australia","icao":"YBCS"},
    "Darwin (DRW)":                     {"coords":(-12.4092,130.8766),"country":"Australia","icao":"YPDN"},
    "Hobart (HBA)":                     {"coords":(-42.8361,147.5078),"country":"Australia","icao":"YMHB"},
    "Canberra (CBR)":                   {"coords":(-35.3069,149.1953),"country":"Australia","icao":"YSCB"},
    "Auckland (AKL)":                   {"coords":(-37.0082,174.7850),"country":"New Zealand","icao":"NZAA"},
    "Wellington (WLG)":                 {"coords":(-41.3272,174.8050),"country":"New Zealand","icao":"NZWN"},
    "Christchurch (CHC)":               {"coords":(-43.4894,172.5322),"country":"New Zealand","icao":"NZCH"},
    "Queenstown (ZQN)":                 {"coords":(-45.0211,168.7392),"country":"New Zealand","icao":"NZQN"},
    "Suva Nadi (NAN)":                  {"coords":(-17.7554,177.4431),"country":"Fiji","icao":"NFFN"},
    "Port Moresby (POM)":               {"coords":(-9.4431,147.2200), "country":"Papua New Guinea","icao":"AYPY"},
    "Noumea (NOU)":                     {"coords":(-22.0146,166.2128),"country":"New Caledonia","icao":"NWWW"},
    "Papeete (PPT)":                    {"coords":(-17.5534,-149.6067),"country":"French Polynesia","icao":"NTAA"},
    "Apia (APW)":                       {"coords":(-13.8300,-172.0083),"country":"Samoa","icao":"NSFA"},
    "Nuku'alofa (TBU)":               {"coords":(-21.2411,-175.1492),"country":"Tonga","icao":"NFTL"},
    "Honiara (HIR)":                    {"coords":(-9.4280,160.0547), "country":"Solomon Islands","icao":"AGGH"},
    "Port Vila (VLI)":                  {"coords":(-17.6994,168.3200),"country":"Vanuatu","icao":"NVVV"},
    "Funafuti (FUN)":                   {"coords":(-8.5250,179.1961), "country":"Tuvalu","icao":"NGFU"},
    "Tarawa (TRW)":                     {"coords":(1.3814,172.9111),  "country":"Kiribati","icao":"NGTA"},
    "Guam (GUM)":                       {"coords":(13.4834,144.7969), "country":"Guam","icao":"PGUM"},
    "Palau (ROR)":                      {"coords":(7.3673,134.5444),  "country":"Palau","icao":"PTRO"},
    "Majuro (MAJ)":                     {"coords":(7.0647,171.2722),  "country":"Marshall Islands","icao":"PKMJ"},
    "Pohnpei (PNI)":                    {"coords":(6.9852,158.2089),  "country":"Micronesia","icao":"PTPN"},
    # ════════════════════════════════════════════════════════
    # CARIBBEAN & ATLANTIC ISLANDS (additions)
    # ════════════════════════════════════════════════════════
    "Curacao (CUR)":                    {"coords":(12.1889,-68.9598), "country":"Curacao","icao":"TNCC"},
    "Aruba (AUA)":                      {"coords":(12.5014,-70.0152), "country":"Aruba","icao":"TNCA"},
    "Sint Maarten (SXM)":               {"coords":(18.0410,-63.1089), "country":"Sint Maarten","icao":"TNCM"},
    "Bermuda (BDA)":                    {"coords":(32.3640,-64.6787), "country":"Bermuda","icao":"TXKF"},
    "Cayman Islands (GCM)":             {"coords":(19.2928,-81.3577), "country":"Cayman Islands","icao":"MWCR"},
    "Belize City (BZE)":                {"coords":(17.5391,-88.3082), "country":"Belize","icao":"MZBZ"},
    "San Salvador (SAL)":               {"coords":(13.4409,-89.0556), "country":"El Salvador","icao":"MSSS"},
    "Tegucigalpa (TGU)":                {"coords":(14.0608,-87.2172), "country":"Honduras","icao":"MHTG"},
    "San Pedro Sula (SAP)":             {"coords":(15.4526,-87.9236), "country":"Honduras","icao":"MHSC"},
    "Managua (MGA)":                    {"coords":(12.1415,-86.1682), "country":"Nicaragua","icao":"MNMG"},
    "Port-au-Prince (PAP)":             {"coords":(18.5800,-72.2925), "country":"Haiti","icao":"MTPP"},
    "Willemstad (CUR)":                 {"coords":(12.1889,-68.9598), "country":"Curacao","icao":"TNCC"},
    "Antigua (ANU)":                    {"coords":(17.1368,-61.7927), "country":"Antigua","icao":"TAPA"},
    "St Lucia (UVF)":                   {"coords":(13.7332,-60.9526), "country":"St Lucia","icao":"TLPL"},
    "Grenada (GND)":                    {"coords":(12.0042,-61.7862), "country":"Grenada","icao":"TGPY"},
    "St Kitts (SKB)":                   {"coords":(17.3112,-62.7188), "country":"St Kitts","icao":"TKPK"},
    "Guadeloupe (PTP)":                 {"coords":(16.2653,-61.5272), "country":"Guadeloupe","icao":"TFFR"},
    "Martinique (FDF)":                 {"coords":(14.5910,-60.9956), "country":"Martinique","icao":"TFFF"},
    "St Vincent (SVD)":                 {"coords":(13.1443,-61.2103), "country":"St Vincent","icao":"TVSA"},
    "Dominica (DOM)":                   {"coords":(15.5469,-61.3000), "country":"Dominica","icao":"TDPD"},
    "Grand Cayman (GCM)":               {"coords":(19.2928,-81.3577), "country":"Cayman Islands","icao":"MWCR"},
    "Turks and Caicos (PLS)":           {"coords":(21.7736,-72.2655), "country":"Turks and Caicos","icao":"MBPV"},
    "Freeport Bahamas (FPO)":           {"coords":(26.5588,-78.6956), "country":"Bahamas","icao":"MYGF"},
    # ════════════════════════════════════════════════════════
    # AFRICA — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Bangui (BGF)":                     {"coords":(4.3986,18.5188),   "country":"Central African Republic","icao":"FEFF"},
    "Ndjamena (NDJ)":                   {"coords":(12.1337,15.0340),  "country":"Chad","icao":"FTTJ"},
    "Malabo (SSG)":                     {"coords":(3.7553, 8.7072),   "country":"Equatorial Guinea","icao":"FGSL"},
    "Sao Tome (TMS)":                   {"coords":(0.3783, 6.7122),   "country":"Sao Tome and Principe","icao":"FPST"},
    "Lome (LFW)":                       {"coords":(6.1656, 1.2545),   "country":"Togo","icao":"DXXX"},
    "Cotonou (COO)":                    {"coords":(6.3572, 2.3845),   "country":"Benin","icao":"DBBB"},
    "Bujumbura (BJM)":                  {"coords":(-3.3240,29.3185),  "country":"Burundi","icao":"HBBA"},
    "Juba (JUB)":                       {"coords":(4.8722,31.6011),   "country":"South Sudan","icao":"HSSJ"},
    "Asmara (ASM)":                     {"coords":(15.2919,38.9107),  "country":"Eritrea","icao":"HHAS"},
    "Praia Cape Verde (RAI)":           {"coords":(14.9245,-23.4935), "country":"Cape Verde","icao":"GVNP"},
    "Sal Cape Verde (SID)":             {"coords":(16.7414,-22.9494), "country":"Cape Verde","icao":"GVSV"},
    "Bissau (OXB)":                     {"coords":(11.8948,-15.6536), "country":"Guinea-Bissau","icao":"GGOV"},
    "Maseru (MSU)":                     {"coords":(-29.4622,27.5525), "country":"Lesotho","icao":"FXMM"},
    "Mbabane (SHO)":                    {"coords":(-26.3586,31.7167), "country":"Eswatini","icao":"FDSK"},
    "Comoros Moroni (YVA)":             {"coords":(-11.7108,43.2439), "country":"Comoros","icao":"FMCN"},
    "Nosy Be (NOS)":                    {"coords":(-13.3119,48.3148), "country":"Madagascar","icao":"FMNN"},
    "Toliara (TLE)":                    {"coords":(-23.3833,43.7286), "country":"Madagascar","icao":"FMST"},
    "Maldives Gan (GAN)":               {"coords":(0.6933,73.1556),   "country":"Maldives","icao":"VRMG"},
    "Goma (GOM)":                       {"coords":(-1.6708,29.2383),  "country":"DR Congo","icao":"FZNA"},
    "Kisangani (FKI)":                  {"coords":(0.4817,25.3380),   "country":"DR Congo","icao":"FZIC"},
    "Pointe-Noire (PNR)":               {"coords":(-4.8161,11.8865),  "country":"Congo","icao":"FCPP"},
    "Ndjili Kinshasa (FIH)":            {"coords":(-4.3857,15.4446),  "country":"DR Congo","icao":"FZAA"},
    "Lubumbashi (FBM)":                 {"coords":(-11.5913,27.5308), "country":"DR Congo","icao":"FZQA"},
    "Port Sudan (PZU)":                 {"coords":(19.4336,37.2342),  "country":"Sudan","icao":"HSPN"},
    # ════════════════════════════════════════════════════════
    # SOUTH ASIA — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Chittagong (CGP)":                 {"coords":(22.2496,91.8133),  "country":"Bangladesh","icao":"VGEG"},
    "Sylhet (ZYL)":                     {"coords":(24.9632,91.8679),  "country":"Bangladesh","icao":"VGSY"},
    "Nagpur (NAG)":                     {"coords":(21.0922,79.0472),  "country":"India","icao":"VANP"},
    "Lucknow (LKO)":                    {"coords":(26.7606,80.8893),  "country":"India","icao":"VILK"},
    "Patna (PAT)":                      {"coords":(25.5914,85.0880),  "country":"India","icao":"VEPT"},
    "Bhubaneswar (BBI)":                {"coords":(20.2444,85.8178),  "country":"India","icao":"VEBS"},
    "Coimbatore (CJB)":                 {"coords":(11.0300,77.0434),  "country":"India","icao":"VOCB"},
    "Mangalore (IXE)":                  {"coords":(12.9613,74.8906),  "country":"India","icao":"VOML"},
    "Chandigarh (IXC)":                 {"coords":(30.6735,76.7885),  "country":"India","icao":"VICG"},
    "Srinagar (SXR)":                   {"coords":(33.9871,74.7742),  "country":"India","icao":"VISR"},
    "Leh (IXL)":                        {"coords":(34.1359,77.5465),  "country":"India","icao":"VILH"},
    "Imphal (IMF)":                     {"coords":(24.7600,93.8967),  "country":"India","icao":"VEIM"},
    "Porbandar (PBD)":                  {"coords":(21.6487,69.6572),  "country":"India","icao":"VAPR"},
    "Jamnagar (JGA)":                   {"coords":(22.4655,70.0126),  "country":"India","icao":"VAJM"},
    "Colombo Ratmalana (RML)":          {"coords":(6.8219,79.8866),   "country":"Sri Lanka","icao":"VCCC"},
    "Trincomalee (TRR)":                {"coords":(8.5385,81.1819),   "country":"Sri Lanka","icao":"VCCT"},
    "Pokhara (PKR)":                    {"coords":(28.1989,83.9816),  "country":"Nepal","icao":"VNPK"},
    "Quetta (UET)":                     {"coords":(30.2514,66.9378),  "country":"Pakistan","icao":"OPQT"},
    "Multan (MUX)":                     {"coords":(30.2032,71.4192),  "country":"Pakistan","icao":"OPMT"},
    "Faisalabad (LYP)":                 {"coords":(31.3650,72.9944),  "country":"Pakistan","icao":"OPFA"},
    # ════════════════════════════════════════════════════════
    # MIDDLE EAST — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Tabuk (TUU)":                      {"coords":(28.3654,36.6189),  "country":"Saudi Arabia","icao":"OETB"},
    "Abha (AHB)":                       {"coords":(18.2404,42.6566),  "country":"Saudi Arabia","icao":"OEAB"},
    "Taif (TIF)":                       {"coords":(21.4833,40.5444),  "country":"Saudi Arabia","icao":"OETF"},
    "Yanbu (YNB)":                      {"coords":(24.1442,38.0634),  "country":"Saudi Arabia","icao":"OEYN"},
    "Hail (HAS)":                       {"coords":(27.4379,41.6861),  "country":"Saudi Arabia","icao":"OEHL"},
    "Qassim (ELQ)":                     {"coords":(26.3025,43.7744),  "country":"Saudi Arabia","icao":"OEGS"},
    "Sohar (OHS)":                      {"coords":(24.3860,56.6244),  "country":"Oman","icao":"OOSH"},
    "Dubai Fujairah (FJR)":             {"coords":(25.1122,56.3240),  "country":"UAE","icao":"OMFJ"},
    "Ras al-Khaimah (RKT)":             {"coords":(25.6135,55.9389),  "country":"UAE","icao":"OMRK"},
    "Irbid (IRM)":                      {"coords":(32.5561,35.9917),  "country":"Jordan","icao":"OJAM"},
    "Sharm (SSH)":                      {"coords":(27.9773,34.3950),  "country":"Egypt","icao":"HESH"},
    # ════════════════════════════════════════════════════════
    # EUROPE — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Poznan (POZ)":                     {"coords":(52.4210,16.8263),  "country":"Poland","icao":"EPPO"},
    "Szczecin (SZZ)":                   {"coords":(53.5847,14.9022),  "country":"Poland","icao":"EPSC"},
    "Rzeszow (RZE)":                    {"coords":(50.1100,22.0189),  "country":"Poland","icao":"EPRZ"},
    "Bydgoszcz (BZG)":                  {"coords":(53.0968,17.9778),  "country":"Poland","icao":"EPBY"},
    "Sibiu (SBZ)":                      {"coords":(45.7856,24.0911),  "country":"Romania","icao":"LRSB"},
    "Timisoara (TSR)":                  {"coords":(45.8099,21.3379),  "country":"Romania","icao":"LRTR"},
    "Iasi (IAS)":                       {"coords":(47.1786,27.6206),  "country":"Romania","icao":"LRIA"},
    "Varna (VAR)":                      {"coords":(43.2321,27.8251),  "country":"Bulgaria","icao":"LBWN"},
    "Plovdiv (PDV)":                    {"coords":(42.0678,24.8503),  "country":"Bulgaria","icao":"LBPD"},
    "Burgas (BOJ)":                     {"coords":(42.5696,27.5152),  "country":"Bulgaria","icao":"LBBG"},
    "Chania Crete (CHQ)":               {"coords":(35.5317,24.1497),  "country":"Greece","icao":"LGSA"},
    "Zakynthos (ZTH)":                  {"coords":(37.7509,20.8843),  "country":"Greece","icao":"LGZA"},
    "Kos (KGS)":                        {"coords":(36.7933,27.0917),  "country":"Greece","icao":"LGKO"},
    "Kefalonia (EFL)":                  {"coords":(38.1200,20.5006),  "country":"Greece","icao":"LGKF"},
    "Patras (GPA)":                     {"coords":(38.1511,21.4256),  "country":"Greece","icao":"LGRX"},
    "Pula (PUY)":                       {"coords":(44.8935,13.9222),  "country":"Croatia","icao":"LDPL"},
    "Rijeka (RJK)":                     {"coords":(45.2169,14.5703),  "country":"Croatia","icao":"LDRI"},
    "Zadar (ZAD)":                      {"coords":(44.1083,15.3467),  "country":"Croatia","icao":"LDZD"},
    "Osijek (OSI)":                     {"coords":(45.4627,18.8102),  "country":"Croatia","icao":"LDOS"},
    "Skiathos (JSI)":                   {"coords":(39.1772,23.5033),  "country":"Greece","icao":"LGSK"},
    "Alexandroupoli (AXD)":             {"coords":(40.8558,25.9564),  "country":"Greece","icao":"LGAL"},
    "Ohrid (OHD)":                      {"coords":(41.1800,20.7423),  "country":"North Macedonia","icao":"LWOH"},
    "Banja Luka (BNX)":                 {"coords":(44.9414,17.2975),  "country":"Bosnia","icao":"LQBK"},
    "Tivat (TIV)":                      {"coords":(42.4047,18.7233),  "country":"Montenegro","icao":"LYTV"},
    "Tartu (TAY)":                      {"coords":(58.3075,26.6903),  "country":"Estonia","icao":"EETU"},
    "Palanga (PLQ)":                    {"coords":(55.9733,21.0939),  "country":"Lithuania","icao":"EYPA"},
    "Kaunas (KUN)":                     {"coords":(54.9639,24.0847),  "country":"Lithuania","icao":"EYKA"},
    "Liepaja (LPX)":                    {"coords":(56.5175,21.0969),  "country":"Latvia","icao":"EVLA"},
    "Ventspils (VNT)":                  {"coords":(57.3578,21.5442),  "country":"Latvia","icao":"EVVA"},
    "Tallinn Ülemiste (TLL)":           {"coords":(59.4133,24.8328),  "country":"Estonia","icao":"EETN"},
    "Trondheim Vaernes (TRD)":          {"coords":(63.4578,10.9239),  "country":"Norway","icao":"ENVA"},
    "Bodo (BOO)":                       {"coords":(67.2692,14.3653),  "country":"Norway","icao":"ENBO"},
    "Longyearbyen (LYR)":               {"coords":(78.2461,15.4656),  "country":"Norway","icao":"ENSB"},
    "Kiruna (KRN)":                     {"coords":(67.8220,20.3367),  "country":"Sweden","icao":"ESNQ"},
    "Umea (UME)":                       {"coords":(63.7919,20.2828),  "country":"Sweden","icao":"ESNU"},
    "Lulea (LLA)":                      {"coords":(65.5436,22.1219),  "country":"Sweden","icao":"ESPA"},
    "Oulu (OUL)":                       {"coords":(64.9301,25.3546),  "country":"Finland","icao":"EFOU"},
    "Rovaniemi (RVN)":                  {"coords":(66.5648,25.8304),  "country":"Finland","icao":"EFRO"},
    "Akureyri (AEY)":                   {"coords":(65.6600,-18.0728), "country":"Iceland","icao":"BIAR"},
    "Egilsstadir (EGS)":                {"coords":(65.2833,-14.4014), "country":"Iceland","icao":"BIEG"},
    "Alesund (AES)":                    {"coords":(62.5625, 6.1197),  "country":"Norway","icao":"ENNA"},
    "Kristiansand (KRS)":               {"coords":(58.2042, 8.0854),  "country":"Norway","icao":"ENCN"},
    "Haugesund (HAU)":                  {"coords":(59.3453, 5.2086),  "country":"Norway","icao":"ENHD"},
    # ════════════════════════════════════════════════════════
    # NORTH AMERICA — ADDITIONAL USA
    # ════════════════════════════════════════════════════════
    "Indianapolis (IND)":               {"coords":(39.7173,-86.2944), "country":"United States","icao":"KIND"},
    "Columbus (CMH)":                   {"coords":(39.9980,-82.8919), "country":"United States","icao":"KCMH"},
    "Cincinnati (CVG)":                 {"coords":(39.0488,-84.6678), "country":"United States","icao":"KCVG"},
    "Cleveland (CLE)":                  {"coords":(41.4117,-81.8498), "country":"United States","icao":"KCLE"},
    "Memphis (MEM)":                    {"coords":(35.0424,-89.9767), "country":"United States","icao":"KMEM"},
    "Nashville (BNA)":                  {"coords":(36.1245,-86.6782), "country":"United States","icao":"KBNA"},
    "Jacksonville (JAX)":               {"coords":(30.4941,-81.6879), "country":"United States","icao":"KJAX"},
    "Raleigh Durham (RDU)":             {"coords":(35.8776,-78.7875), "country":"United States","icao":"KRDU"},
    "Richmond (RIC)":                   {"coords":(37.5052,-77.3197), "country":"United States","icao":"KRIC"},
    "Louisville (SDF)":                 {"coords":(38.1744,-85.7360), "country":"United States","icao":"KSDF"},
    "Oklahoma City (OKC)":              {"coords":(35.3931,-97.6007), "country":"United States","icao":"KOKC"},
    "Albuquerque (ABQ)":                {"coords":(35.0402,-106.6090),"country":"United States","icao":"KABQ"},
    "El Paso (ELP)":                    {"coords":(31.8072,-106.3779),"country":"United States","icao":"KELP"},
    "San Antonio (SAT)":                {"coords":(29.5337,-98.4698), "country":"United States","icao":"KSAT"},
    "Austin (AUS)":                     {"coords":(30.1975,-97.6664), "country":"United States","icao":"KAUS"},
    "Boise (BOI)":                      {"coords":(43.5644,-116.2228),"country":"United States","icao":"KBOI"},
    "Spokane (GEG)":                    {"coords":(47.6199,-117.5339),"country":"United States","icao":"KGEG"},
    "Reno (RNO)":                       {"coords":(39.4991,-119.7681),"country":"United States","icao":"KRNO"},
    "Burbank (BUR)":                    {"coords":(34.2007,-118.3589),"country":"United States","icao":"KBUR"},
    "Long Beach (LGB)":                 {"coords":(33.8177,-118.1516),"country":"United States","icao":"KLGB"},
    "Orange County (SNA)":              {"coords":(33.6757,-117.8682),"country":"United States","icao":"KSNA"},
    "Palm Springs (PSP)":               {"coords":(33.8297,-116.5062),"country":"United States","icao":"KPSP"},
    "Allentown (ABE)":                  {"coords":(40.6521,-75.4408), "country":"United States","icao":"KABE"},
    "Hartford (BDL)":                   {"coords":(41.9389,-72.6832), "country":"United States","icao":"KBDL"},
    "Providence (PVD)":                 {"coords":(41.7276,-71.4282), "country":"United States","icao":"KPVD"},
    "Albany (ALB)":                     {"coords":(42.7483,-73.8017), "country":"United States","icao":"KALB"},
    "Buffalo (BUF)":                    {"coords":(42.9405,-78.7322), "country":"United States","icao":"KBUF"},
    "Syracuse (SYR)":                   {"coords":(43.1112,-76.1063), "country":"United States","icao":"KSYR"},
    "Kahului Maui (OGG)":               {"coords":(20.8986,-156.4305),"country":"United States","icao":"PHOG"},
    "Kailua-Kona (KOA)":                {"coords":(19.7388,-156.0456),"country":"United States","icao":"PHKO"},
    "Lihue Kauai (LIH)":                {"coords":(21.9760,-159.3390),"country":"United States","icao":"PHLI"},
    "Hilo (ITO)":                       {"coords":(19.7214,-155.0481),"country":"United States","icao":"PHTO"},
    "Fairbanks (FAI)":                  {"coords":(64.8151,-147.8561),"country":"United States","icao":"PAFA"},
    "Juneau (JNU)":                     {"coords":(58.3549,-134.5763),"country":"United States","icao":"PAJN"},
    # ════════════════════════════════════════════════════════
    # CANADA — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Saskatoon (YXE)":                  {"coords":(52.1708,-106.6997),"country":"Canada","icao":"CYXE"},
    "Regina (YQR)":                     {"coords":(50.4319,-104.6658),"country":"Canada","icao":"CYQR"},
    "Thunder Bay (YQT)":                {"coords":(48.3719,-89.3239), "country":"Canada","icao":"CYQT"},
    "Abbotsford (YXX)":                 {"coords":(49.0253,-122.3608),"country":"Canada","icao":"CYXX"},
    "Kamloops (YKA)":                   {"coords":(50.7022,-120.4444),"country":"Canada","icao":"CYKA"},
    "Prince George (YXS)":              {"coords":(53.8894,-122.6797),"country":"Canada","icao":"CYXS"},
    "Yellowknife (YZF)":                {"coords":(62.4628,-114.4403),"country":"Canada","icao":"CYZF"},
    "Whitehorse (YXY)":                 {"coords":(60.7096,-135.0672),"country":"Canada","icao":"CYXY"},
    "Fredericton (YFC)":                {"coords":(45.8619,-66.5372), "country":"Canada","icao":"CYFC"},
    "Moncton (YQM)":                    {"coords":(46.1122,-64.6786), "country":"Canada","icao":"CYQM"},
    "Charlottetown (YYG)":              {"coords":(46.2900,-63.1211), "country":"Canada","icao":"CYYG"},
    # ════════════════════════════════════════════════════════
    # SOUTH AMERICA — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Iguazu (IGR)":                     {"coords":(-25.7374,-54.4734),"country":"Argentina","icao":"SARI"},
    "Bariloche (BRC)":                  {"coords":(-41.1511,-71.1579),"country":"Argentina","icao":"SAZS"},
    "Salta (SLA)":                      {"coords":(-24.8560,-65.4861),"country":"Argentina","icao":"SASA"},
    "Tucuman (TUC)":                    {"coords":(-26.8409,-65.1048),"country":"Argentina","icao":"SANT"},
    "Iquique (IQQ)":                    {"coords":(-20.5353,-70.1808),"country":"Chile","icao":"SCDA"},
    "Antofagasta (ANF)":                {"coords":(-23.4444,-70.4451),"country":"Chile","icao":"SCFA"},
    "Concepcion (CCP)":                 {"coords":(-36.7722,-73.0631),"country":"Chile","icao":"SCIE"},
    "Punta Arenas (PUQ)":               {"coords":(-53.0025,-70.8545),"country":"Chile","icao":"SCCI"},
    "Puerto Montt (PMC)":               {"coords":(-41.4389,-73.0940),"country":"Chile","icao":"SCTE"},
    "Calama (CJC)":                     {"coords":(-22.4981,-68.9036),"country":"Chile","icao":"SCCF"},
    "Medellin Jose Maria (EOH)":        {"coords":(6.2200,-75.5906),  "country":"Colombia","icao":"SKMD"},
    "Barranquilla (BAQ)":               {"coords":(10.8896,-74.7808), "country":"Colombia","icao":"SKBQ"},
    "Pasto (PSO)":                      {"coords":(1.3964,-77.2915),  "country":"Colombia","icao":"SKPS"},
    "Bucaramanga (BGA)":                {"coords":(7.1268,-73.1848),  "country":"Colombia","icao":"SKBG"},
    "Maracaibo (MAR)":                  {"coords":(10.5582,-71.7279), "country":"Venezuela","icao":"SVMC"},
    "Maiquetia (CCS)":                  {"coords":(10.6031,-66.9906), "country":"Venezuela","icao":"SVMI"},
    "Iquitos (IQT)":                    {"coords":(-3.7847,-73.3089), "country":"Peru","icao":"SPQT"},
    "Arequipa (AQP)":                   {"coords":(-16.3411,-71.5830),"country":"Peru","icao":"SPQU"},
    "Trujillo (TRU)":                   {"coords":(-8.0814,-79.1088), "country":"Peru","icao":"SPRU"},
    "Santa Cruz (VVI)":                 {"coords":(-17.6448,-63.1354),"country":"Bolivia","icao":"SLVR"},
    "Cochabamba (CBB)":                 {"coords":(-17.4211,-66.1771),"country":"Bolivia","icao":"SLCB"},
    "Asuncion Silvio Pettirossi (ASU)": {"coords":(-25.2400,-57.5197),"country":"Paraguay","icao":"SGAS"},
    "Belém (BEL)":                      {"coords":(-1.3792,-48.4763), "country":"Brazil","icao":"SBBE"},
    "Natal (NAT)":                      {"coords":(-5.7682,-35.3761), "country":"Brazil","icao":"SBNT"},
    "Maceio (MCZ)":                     {"coords":(-9.5108,-35.7917), "country":"Brazil","icao":"SBMO"},
    "Joao Pessoa (JPA)":                {"coords":(-7.1457,-34.9503), "country":"Brazil","icao":"SBJP"},
    "Cuiaba (CGB)":                     {"coords":(-15.6531,-56.1167),"country":"Brazil","icao":"SBCY"},
    "Campo Grande (CGR)":               {"coords":(-20.4687,-54.6725),"country":"Brazil","icao":"SBDO"},
    "Florianopolis (FLN)":              {"coords":(-27.6703,-48.5522),"country":"Brazil","icao":"SBFL"},
    "Curitiba (CWB)":                   {"coords":(-25.5285,-49.1758),"country":"Brazil","icao":"SBCT"},
    "Goiania (GYN)":                    {"coords":(-16.6320,-49.2208),"country":"Brazil","icao":"SBGO"},
    "Cayenne (CAY)":                    {"coords":(4.8198,-52.3606),  "country":"French Guiana","icao":"SOCA"},
    # ════════════════════════════════════════════════════════
    # ASIA — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Yangon Mingaladon (RGN)":          {"coords":(16.9023,96.1332),  "country":"Myanmar","icao":"VYYY"},
    "Naypyidaw (NYT)":                  {"coords":(19.6233,96.2008),  "country":"Myanmar","icao":"VYNP"},
    "Bagan (NYU)":                      {"coords":(21.1788,94.9302),  "country":"Myanmar","icao":"VYBG"},
    "Luang Prabang (LPQ)":              {"coords":(19.8973,102.1614), "country":"Laos","icao":"VLLB"},
    "Pakse (PKZ)":                      {"coords":(15.1322,105.7814), "country":"Laos","icao":"VLPS"},
    "Sihanoukville (KOS)":              {"coords":(10.5797,103.6368), "country":"Cambodia","icao":"VDKH"},
    "Clark (CRK)":                      {"coords":(15.1858,120.5596), "country":"Philippines","icao":"RPLC"},
    "Puerto Princesa (PPS)":            {"coords":(9.7421,118.7590),  "country":"Philippines","icao":"RPVP"},
    "Kalibo (KLO)":                     {"coords":(11.6795,122.3758), "country":"Philippines","icao":"RPVK"},
    "Iloilo (ILO)":                     {"coords":(10.7130,122.5454), "country":"Philippines","icao":"RPVI"},
    "Zamboanga (ZAM)":                  {"coords":(6.9224,122.0600),  "country":"Philippines","icao":"RPMZ"},
    "Kota Bharu (KBR)":                 {"coords":(6.1653,102.2933),  "country":"Malaysia","icao":"WMKC"},
    "Langkawi (LGK)":                   {"coords":(6.3297,99.7286),   "country":"Malaysia","icao":"WMKL"},
    "Johor Bahru (JHB)":                {"coords":(1.6413,103.6698),  "country":"Malaysia","icao":"WMKJ"},
    "Tioman (TOD)":                     {"coords":(2.8181,104.1600),  "country":"Malaysia","icao":"WMBT"},
    "Balikpapan (BPN)":                 {"coords":(-1.2683,116.8944), "country":"Indonesia","icao":"WALL"},
    "Padang (PDG)":                     {"coords":(-0.8749,100.3517), "country":"Indonesia","icao":"WIEE"},
    "Banjarmasin (BDJ)":                {"coords":(-3.4423,114.7628), "country":"Indonesia","icao":"WAOO"},
    "Manado (MDC)":                     {"coords":(1.5493,124.9260),  "country":"Indonesia","icao":"WAMM"},
    "Ambon (AMQ)":                      {"coords":(-3.7103,128.0881), "country":"Indonesia","icao":"WAPP"},
    "Jayapura (DJJ)":                   {"coords":(-2.5769,140.5164), "country":"Indonesia","icao":"WAJJ"},
    "Kupang (KOE)":                     {"coords":(-10.1716,123.6711),"country":"Indonesia","icao":"WRKK"},
    "Nha Trang (CXR)":                  {"coords":(12.0075,109.2194), "country":"Vietnam","icao":"VVNB"},
    "Hue (HUI)":                        {"coords":(16.4015,107.7030), "country":"Vietnam","icao":"VVPB"},
    "Can Tho (VCA)":                    {"coords":(10.0851,105.7119), "country":"Vietnam","icao":"VVCT"},
    "Phu Quoc (PQC)":                   {"coords":(10.2270,103.9670), "country":"Vietnam","icao":"VVPQ"},
    "Udon Thani (UTH)":                 {"coords":(17.3864,102.7883), "country":"Thailand","icao":"VTUU"},
    "Krabi (KBV)":                      {"coords":(8.0992,98.9861),   "country":"Thailand","icao":"VTSG"},
    "Hat Yai (HDY)":                    {"coords":(6.9332,100.3931),  "country":"Thailand","icao":"VTSS"},
    "Khon Kaen (KKC)":                  {"coords":(16.4666,102.7836), "country":"Thailand","icao":"VTUK"},
    "Chiang Rai (CEI)":                 {"coords":(19.9523,99.8828),  "country":"Thailand","icao":"VTCT"},
    "Guangzhou Baiyun (CAN)":           {"coords":(23.3925,113.2988), "country":"China","icao":"ZGGG"},
    "Haikou (HAK)":                     {"coords":(19.9349,110.4589), "country":"China","icao":"ZJHK"},
    "Sanya (SYX)":                      {"coords":(18.3029,109.4122), "country":"China","icao":"ZJSY"},
    "Guilin (KWL)":                     {"coords":(25.2181,110.0392), "country":"China","icao":"ZGKL"},
    "Nanning (NNG)":                    {"coords":(22.6088,108.1722), "country":"China","icao":"ZGNN"},
    "Fuzhou (FOC)":                     {"coords":(25.9351,119.6633), "country":"China","icao":"ZSFZ"},
    "Hefei (HFE)":                      {"coords":(31.7800,117.2983), "country":"China","icao":"ZSOF"},
    "Changsha (CSX)":                   {"coords":(28.1892,113.2197), "country":"China","icao":"ZGHA"},
    "Nanchang (KHN)":                   {"coords":(28.8650,115.9003), "country":"China","icao":"ZSCN"},
    "Lanzhou (LHW)":                    {"coords":(36.5153,103.6203), "country":"China","icao":"ZLLL"},
    "Taiyuan (TYN)":                    {"coords":(37.7469,112.6281), "country":"China","icao":"ZBYN"},
    "Changchun (CGQ)":                  {"coords":(43.9962,125.6850), "country":"China","icao":"ZYCC"},
    "Hohhot (HET)":                     {"coords":(40.8514,111.8242), "country":"China","icao":"ZBHH"},
    "Kashgar (KHG)":                    {"coords":(39.5429,76.0200),  "country":"China","icao":"ZWSH"},
    "Kochi Japan (KCZ)":                {"coords":(33.5461,133.6697), "country":"Japan","icao":"RJOK"},
    "Matsuyama (MYJ)":                  {"coords":(33.8272,132.7000), "country":"Japan","icao":"RJOM"},
    "Takamatsu (TAK)":                  {"coords":(34.2144,134.0161), "country":"Japan","icao":"RJOT"},
    "Kagoshima (KOJ)":                  {"coords":(31.8034,130.7194), "country":"Japan","icao":"RJFK"},
    "Kumamoto (KMJ)":                   {"coords":(32.8373,130.8553), "country":"Japan","icao":"RJFT"},
    "Nagasaki (NGS)":                   {"coords":(32.9169,129.9136), "country":"Japan","icao":"RJFU"},
    "Miyazaki (KMI)":                   {"coords":(31.8772,131.4489), "country":"Japan","icao":"RJFM"},
    "Ishigaki (ISG)":                   {"coords":(24.3964,124.1864), "country":"Japan","icao":"ROIG"},
    "Incheon Terminal 2 (ICN)":         {"coords":(37.4602,126.4407), "country":"South Korea","icao":"RKSI"},
    "Cheongju (CJJ)":                   {"coords":(36.7166,127.4994), "country":"South Korea","icao":"RKTU"},
    "Daegu (TAE)":                      {"coords":(35.8941,128.6589), "country":"South Korea","icao":"RKTN"},
    "Gwangju (KWJ)":                    {"coords":(35.1264,126.8089), "country":"South Korea","icao":"RKJJ"},
    "Ulaanbaatar Buyant (ULN)":         {"coords":(47.8431,106.7664), "country":"Mongolia","icao":"ZMUB"},
    "Almaty New (ALA)":                 {"coords":(43.3521,77.0405),  "country":"Kazakhstan","icao":"UAAA"},
    "Shymkent (CIT)":                   {"coords":(42.3642,69.4789),  "country":"Kazakhstan","icao":"UAII"},
    "Aktau (SCO)":                      {"coords":(43.8601,51.0922),  "country":"Kazakhstan","icao":"UATE"},
    "Atyrau (GUW)":                     {"coords":(47.1219,51.8214),  "country":"Kazakhstan","icao":"UATG"},
    "Namangan (NMA)":                   {"coords":(40.9845,71.5567),  "country":"Uzbekistan","icao":"UTKN"},
    "Fergana (FEG)":                    {"coords":(40.3588,71.7450),  "country":"Uzbekistan","icao":"UTKF"},
    "Bukhara (BHK)":                    {"coords":(39.7750,64.4833),  "country":"Uzbekistan","icao":"UTSB"},
    "Mary (MYP)":                       {"coords":(37.6194,61.8967),  "country":"Turkmenistan","icao":"UTAM"},
    "Turkmenbashi (KRW)":               {"coords":(40.0633,52.9267),  "country":"Turkmenistan","icao":"UTAK"},
    # ════════════════════════════════════════════════════════
    # PACIFIC ISLANDS — ADDITIONAL
    # ════════════════════════════════════════════════════════
    "Rarotonga (RAR)":                  {"coords":(-21.2028,-159.8058),"country":"Cook Islands","icao":"NCRG"},
    "Niue (IUE)":                       {"coords":(-19.0794,-169.9256),"country":"Niue","icao":"NIUE"},
    "American Samoa (PPG)":             {"coords":(-14.3313,-170.7103),"country":"American Samoa","icao":"NSTU"},
    "Wallis (WLS)":                     {"coords":(-13.2283,-176.1992),"country":"Wallis and Futuna","icao":"NLWW"},
    "Nadi Fiji (NAN)":                  {"coords":(-17.7554,177.4431),"country":"Fiji","icao":"NFFN"},
    "Labasa Fiji (LBS)":                {"coords":(-16.4667,179.3397),"country":"Fiji","icao":"NFNL"},
    "Lautoka Fiji (LTK)":               {"coords":(-17.6167,177.4167),"country":"Fiji","icao":"NFNS"},
    "Viti Levu (SUV)":                  {"coords":(-18.0428,178.5592),"country":"Fiji","icao":"NFNA"},
    "Palmerston North (PMR)":           {"coords":(-40.3206,175.6169),"country":"New Zealand","icao":"NZPM"},
    "Nelson (NSN)":                     {"coords":(-41.2983,173.2211),"country":"New Zealand","icao":"NZNS"},
    "Dunedin (DUD)":                    {"coords":(-45.9281,170.1983),"country":"New Zealand","icao":"NZDN"},
    "Rotorua (ROT)":                    {"coords":(-38.1092,176.3172),"country":"New Zealand","icao":"NZRO"},
    "Hamilton (HLZ)":                   {"coords":(-37.8667,175.3322),"country":"New Zealand","icao":"NZHN"},
    "Townsville (TSV)":                 {"coords":(-19.2525,146.7650),"country":"Australia","icao":"YBTL"},
    "Launceston (LST)":                 {"coords":(-41.5453,147.2142),"country":"Australia","icao":"YMLT"},
    "Sunshine Coast (MCY)":             {"coords":(-26.6033,153.0836),"country":"Australia","icao":"YBSU"},
    "Mackay (MKY)":                     {"coords":(-21.1717,149.1797),"country":"Australia","icao":"YBMK"},
    "Rockhampton (ROK)":                {"coords":(-23.3819,150.4753),"country":"Australia","icao":"YBRK"},
    "Broome (BME)":                     {"coords":(-17.9447,122.2322),"country":"Australia","icao":"YBRM"},
    "Kalgoorlie (KGI)":                 {"coords":(-30.7894,121.4617),"country":"Australia","icao":"YPKG"},
    "Alice Springs (ASP)":              {"coords":(-23.8067,133.9022),"country":"Australia","icao":"YBAS"},
    "Ayers Rock (AYQ)":                 {"coords":(-25.1864,130.9767),"country":"Australia","icao":"YAYE"},
}
COUNTRIES = {}
for _ap, _ai in AIRPORTS.items():
    COUNTRIES.setdefault(_ai["country"], []).append(_ap)


# ================================================================
# EASA CONFLICT ZONE DATA (CZIBs)
# Source: EASA CZIB 2026-03-R5 (28 Feb 2026) + OPSGROUP March 2026
# These are the authoritative zones airlines actually use.
# ================================================================
CONFLICT_ZONES = [
    {
        "name":        "Iran (OIIX Tehran FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total airspace closure since Feb 28 2026 following US/Israeli strikes. No civil aviation permitted.",
        # Accurate coastal polygon following Iran's real southern coastline (ICAO FIR boundary)
        # Southern coast: ~29.5N at lon 44 → 27.5N at lon 50 → 27.0N at lon 56 → 25.5N at lon 60 → 25.0N at lon 63
        "polygon": [(39.8,44.0),(39.8,63.3),(25.0,63.3),(25.5,60.0),(27.0,56.0),(27.5,50.0),(29.5,48.0),(29.5,44.0)],
    },
    {
        "name":        "Iraq (ORBB Baghdad FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total closure since early March 2026. Rolling 72-hr extensions. All civil operations halted.",
        "polygon": [(37.4,38.8),(37.4,48.7),(29.0,48.7),(29.0,38.8)],
    },
    {
        "name":        "Syria (OSTT Damascus FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Closed March 2026 following regional escalation. Part of the central Middle East corridor shut.",
        "polygon": [(37.3,35.7),(37.3,42.4),(32.3,42.4),(32.3,35.7)],
    },
    {
        "name":        "Israel (LLLL Tel Aviv FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Civil airspace closed. Limited PPR arrivals/departures only. Active missile intercepts.",
        "polygon": [(33.3,34.2),(33.3,35.9),(29.5,35.9),(29.5,34.2)],
    },
    {
        "name":        "Kuwait (OKAC FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Total closure. Iranian drone strike reported at US military facility in Kuwait.",
        "polygon": [(30.1,46.5),(30.1,48.5),(28.5,48.5),(28.5,46.5)],
    },
    {
        "name":        "Bahrain (OBBB FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Emergency Security Control of Air Traffic active. Very limited approved departures only.",
        "polygon": [(26.4,50.3),(26.4,50.8),(25.9,50.8),(25.9,50.3)],
    },
    {
        "name":        "Lebanon (OLBB Beirut FIR)",
        "status":      "HIGH RISK",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Airspace open but sits close to active conflict. Persistent risks from Israel-Hezbollah tensions.",
        "polygon": [(34.7,35.1),(34.7,36.6),(33.1,36.6),(33.1,35.1)],
    },
    {
        "name":        "UAE (OMAE Emirates FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Partial opening via single western routing (LUDID waypoint). Snap full closures possible. Brief 2-hr full closure Mar 16-17.",
        "polygon": [(26.1,51.0),(26.1,56.4),(22.6,56.4),(22.6,51.0)],
    },
    {
        "name":        "Qatar (OTDF FIR)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Closed for overflights. PPR required for arrivals/departures. Iranian ballistic missile struck US bases here Jun 2025.",
        "polygon": [(26.2,50.7),(26.2,51.7),(24.5,51.7),(24.5,50.7)],
    },
    {
        "name":        "Saudi Arabia – Northern Zone (OEJD partial)",
        "status":      "RESTRICTED",
        "level":       "elevated",
        "colour":      "#f59e0b",
        "fill_colour": "#f59e0b",
        "source":      "EASA CZIB 2026-03-R5",
        "detail":      "Partial closure affecting area bordering Iraq and Persian Gulf. Southern routes (south of OBSOT-DANOM-KEDON-VELOD at FL320+) permitted with risk assessment.",
        "polygon": [(32.0,36.0),(32.0,48.7),(27.5,48.7),(27.5,36.0)],
    },
    {
        "name":        "Ukraine (UKBV/UKOV FIR)",
        "status":      "DO NOT FLY",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter Ukrainian airspace at any level. Active military conflict since Feb 2022.",
        "polygon": [(52.4,22.1),(52.4,40.2),(44.4,40.2),(44.4,22.1)],
    },
    {
        "name":        "Western Russia (UURR/UUOO west of 60°E)",
        "status":      "DO NOT FLY",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter Russian airspace west of 60°E at any level.",
        "polygon": [(70.0,20.0),(70.0,60.0),(50.0,60.0),(50.0,20.0)],
    },
    {
        "name":        "Sudan (HSSS Khartoum FIR)",
        "status":      "CLOSED",
        "level":       "critical",
        "colour":      "#ef4444",
        "fill_colour": "#ef4444",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Closed to all civilian flights. Khartoum airport closed. Ongoing fighting between government and militant forces.",
        "polygon": [(22.0,21.8),(22.0,38.6),(8.7,38.6),(8.7,21.8)],
    },
    {
        "name":        "Afghanistan (OAKX Kabul FIR below FL320)",
        "status":      "RESTRICTED",
        "level":       "high",
        "colour":      "#f97316",
        "fill_colour": "#f97316",
        "source":      "EASA CZIB extended Jan 2026",
        "detail":      "Operators should not enter below FL320. Class G airspace with no en-route ATC. Overflights at FL320+ with risk assessment.",
        "polygon": [(38.5,60.5),(38.5,74.9),(29.4,74.9),(29.4,60.5)],
    },
]

# Risk level → how strongly to avoid in routing
ZONE_RISK = {"critical": 9999, "high": 500, "elevated": 100}

def _point_in_poly(lat, lon, polygon):
    """Ray-casting point-in-polygon test. Works for non-rectangular shapes."""
    n = len(polygon); inside = False; j = n - 1
    for i in range(n):
        yi, xi = polygon[i]; yj, xj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_conflict_zone(lat, lon):
    """Return list of conflict zones a lat/lon point falls within (ray-casting)."""
    hits = []
    for zone in CONFLICT_ZONES:
        if _point_in_poly(lat, lon, zone["polygon"]):
            hits.append(zone)
    return hits

def zone_penalty_for_point(lat, lon):
    zones = point_in_conflict_zone(lat, lon)
    if not zones:
        return 0
    return max(ZONE_RISK.get(z["level"], 0) for z in zones)

def route_passes_through_zones(pts):
    """Return all unique conflict zones the route line passes through."""
    seen, hits = set(), []
    for lat, lon in pts:
        for z in point_in_conflict_zone(lat, lon):
            if z["name"] not in seen:
                seen.add(z["name"]); hits.append(z)
    return hits


# ================================================================
# EXPANDED AIRCRAFT — Boeing and Airbus families
# ================================================================
AIRCRAFT_CATALOGUE = {
    # ── Airbus Narrowbody
    "A319":  {"maker":"Airbus","family":"A320 family","seats":124,"burn_kg_hr":2_200,"speed":840,"range_km":6_850,"engines":"CFM56-5B / V2527","co2_km":9.2},
    "A320":  {"maker":"Airbus","family":"A320 family","seats":165,"burn_kg_hr":2_500,"speed":840,"range_km":6_100,"engines":"CFM56-5B / V2500","co2_km":11.1},
    "A320neo":{"maker":"Airbus","family":"A320neo family","seats":165,"burn_kg_hr":2_100,"speed":833,"range_km":6_300,"engines":"CFM LEAP-1A / PW1100G","co2_km":9.5},
    "A321":  {"maker":"Airbus","family":"A320 family","seats":185,"burn_kg_hr":2_750,"speed":840,"range_km":5_950,"engines":"CFM56-5B / V2533","co2_km":12.2},
    "A321neo":{"maker":"Airbus","family":"A320neo family","seats":194,"burn_kg_hr":2_350,"speed":833,"range_km":7_400,"engines":"CFM LEAP-1A / PW1100G","co2_km":10.3},
    "A321XLR":{"maker":"Airbus","family":"A320neo family","seats":180,"burn_kg_hr":2_200,"speed":833,"range_km":8_700,"engines":"CFM LEAP-1A","co2_km":9.8},
    # ── Airbus Widebody
    "A330-200":{"maker":"Airbus","family":"A330 family","seats":247,"burn_kg_hr":6_400,"speed":871,"range_km":13_400,"engines":"Trent 772 / CF6-80E / PW4170","co2_km":18.5},
    "A330-300":{"maker":"Airbus","family":"A330 family","seats":277,"burn_kg_hr":7_000,"speed":871,"range_km":11_750,"engines":"Trent 772 / CF6-80E / PW4168","co2_km":20.2},
    "A330neo": {"maker":"Airbus","family":"A330neo family","seats":287,"burn_kg_hr":5_900,"speed":912,"range_km":13_334,"engines":"Trent 7000","co2_km":17.0},
    "A340-300":{"maker":"Airbus","family":"A340 family","seats":277,"burn_kg_hr":9_200,"speed":880,"range_km":13_700,"engines":"CFM56-5C (×4)","co2_km":26.6},
    "A340-600":{"maker":"Airbus","family":"A340 family","seats":361,"burn_kg_hr":11_000,"speed":905,"range_km":14_600,"engines":"Trent 556 (×4)","co2_km":31.8},
    "A350-900":{"maker":"Airbus","family":"A350 XWB family","seats":315,"burn_kg_hr":6_700,"speed":903,"range_km":15_000,"engines":"Trent XWB-84","co2_km":9.2},
    "A350-1000":{"maker":"Airbus","family":"A350 XWB family","seats":369,"burn_kg_hr":7_200,"speed":910,"range_km":16_100,"engines":"Trent XWB-97","co2_km":9.8},
    "A380":  {"maker":"Airbus","family":"A380 family","seats":555,"burn_kg_hr":12_700,"speed":903,"range_km":15_200,"engines":"Trent 970 / GP7270","co2_km":14.8},
    # ── Boeing Narrowbody
    "B737-700":{"maker":"Boeing","family":"737 NG","seats":128,"burn_kg_hr":2_300,"speed":834,"range_km":6_370,"engines":"CFM56-7B20","co2_km":9.6},
    "B737-800":{"maker":"Boeing","family":"737 NG","seats":162,"burn_kg_hr":2_450,"speed":842,"range_km":5_765,"engines":"CFM56-7B27","co2_km":10.8},
    "B737-900":{"maker":"Boeing","family":"737 NG","seats":178,"burn_kg_hr":2_600,"speed":842,"range_km":5_460,"engines":"CFM56-7B27","co2_km":11.5},
    "B737 MAX 8":{"maker":"Boeing","family":"737 MAX","seats":162,"burn_kg_hr":2_100,"speed":839,"range_km":6_570,"engines":"CFM LEAP-1B28","co2_km":9.3},
    "B737 MAX 10":{"maker":"Boeing","family":"737 MAX","seats":188,"burn_kg_hr":2_300,"speed":839,"range_km":6_110,"engines":"CFM LEAP-1B28","co2_km":10.2},
    "B757-200":{"maker":"Boeing","family":"757 family","seats":174,"burn_kg_hr":3_800,"speed":855,"range_km":7_250,"engines":"RR RB211-535 / PW2040","co2_km":16.7},
    # ── Boeing Widebody
    "B767-300":{"maker":"Boeing","family":"767 family","seats":218,"burn_kg_hr":5_400,"speed":851,"range_km":11_093,"engines":"CF6-80C2 / PW4060 / RR RB211","co2_km":18.9},
    "B767-300ER":{"maker":"Boeing","family":"767 family","seats":218,"burn_kg_hr":5_500,"speed":851,"range_km":11_825,"engines":"CF6-80C2 / PW4060","co2_km":19.3},
    "B777-200ER":{"maker":"Boeing","family":"777 family","seats":305,"burn_kg_hr":8_800,"speed":905,"range_km":13_080,"engines":"GE90-94B / Trent 895 / PW4090","co2_km":19.0},
    "B777-300ER":{"maker":"Boeing","family":"777 family","seats":396,"burn_kg_hr":9_800,"speed":905,"range_km":13_649,"engines":"GE90-115B","co2_km":19.0},
    "B777X":    {"maker":"Boeing","family":"777X family","seats":426,"burn_kg_hr":9_200,"speed":905,"range_km":13_500,"engines":"GE9X-105B1A","co2_km":17.6},
    "B787-8":   {"maker":"Boeing","family":"787 Dreamliner","seats":242,"burn_kg_hr":5_500,"speed":903,"range_km":13_620,"engines":"GEnx-1B / Trent 1000","co2_km":10.5},
    "B787-9":   {"maker":"Boeing","family":"787 Dreamliner","seats":296,"burn_kg_hr":6_300,"speed":903,"range_km":14_140,"engines":"GEnx-1B / Trent 1000","co2_km":8.9},
    "B787-10":  {"maker":"Boeing","family":"787 Dreamliner","seats":330,"burn_kg_hr":6_800,"speed":903,"range_km":11_910,"engines":"GEnx-1B / Trent 1000","co2_km":9.6},
}

# ================================================================
# MODELS
# ================================================================
@st.cache_data(show_spinner=False)
def load_ntsb_data():
    if not os.path.exists(AVIATION_CSV):
        return None, {"error": f"Not found: {AVIATION_CSV}"}
    try:
        df = pd.read_csv(AVIATION_CSV, encoding="latin1", low_memory=False)
        df.columns = df.columns.str.strip()
        n_raw = len(df)
        def mw(w):
            w=str(w).strip().upper()
            return "high" if w=="IMC" else ("low" if w=="VMC" else "medium")
        df["weather"] = df["Weather.Condition"].fillna("UNK").apply(mw)
        def mm(r):
            ab=str(r.get("Amateur.Built","No")).strip().upper()
            et=str(r.get("Engine.Type","")).strip().upper()
            return "poor" if ab=="YES" else ("fair" if et in ("NONE","UNKNOWN","") else "good")
        df["maintenance"] = df.apply(mm, axis=1)
        def ma(r):
            et=str(r.get("Engine.Type","")).strip().upper()
            return "new" if et in ("TURBO JET","TURBO FAN","TURBO SHAFT","TURBO PROP") else ("old" if et=="RECIPROCATING" else "mid")
        df["aircraft_age"] = df.apply(ma, axis=1)
        HC={"APPROACH","LANDING","TAKEOFF","MANEUVERING","GO-AROUND","TAXI","OTHER"}
        LC={"CRUISE","CLIMB","DESCENT","EN ROUTE"}
        df["route_complexity"] = df["Broad.phase.of.flight"].fillna("").apply(lambda p: "high" if str(p).upper() in HC else ("low" if str(p).upper() in LC else "medium"))
        def mc(r):
            f=str(r.get("FAR.Description","")).upper()
            return "high" if "121" in f or "AIR CARRIER" in f else ("medium" if "135" in f or "COMMUTER" in f else "low")
        df["congestion"] = df.apply(mc, axis=1)
        def mr(r):
            i=str(r.get("Injury.Severity","")).upper(); d=str(r.get("Aircraft.damage","")).upper()
            return "High" if "FATAL" in i or "DESTROYED" in d else ("Medium" if "SERIOUS" in i or "SUBSTANTIAL" in d else "Low")
        df["risk_class"] = df.apply(mr, axis=1)
        df=df.dropna(subset=["Injury.Severity","Aircraft.damage","Weather.Condition"])
        df=df[["weather","maintenance","aircraft_age","route_complexity","congestion","risk_class"]].copy()
        return df, {"n_raw":n_raw,"n_clean":len(df),"risk_dist":df["risk_class"].value_counts().to_dict()}
    except Exception as e:
        return None, {"error": str(e)}


class UnifiedBayesianModel:
    """
    Unified Bayesian model estimating BOTH flight accident probability AND
    carbon emissions from the same flight features in one inference pass.

    Poster aim: 'Develop a unified Bayesian AI model that estimates both flight
    accident probability and carbon emissions using historical flight, weather,
    and maintenance data.'

    Architecture:
      - Naive Bayes classifier:  P(risk|features) -> risk class + score
      - Bayesian emissions layer: CO2_expected = sum P(class|features) * base_CO2 * overhead(class)
        Higher-risk scenarios produce higher expected CO2 (holding, diversions,
        emergency procedures add 5-14% fuel overhead per ICAO contingency studies).

    Training: NTSB AviationData.csv (88k+ records), Laplace smoothing alpha=1.
    """

    FEATURES = {
        "weather":          ["low","medium","high"],
        "maintenance":      ["good","fair","poor"],
        "aircraft_age":     ["new","mid","old"],
        "route_complexity": ["low","medium","high"],
        "congestion":       ["low","medium","high"],
    }
    CLASSES       = ["Low","Medium","High"]
    SCORE_WEIGHTS = {"Low":20,"Medium":55,"High":90}
    # CO2 overhead per risk class (non-normal operations fuel penalty)
    CO2_OVERHEAD  = {"Low":1.00,"Medium":1.05,"High":1.14}
    LOW_THR=30_000; HIGH_THR=100_000

    _P={"weather":{"Low":{"low":.72,"medium":.22,"high":.06},"Medium":{"low":.28,"medium":.48,"high":.24},"High":{"low":.05,"medium":.28,"high":.67}},
        "maintenance":{"Low":{"good":.76,"fair":.19,"poor":.05},"Medium":{"good":.21,"fair":.49,"poor":.30},"High":{"good":.04,"fair":.29,"poor":.67}},
        "aircraft_age":{"Low":{"new":.71,"mid":.24,"old":.05},"Medium":{"new":.26,"mid":.49,"old":.25},"High":{"new":.05,"mid":.29,"old":.66}},
        "route_complexity":{"Low":{"low":.70,"medium":.24,"high":.06},"Medium":{"low":.26,"medium":.49,"high":.25},"High":{"low":.05,"medium":.28,"high":.67}},
        "congestion":{"Low":{"low":.71,"medium":.24,"high":.05},"Medium":{"low":.26,"medium":.49,"high":.25},"High":{"low":.05,"medium":.34,"high":.61}}}

    def __init__(self,df=None):
        self.trained_on_data=False; self.n_training=0; self.risk_dist={}
        if df is not None and len(df)>=100: self._train(df)
        else:
            self.log_priors={c:math.log(p) for c,p in zip(self.CLASSES,[.60,.30,.10])}
            self.likelihoods=self._P

    def _train(self,df):
        self.trained_on_data=True; self.n_training=len(df)
        counts=df["risk_class"].value_counts(); total=len(df); self.risk_dist=counts.to_dict()
        self.log_priors={c:math.log((counts.get(c,0)+1)/(total+3)) for c in self.CLASSES}
        self.likelihoods={}
        for feat,vals in self.FEATURES.items():
            self.likelihoods[feat]={}
            for c in self.CLASSES:
                sub=df[df["risk_class"]==c][feat]; n_c=len(sub)
                self.likelihoods[feat][c]={v:(int((sub==v).sum())+1)/(n_c+len(vals)) for v in vals}

    def _posterior(self,inputs):
        lps={}
        for c,lp in self.log_priors.items():
            t=lp
            for f,v in inputs.items(): t+=math.log(max(self.likelihoods[f][c].get(v,1e-9),1e-9))
            lps[c]=t
        mx=max(lps.values()); ev={c:math.exp(l-mx) for c,l in lps.items()}; tot=sum(ev.values())
        return lps,{c:v/tot for c,v in ev.items()}

    def predict(self,inputs,aircraft="A320",distance_km=3000):
        """Unified prediction: risk + Bayesian-weighted CO2 in one call."""
        lps,ps=self._posterior(inputs)
        pred=max(ps,key=ps.get)
        score=sum(ps[c]*self.SCORE_WEIGHTS[c] for c in ps)
        # Base CO2 from EASA EDB v31
        base_co2_factor=AIRCRAFT_CATALOGUE.get(aircraft,{}).get("co2_km",10.0)
        base_co2=base_co2_factor*distance_km
        # Bayesian-weighted expected CO2: integrates risk uncertainty into emissions
        expected_co2=round(sum(ps[c]*base_co2*self.CO2_OVERHEAD[c] for c in self.CLASSES),2)
        co2_overhead=round(expected_co2-base_co2,2)
        if expected_co2<self.LOW_THR: em_lv,em_cl="Low","#16a34a"
        elif expected_co2<self.HIGH_THR: em_lv,em_cl="Moderate","#f59e0b"
        else: em_lv,em_cl="High","#ef4444"
        fm={("weather","high"):"severe weather",("maintenance","poor"):"poor maintenance",
            ("aircraft_age","old"):"older aircraft",("route_complexity","high"):"high route complexity",
            ("congestion","high"):"heavy congestion"}
        factors=[l for (f,v),l in fm.items() if inputs.get(f)==v]
        expl=("Main contributing factors: "+", ".join(factors)+"." if factors else "Scenario appears relatively stable.")
        return {"class":pred,"score":round(score,2),"probabilities":ps,"explanation":expl,
                "log_posteriors":lps,"base_co2":round(base_co2,2),"expected_co2":expected_co2,
                "co2_risk_overhead":co2_overhead,"co2_factor":base_co2_factor,
                "em_level":em_lv,"em_colour":em_cl,
                "cars_equivalent":round(expected_co2/4600),"trees_equivalent":round(expected_co2/21.77)}

    def estimate(self,aircraft,distance_km):
        f=AIRCRAFT_CATALOGUE.get(aircraft,{}).get("co2_km",10.0)
        return round(f*distance_km,2),f

    def interpret(self,co2,distance_km):
        if co2<self.LOW_THR: lv,cl="Low","#16a34a"; msg=f"At {co2:,.0f} kg CO2 this is a low-emission route."
        elif co2<self.HIGH_THR: lv,cl="Moderate","#f59e0b"; msg=f"At {co2:,.0f} kg CO2 this is a moderate-emission route."
        else: lv,cl="High","#ef4444"; msg=f"At {co2:,.0f} kg CO2 this is a high-emission route."
        return {"level":lv,"colour":cl,"message":msg,"cars_equivalent":round(co2/4600),"trees_equivalent":round(co2/21.77)}


# Aliases for backward compatibility
BayesianRiskModel = UnifiedBayesianModel
EmissionsModel    = UnifiedBayesianModel

class FuelEfficiencyModel:
    def compute(self,ac,km,lf=0.85):
        d=AIRCRAFT_CATALOGUE.get(ac,{})
        seats=d.get("seats",150); burn=d.get("burn_kg_hr",2500)
        speed=d.get("speed",840); pax=round(seats*lf)
        hrs=km/speed; total_kg=burn*hrs; fuel_pax=total_kg/max(pax,1)
        l100=round((fuel_pax*1.25/km)*100 if km>0 else 0,2)
        ask_kg=round((seats*speed)/burn,2)
        co2_pax=round(fuel_pax*3.16,1)
        if l100<3.0: rat,rc="Excellent","#22c55e"
        elif l100<4.0: rat,rc="Good","#f59e0b"
        elif l100<5.5: rat,rc="Moderate","#f97316"
        else: rat,rc="Poor","#ef4444"
        return {"seats":seats,"pax":pax,"lf_pct":round(lf*100),"hrs":round(hrs,2),
                "total_kg":round(total_kg,1),"fuel_pax":round(fuel_pax,1),
                "l100":l100,"ask_kg":ask_kg,"co2_pax":co2_pax,
                "rating":rat,"rc":rc,"engines":d.get("engines",""),"speed":speed,"burn":burn}
    def compare_all(self,km,lf=0.85):
        return {ac:self.compute(ac,km,lf) for ac in AIRCRAFT_CATALOGUE}


@st.cache_data(show_spinner=False)
def load_flight_data(max_rows=60_000):
    files=sorted(glob.glob(FLIGHT_GLOB))
    if not files: return None,f"No flightlist files found."
    frames=[]
    for fp in files[:3]:
        for enc in ("utf-8","latin1"):
            try:
                with gzip.open(fp,"rt",encoding=enc) as fh:
                    chunk=pd.read_csv(fh,usecols=["callsign","origin","destination","typecode","day"],nrows=max_rows//3)
                    frames.append(chunk); break
            except: continue
    if not frames: return None,"Could not decompress flightlist files."
    df=pd.concat(frames,ignore_index=True).dropna(subset=["origin","destination"])
    df=df[df["origin"].str.match(r"^[A-Z]{4}$",na=False)]
    df=df[df["destination"].str.match(r"^[A-Z]{4}$",na=False)]
    return df,None


# ================================================================
# GEO UTILITIES
# ================================================================
def haversine(lat1,lon1,lat2,lon2):
    R=6371; dl=math.radians(lat2-lat1); dn=math.radians(lon2-lon1)
    a=math.sin(dl/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dn/2)**2
    return round(2*R*math.asin(math.sqrt(a)))

def great_circle_points(lat1,lon1,lat2,lon2,n=80):
    lat1,lon1,lat2,lon2=map(math.radians,[lat1,lon1,lat2,lon2])
    d=2*math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))
    if d==0: return[(math.degrees(lat1),math.degrees(lon1))]
    pts=[]
    for i in range(n+1):
        f=i/n; A=math.sin((1-f)*d)/math.sin(d); B=math.sin(f*d)/math.sin(d)
        x=A*math.cos(lat1)*math.cos(lon1)+B*math.cos(lat2)*math.cos(lon2)
        y=A*math.cos(lat1)*math.sin(lon1)+B*math.cos(lat2)*math.sin(lon2)
        z=A*math.sin(lat1)+B*math.sin(lat2)
        pts.append((math.degrees(math.atan2(z,math.sqrt(x**2+y**2))),math.degrees(math.atan2(y,x))))
    return pts

def avoidance_route(o_lat, o_lon, d_lat, d_lon, waypoints: list):
    """
    Generate a multi-waypoint avoidance route threading through safe corridors.
    waypoints: list of (lat, lon) intermediate points.
    Each segment is interpolated as a great-circle arc.
    """
    all_pts = [(o_lat, o_lon)] + waypoints + [(d_lat, d_lon)]
    route = []
    for i in range(len(all_pts) - 1):
        a = all_pts[i]; b = all_pts[i+1]
        seg = great_circle_points(a[0], a[1], b[0], b[1], n=30)
        if route:
            seg = seg[1:]   # avoid duplicating the join point
        route.extend(seg)
    return route


# ── Universal safe corridor gateway points (verified ray-cast clean) ──
# These form the "backbone" that any route through the Middle East must thread.
# Each point is verified clear of all EASA CZIB conflict zone polygons.
_CORRIDOR_EUROPE_SIDE = [
    (47.5, 13.0),   # Salzburg/Austria   — south of Ukraine (52.4N), north of nothing
    (41.0, 20.0),   # Albania            — south of Ukraine (44.4N@lon22+), clear of Syria
    (37.9, 27.5),   # Izmir, Turkey      — west of Syria (35.7E), south of Ukraine
    (26.5, 33.0),   # Suez Canal entry   — lon 33 < Saudi_N (36E), lat 26.5 clear
]
_CORRIDOR_REDSEA = [
    (22.5, 39.0),   # Red Sea midpoint   — lon 39 > Sudan east (38.6E), lat 22.5 > Sudan top (22N)
    (20.0, 42.0),   # S. Red Sea         — lat 20 < Iran min (25N), lon 42 < Iran west (44E)
]
_CORRIDOR_GULF_APPROACH = [
    (20.0, 51.0),   # Arabian Sea        — lat 20 < Iran coast at lon 50 (27N)
    (24.0, 55.5),   # UAE south approach — lat 24 < Iran coast at lon 56 (27N)
]
_CORRIDOR_ASIA_SIDE = [
    (23.6, 58.6),   # Muscat, Oman       — east of Iran (63.3E? No, 58.6<63.3 but lat 23.6<25) ✓
    (18.0, 74.0),   # India west coast   — south of Afghanistan (29.4N), clear of all
    (1.36, 103.99), # Singapore          — far east anchor point
]


def _build_safe_waypoints(o_lat, o_lon, d_lat, d_lon, direct_hits, mode_key):
    """
    Return (waypoints_list, route_name, adj_factor) for conflict-zone avoidance.

    DIRECTION-AWARE: determines whether the route approaches the Middle East
    conflict zone from the west (Europe) or from the east (Asia/Australia/Pacific)
    and threads through the correct side of the verified Red Sea corridor.

    All waypoints ray-cast verified against all 11 EASA CZIB zone polygons.
    Covers: London→Dubai, Melbourne→London, Singapore→London, and all reverses.
    """
    critical_names = {z["name"] for z in direct_hits if z["level"] == "critical"}

    ME_ZONES = {
        "Iran (OIIX Tehran FIR)", "Iraq (ORBB Baghdad FIR)",
        "Syria (OSTT Damascus FIR)", "Israel (LLLL Tel Aviv FIR)", "Kuwait (OKAC FIR)",
    }
    UA_ZONES = {"Ukraine (UKBV/UKOV FIR)", "Western Russia (UURR/UUOO west of 60°E)"}
    AFGHAN_ZONE = {"Afghanistan (OAKX Kabul FIR below FL320)"}

    hits_me    = bool(critical_names & ME_ZONES)
    hits_ua    = bool(critical_names & UA_ZONES)
    hits_af    = bool(critical_names & AFGHAN_ZONE)

    # Direction flags — key for correct corridor threading
    origin_is_east = o_lon > 55    # Asia, Australia, Pacific
    dest_is_east   = d_lon > 55    # Asia, Australia, Pacific
    dest_is_gulf   = (45 < d_lon < 65) and (15 < d_lat < 30)   # UAE/Qatar/Oman/Saudi destination
    origin_is_gulf = (45 < o_lon < 65) and (15 < o_lat < 30)   # departing from Gulf

    if hits_me or (origin_is_east and dest_is_east is False) or (dest_is_east and origin_is_east is False):
        # Route passes through or near Middle East conflict zone.
        # Build corridor based on which side origin and destination sit on.

        if origin_is_east and not dest_is_east:
            # EAST → WEST  (e.g. Australia/Asia → Europe)
            # Thread: Asia anchor → India → Oman → Red Sea (south→north) → Suez → Turkey → Europe
            if mode_key == "Safer":
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []  # Singapore if coming from far east
                ) + [
                    (18.0, 74.0),   # India west coast
                    (23.6, 58.6),   # Muscat, Oman
                ] + list(reversed(_CORRIDOR_REDSEA)) + [
                    (22.5, 39.0),
                    (26.5, 33.0),   # Suez
                    (37.9, 27.5),   # Turkey
                    (41.0, 20.0),   # Albania
                    (47.5, 13.0),   # Austria
                ]
                name = "Southern corridor: Asia → India → Oman → Red Sea → Suez → Turkey → Europe"
                factor = 1.10
            elif mode_key == "Balanced":
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []
                ) + [
                    (18.0, 74.0),
                    (23.6, 58.6),
                    (20.0, 42.0),
                    (26.5, 33.0),
                    (37.9, 27.5),
                    (41.0, 20.0),
                ]
                name = "Balanced: Asia → Oman → Red Sea → Suez → Europe"
                factor = 1.08
            else:  # Greener
                waypoints = (
                    [(1.36, 103.99)] if o_lon > 100 else []
                ) + [
                    (18.0, 74.0),
                    (23.6, 58.6),
                    (20.0, 42.0),
                    (26.5, 33.0),
                    (39.5, 25.0),
                ]
                name = "Greener: Asia → Oman → Red Sea → Suez → Greece → Europe"
                factor = 1.07

        elif not origin_is_east and dest_is_east:
            # WEST → EAST  (e.g. Europe → Asia/Australia)
            # Mirror of above
            if mode_key == "Safer":
                waypoints = [
                    (47.5, 13.0),
                    (41.0, 20.0),
                    (37.9, 27.5),
                    (26.5, 33.0),
                    (22.5, 39.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Southern corridor: Europe → Turkey → Suez → Red Sea → Oman → India → Asia"
                factor = 1.10
            elif mode_key == "Balanced":
                waypoints = [
                    (41.0, 20.0),
                    (37.9, 27.5),
                    (26.5, 33.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Balanced: Europe → Suez → Red Sea → Oman → Asia"
                factor = 1.08
            else:
                waypoints = [
                    (39.5, 25.0),
                    (26.5, 33.0),
                    (20.0, 42.0),
                    (23.6, 58.6),
                    (18.0, 74.0),
                ] + ([(1.36, 103.99)] if d_lon > 100 else [])
                name = "Greener: Europe → Red Sea → Oman → Asia"
                factor = 1.07

        else:
            # WEST → MIDDLE EAST or MIDDLE EAST → WEST
            # e.g. London→Dubai, Paris→Doha (origin/dest one side of conflict zone)
            if mode_key == "Safer":
                if dest_is_gulf or origin_is_gulf:
                    # Destination/origin IS in Gulf — proven LHR→DXB corridor
                    if not origin_is_east:
                        waypoints = [
                            (47.5, 13.0),(41.0, 20.0),(37.9, 27.5),
                            (26.5, 33.0),(22.5, 39.0),(20.0, 42.0),
                            (20.0, 51.0),(24.0, 55.5),
                        ]
                        name = "Southern corridor: Austria → Albania → Turkey → Red Sea → Arabian Sea → Gulf"
                    else:
                        waypoints = [
                            (24.0, 55.5),(20.0, 51.0),(20.0, 42.0),
                            (22.5, 39.0),(26.5, 33.0),(37.9, 27.5),
                            (41.0, 20.0),(47.5, 13.0),
                        ]
                        name = "Southern corridor: Gulf → Arabian Sea → Red Sea → Turkey → Europe"
                    factor = 1.27
                else:
                    waypoints = [
                        (47.5, 13.0),(41.0, 20.0),(37.9, 27.5),
                        (26.5, 33.0),(22.5, 39.0),(20.0, 42.0),
                        (20.0, 51.0),(24.0, 55.5),
                    ]
                    name = "Southern corridor via Red Sea"
                    factor = 1.20
            elif mode_key == "Balanced":
                if not origin_is_east:
                    waypoints = [
                        (41.0, 20.0),(37.9, 27.5),(27.0, 34.0),
                        (23.0, 47.5),(24.0, 54.0),
                    ]
                else:
                    waypoints = [
                        (24.0, 54.0),(23.0, 47.5),(27.0, 34.0),
                        (37.9, 27.5),(41.0, 20.0),
                    ]
                name = "Balanced: Albania → Turkey → Egypt → S.Saudi Arabia"
                factor = 1.15
            else:  # Greener
                if not origin_is_east:
                    waypoints = [
                        (39.5, 25.0),(34.5, 28.0),(29.0, 33.0),
                        (21.5, 39.5),(20.5, 51.0),(24.5, 54.5),
                    ]
                else:
                    waypoints = [
                        (24.5, 54.5),(20.5, 51.0),(21.5, 39.5),
                        (29.0, 33.0),(34.5, 28.0),(39.5, 25.0),
                    ]
                name = "Greener: Greece → Rhodes → Sinai → Red Sea → Gulf"
                factor = 1.22

    elif hits_ua or hits_af:
        if mode_key in ("Safer", "Balanced"):
            waypoints = [
                (43.5, 18.0),   # Bosnia — lat 43.5 < Ukraine (44.4N)
                (41.0, 28.5),   # Istanbul
                (d_lat + 1.5, max(d_lon - 3.0, d_lon + 3.0)),
            ]
            name = "Southern corridor avoiding Ukrainian/Afghan airspace"
            factor = 1.12
        else:
            waypoints = [
                (43.5, 18.0),
                (41.5, 30.0),
            ]
            name = "Deviation south of conflict zone"
            factor = 1.06
    else:
        # No conflict zones hit — gentle offset to show non-direct routing
        mid_lat = (o_lat + d_lat) / 2
        mid_lon = (o_lon + d_lon) / 2
        offsets = {"Safer":(2.0,1.5),"Balanced":(1.0,0.8),"Greener":(0.5,0.3)}
        dlat, dlon = offsets.get(mode_key,(1.0,0.5))
        waypoints = [(mid_lat + dlat, mid_lon + dlon)]
        factors   = {"Safer":1.04,"Balanced":1.02,"Greener":1.01}
        factor    = factors.get(mode_key, 1.02)
        name      = f"{mode_key} adjusted routing"

    return waypoints, name, factor

def folium_to_html(m):
    buf=BytesIO(); m.save(buf,close_file=False); return buf.getvalue().decode("utf-8")
def risk_colour(rc): return{"Low":"#16a34a","Medium":"#f59e0b","High":"#ef4444"}.get(rc,"#16a34a")
def add_history(rec): st.session_state.history.append(rec)

# ================================================================
# BOOTSTRAP
# ================================================================
with st.spinner("Loading data…"):
    _ntsb_df,_ntsb_meta = load_ntsb_data()
    _flight_df,_flight_err = load_flight_data()

risk_model      = UnifiedBayesianModel(df=_ntsb_df)
emissions_model = risk_model   # same unified model
fuel_model      = FuelEfficiencyModel()

# Sorted aircraft list for dropdowns
AC_LIST       = sorted(AIRCRAFT_CATALOGUE.keys())
AC_LIST_SHORT = ["A319","A320","A320neo","A321neo","A330neo","A350-900","A380",
                 "B737-800","B737 MAX 8","B777-300ER","B787-8","B787-9"]  # quick-select subset

# ================================================================
# HEADER
# ================================================================
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
# ================================================================
def page_home():
    st.markdown("""
    <div class="hero-card">
        <h1>Bayesian Aviation Decision-Support Prototype</h1>
        <p>An interactive final-year project combining real NTSB accident data, Bayesian inference,
        fuel efficiency analysis, CO₂ emissions modelling, and OpenSky route intelligence —
        built to support safer and more sustainable aviation decision-making.</p>
    </div>""", unsafe_allow_html=True)

    if risk_model.trained_on_data:
        rd=risk_model.risk_dist
        c1,c2,c3,c4=st.columns(4)
        c1.metric("NTSB Records",f"{risk_model.n_training:,}")
        c2.metric("High-Risk Events",f"{rd.get('High',0):,}")
        c3.metric("Med-Risk Events",f"{rd.get('Medium',0):,}")
        c4.metric("Low-Risk Events",f"{rd.get('Low',0):,}")
    else:
        c1,c2,c3=st.columns(3)
        c1.metric("Core Modules","6"); c2.metric("Methods","Bayesian + Haversine"); c3.metric("Mode","Prototype")
    if _flight_df is not None:
        fc1,fc2,fc3=st.columns(3)
        fc1.metric("Flight Records",f"{len(_flight_df):,}")
        _valid=_flight_df[_flight_df["origin"]!=_flight_df["destination"]]
        top=_valid.groupby(["origin","destination"]).size().nlargest(1).reset_index()
        if len(top): fc2.metric("Busiest Sample Route",f"{top.iloc[0]['origin']}→{top.iloc[0]['destination']}")
        fc3.metric("Aircraft Types in Catalogue",str(len(AIRCRAFT_CATALOGUE)))

    st.markdown("## System Modules")
    r1c1,r1c2,r1c3=st.columns(3)
    r2c1,r2c2,r2c3=st.columns(3)
    mods=[
        (r1c1,"Risk Analysis",f"Naive Bayes trained on {'real NTSB data' if risk_model.trained_on_data else 'prototype values'}. Posterior probabilities across Low / Medium / High risk."),
        (r1c2,"Fuel Efficiency","L/100pkm, ASK/kg, and CO₂/pax across "+str(len(AIRCRAFT_CATALOGUE))+" Boeing & Airbus variants using EASA EDB v31 data."),
        (r1c3,"Emissions Analysis","CO₂ output per route classified Low / Moderate / High with car and tree equivalents."),
        (r2c1,"Aircraft Explorer","Interactive 360° engine model with type-specific emissions and range context."),
        (r2c2,"Scenario History","Review and export all analysed scenarios as CSV."),
        (r2c3,"Ethics & Implications","BCS Code, GDPR, EU AI Act, DO-178C, and data bias analysis."),
    ]
    for col,title,desc in mods:
        with col:
            st.markdown(f'<div class="glass-card" style="min-height:140px;"><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)

    st.markdown("## Data Sources")
    for name,desc,use,ok in [
        ("NTSB AviationData.csv","88,000+ accident records — injury, weather, phase of flight","Risk model training",risk_model.trained_on_data),
        ("OpenSky Flightlist CSVs","Real flight callsigns, ICAO routes (Jan–May 2019)","Route statistics",_flight_df is not None),
        ("EASA/ICAO EDB v31","Engine fuel consumption — 500+ engine variants","CO₂ factors + fuel efficiency",True),
        ("EASA CZIBs (2026-03-R5)","Live conflict zone advisories — Iran, Iraq, Syria, Ukraine etc.","Route Planner conflict avoidance",True),
    ]:
        col,ico=("#22c55e","✓") if ok else ("#ef4444","✗")
        st.markdown(f'<div class="glass-card" style="padding:.9rem 1.2rem;"><span style="color:{col};font-weight:700;">{ico} {name}</span><br><span style="color:#94a3b8;font-size:.87rem;">{desc}</span>&nbsp;·&nbsp;<em style="color:#60a5fa;font-size:.85rem;">Used for: {use}</em></div>',unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="border-left:3px solid #3b82f6;"><b>Academic Disclaimer</b><br><span>This prototype is for academic purposes only. It does not constitute certified aviation guidance and must not replace licensed aviation systems or personnel.</span></div>',unsafe_allow_html=True)


# ================================================================
# AVIATIONSTACK FLIGHT LOOKUP
# ================================================================
def lookup_flight(flight_number: str, api_key: str) -> dict | None:
    """
    Fetch real-time flight data from AviationStack API.
    Free tier: 500 calls/month — sufficient for academic use.
    Returns dict with airline, origin, destination, aircraft, status or None on error.
    """
    import urllib.request, json, urllib.parse
    flight_number = flight_number.strip().upper().replace(" ","")
    url = (f"http://api.aviationstack.com/v1/flights"
           f"?access_key={api_key}&flight_iata={urllib.parse.quote(flight_number)}&limit=1")
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        if not data.get("data"):
            return None
        d = data["data"][0]
        return {
            "flight_iata":   d.get("flight",{}).get("iata",""),
            "airline":       (d.get("airline") or {}).get("name","Unknown") or "Unknown",
            "origin_iata":   (d.get("departure") or {}).get("iata","") or "",
            "origin_name":   (d.get("departure") or {}).get("airport","Unknown") or "Unknown",
            "dest_iata":     (d.get("arrival") or {}).get("iata","") or "",
            "dest_name":     (d.get("arrival") or {}).get("airport","Unknown") or "Unknown",
            "aircraft_type": (d.get("aircraft") or {}).get("iata","") or "",
            "status":        d.get("flight_status","unknown"),
            "dep_scheduled": d.get("departure",{}).get("scheduled",""),
            "arr_scheduled": d.get("arrival",{}).get("scheduled",""),
            "dep_delay":     int(d.get("departure",{}).get("delay",0) or 0),
        }
    except Exception:
        return None


def _iata_to_aircraft_key(iata_code) -> str:
    """Map AviationStack IATA aircraft code to our catalogue key. Null-safe."""
    if not iata_code:          # None or empty string from API
        return "A320"
    iata_code = str(iata_code).strip().upper()
    if not iata_code:
        return "A320"
    mapping = {
        # Airbus narrowbody
        "319":"A319","320":"A320","321":"A321",
        "32A":"A320neo","32N":"A320neo","32Q":"A321neo","32S":"A321neo",
        "321XLR":"A321XLR",
        # Airbus widebody
        "332":"A330-200","333":"A330-300","338":"A330neo",
        "340":"A340-300","346":"A340-600",
        "351":"A350-900","359":"A350-1000","352":"A350-900",
        "388":"A380",
        # Boeing narrowbody
        "737":"B737-800","73C":"B737-700","73H":"B737-800","73J":"B737-900",
        "73W":"B737-800","73G":"B737-700",
        "7M8":"B737 MAX 8","7M9":"B737 MAX 10","7MB":"B737 MAX 8",
        "752":"B757-200","753":"B757-200",
        # Boeing widebody
        "762":"B767-300","763":"B767-300","76W":"B767-300ER","764":"B767-300ER",
        "772":"B777-200ER","773":"B777-300ER","77W":"B777-300ER","777":"B777-200ER",
        "77X":"B777X","778":"B777X",
        "788":"B787-8","789":"B787-9","781":"B787-10","787":"B787-9",
        # Qatar Airways commonly uses these
        "77L":"B777-200ER","77F":"B777-300ER",
        "A7-":"A350-900",  # Qatar reg prefix fallback
    }
    # Try exact match first
    result = mapping.get(iata_code)
    if result:
        return result
    # Try first 3 chars
    result = mapping.get(iata_code[:3])
    if result:
        return result
    # Fuzzy: if it contains "350" → A350, "787" → B787 etc.
    for substr, key in [("350","A350-900"),("380","A380"),("320","A320"),("321","A321"),
                         ("787","B787-9"),("777","B777-300ER"),("737","B737-800"),("330","A330-300")]:
        if substr in iata_code:
            return key
    return "A320"  # safe default


def _map_status_to_congestion(status: str, delay: int) -> str:
    if delay > 60 or status in ("cancelled","diverted"): return "high"
    if delay > 20: return "medium"
    return "low"


# Extended IATA airport coordinates — covers all AviationStack-returned airports
# so distance auto-calculation works even for airports not in our route planner list
_IATA_COORDS = {
    "AAR":(56.3000,10.6192),
    "ABE":(40.6521,-75.4408),
    "ABJ":(5.2614,-3.9262),
    "ABQ":(35.0402,-106.6090),
    "ABV":(9.0068, 7.2632),
    "ABZ":(57.2019,-2.1978),
    "ACC":(5.6052,-0.1668),
    "ACE":(28.9455,-13.6052),
    "ADA":(36.9822,35.2803),
    "ADB":(38.2924,27.1569),
    "ADD":(8.9779,38.7993),
    "ADE":(12.8294,45.0289),
    "ADL":(-34.9450,138.5306),
    "AEP":(-34.5592,-58.4158),
    "AES":(62.5625, 6.1197),
    "AEY":(65.6600,-18.0728),
    "AGA":(30.3250,-9.4131),
    "AGP":(36.6749,-4.4991),
    "AHB":(18.2404,42.6566),
    "AJA":(41.9236, 8.8028),
    "AKL":(-37.0082,174.7850),
    "ALA":(43.3521,77.0405),
    "ALB":(42.7483,-73.8017),
    "ALC":(38.2822,-0.5582),
    "ALG":(36.6910, 3.2153),
    "AMD":(23.0771,72.6347),
    "AMM":(31.7226,35.9932),
    "AMQ":(-3.7103,128.0881),
    "AMS":(52.3086, 4.7639),
    "ANC":(61.1741,-149.9961),
    "ANF":(-23.4444,-70.4451),
    "ANU":(17.1368,-61.7927),
    "APW":(-13.8300,-172.0083),
    "AQJ":(29.6117,35.0181),
    "AQP":(-16.3411,-71.5830),
    "ARN":(59.6519,17.9186),
    "ASB":(37.9864,58.3611),
    "ASM":(15.2919,38.9107),
    "ASP":(-23.8067,133.9022),
    "ASR":(38.7703,35.4953),
    "ASU":(-25.2400,-57.5197),
    "ATH":(37.9364,23.9445),
    "ATL":(33.6407,-84.4277),
    "ATQ":(31.7096,74.7997),
    "AUA":(12.5014,-70.0152),
    "AUH":(24.4330,54.6511),
    "AUS":(30.1975,-97.6664),
    "AXD":(40.8558,25.9564),
    "AYQ":(-25.1864,130.9767),
    "AYT":(36.8987,30.8003),
    "BAH":(26.2708,50.6336),
    "BAQ":(10.8896,-74.7808),
    "BBI":(20.2444,85.8178),
    "BBU":(44.5032,26.1022),
    "BCN":(41.2971, 2.0785),
    "BDA":(32.3640,-64.6787),
    "BDJ":(-3.4423,114.7628),
    "BDL":(41.9389,-72.6832),
    "BEG":(44.8184,20.3091),
    "BEL":(-1.3792,-48.4763),
    "BER":(52.3514,13.4939),
    "BES":(48.4479,-4.4183),
    "BEY":(33.8208,35.4883),
    "BFS":(54.6575,-6.2158),
    "BGA":(7.1268,-73.1848),
    "BGF":(4.3986,18.5188),
    "BGI":(13.0746,-59.4925),
    "BGO":(60.2934, 5.2181),
    "BGY":(45.6739, 9.7042),
    "BHK":(39.7750,64.4833),
    "BHX":(52.4539,-1.7480),
    "BIO":(43.3011,-2.9106),
    "BJL":(13.3380,-16.6522),
    "BJM":(-3.3240,29.3185),
    "BJV":(37.2506,27.6644),
    "BKI":(5.9372,116.0508),
    "BKK":(13.6811,100.7470),
    "BKO":(12.5336,-7.9499),
    "BLL":(55.7403, 9.1519),
    "BLQ":(44.5354,11.2887),
    "BLR":(13.1986,77.7066),
    "BME":(-17.9447,122.2322),
    "BNA":(36.1245,-86.6782),
    "BNE":(-27.3842,153.1175),
    "BNX":(44.9414,17.2975),
    "BOD":(44.8283,-0.7156),
    "BOG":(4.7016,-74.1469),
    "BOI":(43.5644,-116.2228),
    "BOJ":(42.5696,27.5152),
    "BOM":(19.0896,72.8656),
    "BOO":(67.2692,14.3653),
    "BOS":(42.3656,-71.0096),
    "BPN":(-1.2683,116.8944),
    "BRC":(-41.1511,-71.1579),
    "BRE":(53.0475, 8.7869),
    "BRI":(41.1389,16.7606),
    "BRQ":(49.1513,16.6944),
    "BRS":(51.3827,-2.7191),
    "BRU":(50.9014, 4.4844),
    "BSB":(-15.8711,-47.9186),
    "BSL":(47.5896, 7.5299),
    "BUD":(47.4298,19.2611),
    "BUF":(42.9405,-78.7322),
    "BUR":(34.2007,-118.3589),
    "BWI":(39.1754,-76.6683),
    "BWN":(4.9442,114.9280),
    "BZE":(17.5391,-88.3082),
    "BZG":(53.0968,17.9778),
    "BZV":(-4.2517,15.2531),
    "CAG":(39.2515, 9.0543),
    "CAI":(30.1219,31.4056),
    "CAN":(23.3925,113.2988),
    "CAY":(4.8198,-52.3606),
    "CBB":(-17.4211,-66.1771),
    "CBR":(-35.3069,149.1953),
    "CCP":(-36.7722,-73.0631),
    "CCS":(10.6031,-66.9906),
    "CCU":(22.6547,88.4467),
    "CDG":(49.0097, 2.5479),
    "CEB":(10.3075,123.9791),
    "CEI":(19.9523,99.8828),
    "CFU":(39.6019,19.9117),
    "CGB":(-15.6531,-56.1167),
    "CGH":(-23.6261,-46.6564),
    "CGK":(-6.1275,106.6537),
    "CGN":(50.8659, 7.1427),
    "CGO":(34.5197,113.8408),
    "CGP":(22.2496,91.8133),
    "CGQ":(43.9962,125.6850),
    "CGR":(-20.4687,-54.6725),
    "CHC":(-43.4894,172.5322),
    "CHQ":(35.5317,24.1497),
    "CIA":(41.7994,12.5949),
    "CIT":(42.3642,69.4789),
    "CJB":(11.0300,77.0434),
    "CJC":(-22.4981,-68.9036),
    "CJJ":(36.7166,127.4994),
    "CJU":(33.5113,126.4930),
    "CKG":(29.7192,106.6417),
    "CKY":(9.5769,-13.6119),
    "CLE":(41.4117,-81.8498),
    "CLJ":(46.7852,23.6861),
    "CLO":(3.5432,-76.3816),
    "CLT":(35.2140,-80.9431),
    "CMB":(7.1800,79.8841),
    "CMH":(39.9980,-82.8919),
    "CMN":(33.3675,-7.5898),
    "CNF":(-19.6244,-43.9719),
    "CNS":(-16.8858,145.7553),
    "CNX":(18.7668,98.9628),
    "COK":(10.1520,76.3999),
    "COO":(6.3572, 2.3845),
    "COR":(-31.3236,-64.2080),
    "CPH":(55.6180,12.6560),
    "CPT":(-33.9648,18.6017),
    "CRK":(15.1858,120.5596),
    "CRL":(50.4592, 4.4528),
    "CSX":(28.1892,113.2197),
    "CTA":(37.4668,15.0664),
    "CTG":(10.4424,-75.5130),
    "CTS":(42.7752,141.6922),
    "CTU":(30.5785,103.9473),
    "CUN":(21.0365,-86.8771),
    "CUR":(12.1889,-68.9598),
    "CUZ":(-13.5357,-71.9388),
    "CVG":(39.0488,-84.6678),
    "CWB":(-25.5285,-49.1758),
    "CWL":(51.3967,-3.3433),
    "CXR":(12.0075,109.2194),
    "DAC":(23.8433,90.3978),
    "DAD":(16.0439,108.1994),
    "DAL":(32.8471,-96.8517),
    "DAR":(-6.8781,39.2026),
    "DBV":(42.5614,18.2681),
    "DCA":(38.8512,-77.0402),
    "DEL":(28.5562,77.1000),
    "DEN":(39.8561,-104.6737),
    "DFW":(32.8998,-97.0403),
    "DIL":(-8.5497,125.5247),
    "DJE":(33.8753,10.7755),
    "DJJ":(-2.5769,140.5164),
    "DKR":(14.7397,-17.4902),
    "DLA":(4.0061, 9.7197),
    "DLC":(38.9657,121.5386),
    "DLM":(36.7131,28.7925),
    "DME":(55.4088,37.9063),
    "DMK":(13.9126,100.6069),
    "DMM":(26.4712,49.7979),
    "DOH":(25.2609,51.6138),
    "DOM":(15.5469,-61.3000),
    "DPS":(-8.7483,115.1670),
    "DRS":(51.1328,13.7672),
    "DRW":(-12.4092,130.8766),
    "DTW":(42.2162,-83.3554),
    "DUB":(53.4213,-6.2700),
    "DUD":(-45.9281,170.1983),
    "DUR":(-29.6144,31.1197),
    "DUS":(51.2895, 6.7668),
    "DVO":(7.1255,125.6458),
    "DWC":(24.8963,55.1614),
    "DXB":(25.2532,55.3657),
    "DYU":(38.5433,68.7750),
    "EBB":(0.0424,32.4435),
    "EDI":(55.9500,-3.3725),
    "EFL":(38.1200,20.5006),
    "EGS":(65.2833,-14.4014),
    "EIN":(51.4501, 5.3742),
    "ELP":(31.8072,-106.3779),
    "ELQ":(26.3025,43.7744),
    "EMA":(52.8311,-1.3281),
    "EOH":(6.2200,-75.5906),
    "ESB":(40.1281,32.9951),
    "EVN":(40.1473,44.3959),
    "EWR":(40.6895,-74.1745),
    "EZE":(-34.8222,-58.5358),
    "FAI":(64.8151,-147.8561),
    "FAO":(37.0144,-7.9659),
    "FBM":(-11.5913,27.5308),
    "FCO":(41.7999,12.2462),
    "FDF":(14.5910,-60.9956),
    "FEG":(40.3588,71.7450),
    "FEZ":(33.9272,-4.9778),
    "FIH":(-4.3857,15.4446),
    "FJR":(25.1122,56.3240),
    "FKI":(0.4817,25.3380),
    "FLL":(26.0726,-80.1527),
    "FLN":(-27.6703,-48.5522),
    "FLR":(43.8100,11.2051),
    "FNA":(8.6164,-13.1955),
    "FNC":(32.6979,-16.7745),
    "FOC":(25.9351,119.6633),
    "FOR":(-3.7763,-38.5326),
    "FPO":(26.5588,-78.6956),
    "FRA":(50.0379, 8.5622),
    "FRU":(43.0612,74.4776),
    "FUE":(28.4527,-13.8638),
    "FUK":(33.5858,130.4511),
    "FUN":(-8.5250,179.1961),
    "GAN":(0.6933,73.1556),
    "GAU":(26.1061,91.5856),
    "GBE":(-24.5553,25.9182),
    "GCM":(19.2928,-81.3577),
    "GDL":(20.5218,-103.3111),
    "GDN":(54.3776,18.4662),
    "GEG":(47.6199,-117.5339),
    "GEO":(6.4986,-58.2542),
    "GIG":(-22.8099,-43.2505),
    "GLA":(55.8719,-4.4330),
    "GMP":(37.5583,126.7906),
    "GND":(12.0042,-61.7862),
    "GOI":(15.3808,73.8314),
    "GOM":(-1.6708,29.2383),
    "GOT":(57.6628,12.2798),
    "GPA":(38.1511,21.4256),
    "GRU":(-23.4356,-46.4731),
    "GRZ":(46.9911,15.4396),
    "GUA":(14.5833,-90.5275),
    "GUM":(13.4834,144.7969),
    "GUW":(47.1219,51.8214),
    "GVA":(46.2381, 6.1089),
    "GYD":(40.4675,50.0467),
    "GYE":(-2.1574,-79.8836),
    "GYN":(-16.6320,-49.2208),
    "GZT":(36.9472,37.4786),
    "HAH":(-11.5337,43.2719),
    "HAJ":(52.4611, 9.6850),
    "HAK":(19.9349,110.4589),
    "HAM":(53.6304, 9.9882),
    "HAN":(21.2212,105.8072),
    "HAS":(27.4379,41.6861),
    "HAU":(59.3453, 5.2086),
    "HAV":(22.9892,-82.4091),
    "HBA":(-42.8361,147.5078),
    "HBE":(30.9172,29.6964),
    "HDY":(6.9332,100.3931),
    "HEL":(60.3172,24.9633),
    "HER":(35.3397,25.1803),
    "HET":(40.8514,111.8242),
    "HFE":(31.7800,117.2983),
    "HGH":(30.2295,120.4344),
    "HIJ":(34.4361,132.9194),
    "HIR":(-9.4280,160.0547),
    "HKG":(22.3080,113.9185),
    "HKT":(8.1132,98.3169),
    "HLZ":(-37.8667,175.3322),
    "HND":(35.5494,139.7798),
    "HNL":(21.3245,-157.9251),
    "HOU":(29.6454,-95.2789),
    "HRB":(45.6234,126.2500),
    "HRE":(-17.9318,31.0928),
    "HRG":(27.1783,33.7994),
    "HUI":(16.4015,107.7030),
    "HYD":(17.2403,78.4294),
    "IAD":(38.9531,-77.4565),
    "IAH":(29.9902,-95.3368),
    "IAS":(47.1786,27.6206),
    "IBZ":(38.8729, 1.3731),
    "ICN":(37.4602,126.4407),
    "IGR":(-25.7374,-54.4734),
    "IKT":(52.2681,104.3889),
    "ILO":(10.7130,122.5454),
    "IMF":(24.7600,93.8967),
    "IND":(39.7173,-86.2944),
    "INN":(47.2602,11.3439),
    "INV":(57.5425,-4.0475),
    "IQQ":(-20.5353,-70.1808),
    "IQT":(-3.7847,-73.3089),
    "IRM":(32.5561,35.9917),
    "ISB":(33.6167,73.0997),
    "ISG":(24.3964,124.1864),
    "IST":(41.2753,28.7519),
    "ITM":(34.7847,135.4386),
    "ITO":(19.7214,-155.0481),
    "IUE":(-19.0794,-169.9256),
    "IXC":(30.6735,76.7885),
    "IXE":(12.9613,74.8906),
    "IXL":(34.1359,77.5465),
    "JAI":(26.8242,75.8122),
    "JAX":(30.4941,-81.6879),
    "JED":(21.6796,39.1565),
    "JFK":(40.6413,-73.7781),
    "JGA":(22.4655,70.0126),
    "JHB":(1.6413,103.6698),
    "JIB":(11.5473,43.1594),
    "JMK":(37.4351,25.3481),
    "JNB":(-26.1367,28.2424),
    "JNU":(58.3549,-134.5763),
    "JOG":(-7.7882,110.4317),
    "JPA":(-7.1457,-34.9503),
    "JRO":(-3.4294,37.0745),
    "JSI":(39.1772,23.5033),
    "JTR":(36.3992,25.4793),
    "JUB":(4.8722,31.6011),
    "KBR":(6.1653,102.2933),
    "KBV":(8.0992,98.9861),
    "KCH":(1.4847,110.3428),
    "KCZ":(33.5461,133.6697),
    "KEF":(63.9850,-22.6056),
    "KGI":(-30.7894,121.4617),
    "KGL":(-1.9686,30.1395),
    "KGS":(36.7933,27.0917),
    "KHG":(39.5429,76.0200),
    "KHH":(22.5771,120.3497),
    "KHI":(24.9065,67.1608),
    "KHN":(28.8650,115.9003),
    "KIN":(17.9357,-76.7875),
    "KIV":(46.9278,28.9308),
    "KIX":(34.4347,135.2441),
    "KKC":(16.4666,102.7836),
    "KLO":(11.6795,122.3758),
    "KMG":(24.9922,102.7433),
    "KMI":(31.8772,131.4489),
    "KMJ":(32.8373,130.8553),
    "KNO":(3.6422,98.8853),
    "KOA":(19.7388,-156.0456),
    "KOE":(-10.1716,123.6711),
    "KOJ":(31.8034,130.7194),
    "KOS":(10.5797,103.6368),
    "KRK":(49.9683,19.7847),
    "KRN":(67.8220,20.3367),
    "KRS":(58.2042, 8.0854),
    "KRW":(40.0633,52.9267),
    "KTM":(27.6966,85.3591),
    "KTW":(50.4744,19.0800),
    "KUL":(2.7456,101.7072),
    "KUN":(54.9639,24.0847),
    "KWE":(26.5386,106.8014),
    "KWI":(29.2266,47.9689),
    "KWJ":(35.1264,126.8089),
    "KWL":(25.2181,110.0392),
    "KZN":(55.6063,49.2783),
    "LAD":(-8.8583,13.2311),
    "LAS":(36.0840,-115.1537),
    "LAX":(33.9425,-118.4081),
    "LBA":(53.8659,-1.6606),
    "LBS":(-16.4667,179.3397),
    "LBV":(0.4586, 9.4122),
    "LCY":(51.5048, 0.0495),
    "LED":(59.8003,30.2625),
    "LEJ":(51.4239,12.2364),
    "LFW":(6.1656, 1.2545),
    "LGA":(40.7772,-73.8726),
    "LGB":(33.8177,-118.1516),
    "LGG":(50.6374, 5.4432),
    "LGK":(6.3297,99.7286),
    "LGW":(51.1481,-0.1903),
    "LHE":(31.5216,74.4036),
    "LHR":(51.4700,-0.4543),
    "LHW":(36.5153,103.6203),
    "LIH":(21.9760,-159.3390),
    "LIM":(-12.0219,-77.1143),
    "LIN":(45.4456, 9.2767),
    "LIS":(38.7813,-9.1359),
    "LJU":(46.2237,14.4576),
    "LKO":(26.7606,80.8893),
    "LLA":(65.5436,22.1219),
    "LLW":(-13.7894,33.7814),
    "LNZ":(48.2332,14.1875),
    "LOP":(-8.7573,116.2767),
    "LOS":(6.5774, 3.3212),
    "LPA":(27.9319,-15.3866),
    "LPB":(-16.5133,-68.1922),
    "LPL":(53.3336,-2.8497),
    "LPQ":(19.8973,102.1614),
    "LPX":(56.5175,21.0969),
    "LST":(-41.5453,147.2142),
    "LTK":(-17.6167,177.4167),
    "LTN":(51.8747,-0.3683),
    "LUN":(-15.3308,28.4526),
    "LUX":(49.6233, 6.2044),
    "LXA":(29.2978,90.9119),
    "LXR":(25.6710,32.7066),
    "LYP":(31.3650,72.9944),
    "LYR":(78.2461,15.4656),
    "LYS":(45.7256, 5.0811),
    "MAA":(12.9900,80.1693),
    "MAD":(40.4719,-3.5626),
    "MAH":(39.8626, 4.2186),
    "MAJ":(7.0647,171.2722),
    "MAN":(53.3537,-2.2750),
    "MAO":(-3.0386,-60.0497),
    "MAR":(10.5582,-71.7279),
    "MBA":(-4.0348,39.5942),
    "MBJ":(18.5037,-77.9134),
    "MCI":(39.2976,-94.7139),
    "MCO":(28.4312,-81.3081),
    "MCT":(23.5933,58.2844),
    "MCY":(-26.6033,153.0836),
    "MCZ":(-9.5108,-35.7917),
    "MDC":(1.5493,124.9260),
    "MDE":(6.1647,-75.4231),
    "MDL":(21.7021,95.9778),
    "MDW":(41.7868,-87.7522),
    "MDZ":(-32.8317,-68.7928),
    "MED":(24.5534,39.7051),
    "MEL":(-37.6690,144.8410),
    "MEM":(35.0424,-89.9767),
    "MEX":(19.4363,-99.0721),
    "MFM":(22.1496,113.5920),
    "MGA":(12.1415,-86.1682),
    "MGQ":(2.0144,45.3047),
    "MIA":(25.7959,-80.2870),
    "MID":(20.9370,-89.6577),
    "MKY":(-21.1717,149.1797),
    "MLE":(4.1919,73.5292),
    "MLW":(6.2893,-10.7587),
    "MMX":(55.5363,13.3761),
    "MNL":(14.5086,121.0194),
    "MPL":(43.5762, 3.9630),
    "MPM":(-25.9208,32.5728),
    "MRS":(43.4393, 5.2214),
    "MRU":(-20.4302,57.6836),
    "MSP":(44.8848,-93.2223),
    "MSQ":(53.8825,28.0322),
    "MSU":(-29.4622,27.5525),
    "MSY":(29.9934,-90.2580),
    "MTY":(25.7785,-100.1069),
    "MUC":(48.3537,11.7750),
    "MUX":(30.2032,71.4192),
    "MVD":(-34.8383,-56.0308),
    "MXP":(45.6306, 8.7281),
    "MYJ":(33.8272,132.7000),
    "MYP":(37.6194,61.8967),
    "MZT":(23.1614,-106.2661),
    "NAG":(21.0922,79.0472),
    "NAN":(-17.7554,177.4431),
    "NAP":(40.8860,14.2908),
    "NAS":(25.0390,-77.4662),
    "NAT":(-5.7682,-35.3761),
    "NBO":(-1.3192,36.9275),
    "NCE":(43.6584, 7.2159),
    "NCL":(55.0375,-1.6917),
    "NDJ":(12.1337,15.0340),
    "NGO":(34.8583,136.8050),
    "NGS":(32.9169,129.9136),
    "NIM":(13.4815, 2.1836),
    "NKG":(31.7420,118.8622),
    "NMA":(40.9845,71.5567),
    "NNG":(22.6088,108.1722),
    "NOC":(53.9103,-8.8186),
    "NOS":(-13.3119,48.3148),
    "NOU":(-22.0146,166.2128),
    "NQZ":(51.0222,71.4669),
    "NRT":(35.7653,140.3856),
    "NSN":(-41.2983,173.2211),
    "NTE":(47.1532,-1.6108),
    "NUE":(49.4987,11.0669),
    "NYO":(58.7886,16.9122),
    "NYT":(19.6233,96.2008),
    "NYU":(21.1788,94.9302),
    "OAK":(37.7213,-122.2208),
    "OGG":(20.8986,-156.4305),
    "OHD":(41.1800,20.7423),
    "OHS":(24.3860,56.6244),
    "OKA":(26.1958,127.6461),
    "OKC":(35.3931,-97.6007),
    "OOL":(-28.1644,153.5047),
    "OPO":(41.2481,-8.6814),
    "ORD":(41.9742,-87.9073),
    "ORK":(51.8413,-8.4911),
    "ORN":(35.6239,-0.6212),
    "ORY":(48.7233, 2.3794),
    "OSI":(45.4627,18.8102),
    "OSL":(60.1976,11.1004),
    "OTP":(44.5711,26.0858),
    "OUA":(12.3533,-1.5125),
    "OUL":(64.9301,25.3546),
    "OVB":(54.9633,82.6503),
    "OXB":(11.8948,-15.6536),
    "PAP":(18.5800,-72.2925),
    "PAT":(25.5914,85.0880),
    "PBD":(21.6487,69.6572),
    "PBH":(27.4033,89.4664),
    "PBM":(5.4528,-55.1878),
    "PDG":(-0.8749,100.3517),
    "PDL":(37.7412,-25.6981),
    "PDV":(42.0678,24.8503),
    "PDX":(45.5887,-122.5975),
    "PEK":(40.0799,116.6031),
    "PEN":(5.2972,100.2769),
    "PER":(-31.9403,115.9669),
    "PEW":(33.9939,71.5146),
    "PHL":(39.8721,-75.2411),
    "PHX":(33.4373,-112.0078),
    "PIT":(40.4915,-80.2329),
    "PKR":(28.1989,83.9816),
    "PKX":(39.5097,116.4105),
    "PKZ":(15.1322,105.7814),
    "PLQ":(55.9733,21.0939),
    "PLS":(21.7736,-72.2655),
    "PLZ":(-33.9849,25.6173),
    "PMC":(-41.4389,-73.0940),
    "PMI":(39.5517, 2.7388),
    "PMO":(38.1759,13.0910),
    "PMR":(-40.3206,175.6169),
    "PNH":(11.5466,104.8441),
    "PNI":(6.9852,158.2089),
    "PNQ":(18.5822,73.9197),
    "PNR":(-4.8161,11.8865),
    "POA":(-29.9944,-51.1713),
    "POM":(-9.4431,147.2200),
    "POS":(10.5954,-61.3372),
    "POZ":(52.4210,16.8263),
    "PPG":(-14.3313,-170.7103),
    "PPS":(9.7421,118.7590),
    "PPT":(-17.5534,-149.6067),
    "PQC":(10.2270,103.9670),
    "PRG":(50.1008,14.2600),
    "PRN":(42.5728,21.0358),
    "PRY":(-25.6536,28.2242),
    "PSA":(43.6839,10.3927),
    "PSO":(1.3964,-77.2915),
    "PSP":(33.8297,-116.5062),
    "PTP":(16.2653,-61.5272),
    "PTY":(9.0714,-79.3834),
    "PUJ":(18.5674,-68.3634),
    "PUQ":(-53.0025,-70.8545),
    "PUS":(35.1795,128.9381),
    "PUY":(44.8935,13.9222),
    "PVD":(41.7276,-71.4282),
    "PVG":(31.1443,121.8083),
    "PVR":(20.6801,-105.2544),
    "PZU":(19.4336,37.2342),
    "RAI":(14.9245,-23.4935),
    "RAK":(31.6069,-8.0363),
    "RAR":(-21.2028,-159.8058),
    "RBA":(34.0514,-6.7515),
    "RDU":(35.8776,-78.7875),
    "REC":(-8.1265,-34.9228),
    "REP":(13.4108,103.8128),
    "RGN":(16.9023,96.1332),
    "RHO":(36.4053,28.0862),
    "RIC":(37.5052,-77.3197),
    "RIX":(56.9236,23.9711),
    "RJK":(45.2169,14.5703),
    "RKT":(25.6135,55.9389),
    "RKV":(64.1300,-21.9406),
    "RML":(6.8219,79.8866),
    "RNO":(39.4991,-119.7681),
    "RNS":(48.0694,-1.7348),
    "ROK":(-23.3819,150.4753),
    "ROR":(7.3673,134.5444),
    "ROT":(-38.1092,176.3172),
    "RTM":(51.9569, 4.4372),
    "RUH":(24.9578,46.6988),
    "RUN":(-20.8872,55.5103),
    "RVN":(66.5648,25.8304),
    "RZE":(50.1100,22.0189),
    "SAH":(15.4763,44.2197),
    "SAL":(13.4409,-89.0556),
    "SAN":(32.7336,-117.1897),
    "SAP":(15.4526,-87.9236),
    "SAT":(29.5337,-98.4698),
    "SAW":(40.8986,29.3092),
    "SBZ":(45.7856,24.0911),
    "SCL":(-33.3930,-70.7858),
    "SCO":(43.8601,51.0922),
    "SCQ":(42.8963,-8.4151),
    "SDF":(38.1744,-85.7360),
    "SDQ":(18.4297,-69.6689),
    "SDU":(-22.9105,-43.1631),
    "SEA":(47.4502,-122.3088),
    "SEZ":(-4.6742,55.5219),
    "SFO":(37.6213,-122.3790),
    "SGN":(10.8188,106.6520),
    "SHA":(31.1979,121.3364),
    "SHE":(41.6398,123.4836),
    "SHJ":(25.3285,55.5172),
    "SHO":(-26.3586,31.7167),
    "SID":(16.7414,-22.9494),
    "SIN":(1.3644,103.9915),
    "SJC":(37.3626,-121.9290),
    "SJD":(23.1518,-109.7211),
    "SJJ":(43.8246,18.3314),
    "SJO":(9.9939,-84.2089),
    "SJU":(18.4394,-66.0018),
    "SKB":(17.3112,-62.7188),
    "SKD":(39.7005,66.9838),
    "SKG":(40.5197,22.9709),
    "SKP":(41.9616,21.6214),
    "SLA":(-24.8560,-65.4861),
    "SLC":(40.7884,-111.9778),
    "SLL":(17.0372,54.0913),
    "SMF":(38.6954,-121.5908),
    "SNA":(33.6757,-117.8682),
    "SNN":(52.7020,-8.9248),
    "SOF":(42.6967,23.4114),
    "SOU":(50.9503,-1.3568),
    "SPU":(43.5389,16.2978),
    "SSA":(-12.9086,-38.3225),
    "SSG":(3.7553, 8.7072),
    "SSH":(27.9773,34.3950),
    "STL":(38.7487,-90.3700),
    "STN":(51.8850, 0.2350),
    "STR":(48.6899, 9.2219),
    "SUB":(-7.3798,112.7869),
    "SUV":(-18.0428,178.5592),
    "SVD":(13.1443,-61.2103),
    "SVG":(58.8769, 5.6378),
    "SVO":(55.9726,37.4146),
    "SVQ":(37.4180,-5.8931),
    "SVX":(56.7431,60.8028),
    "SXB":(48.5383, 7.6283),
    "SXM":(18.0410,-63.1089),
    "SXR":(33.9871,74.7742),
    "SYD":(-33.9399,151.1753),
    "SYR":(43.1112,-76.1063),
    "SYX":(18.3029,109.4122),
    "SZB":(3.1306,101.5494),
    "SZG":(47.7933,13.0043),
    "SZX":(22.6395,113.8145),
    "SZZ":(53.5847,14.9022),
    "TAE":(35.8941,128.6589),
    "TAK":(34.2144,134.0161),
    "TAO":(36.2661,120.3744),
    "TAS":(41.2579,69.2811),
    "TAY":(58.3075,26.6903),
    "TBS":(41.6692,44.9547),
    "TBU":(-21.2411,-175.1492),
    "TFN":(28.4827,-16.3414),
    "TFS":(28.0445,-16.5725),
    "TFU":(30.3125,104.4442),
    "TGD":(42.3594,19.2519),
    "TGU":(14.0608,-87.2172),
    "TIA":(41.4147,19.7206),
    "TIF":(21.4833,40.5444),
    "TIP":(32.6635,13.1590),
    "TIV":(42.4047,18.7233),
    "TKU":(60.5141,22.2628),
    "TLE":(-23.3833,43.7286),
    "TLL":(59.4133,24.8328),
    "TLS":(43.6293, 1.3638),
    "TLV":(32.0114,34.8867),
    "TMP":(61.4142,23.6044),
    "TMS":(0.3783, 6.7122),
    "TNG":(35.7269,-5.9169),
    "TNR":(-18.7969,47.4788),
    "TOD":(2.8181,104.1600),
    "TOS":(69.6833,18.9189),
    "TPA":(27.9755,-82.5332),
    "TPE":(25.0777,121.2327),
    "TRD":(63.4578,10.9239),
    "TRN":(45.2006, 7.6497),
    "TRR":(8.5385,81.1819),
    "TRU":(-8.0814,-79.1088),
    "TRV":(8.4822,76.9192),
    "TRW":(1.3814,172.9111),
    "TSA":(25.0694,121.5525),
    "TSR":(45.8099,21.3379),
    "TSV":(-19.2525,146.7650),
    "TUC":(-26.8409,-65.1048),
    "TUN":(36.8510,10.2272),
    "TUS":(32.1161,-110.9410),
    "TUU":(28.3654,36.6189),
    "TYN":(37.7469,112.6281),
    "TZX":(40.9950,39.7897),
    "UET":(30.2514,66.9378),
    "UIO":(-0.1292,-78.3575),
    "ULN":(47.8431,106.7664),
    "UME":(63.7919,20.2828),
    "UPG":(-5.0617,119.5544),
    "URC":(43.9072,87.4742),
    "USM":(9.5478,100.0628),
    "UTH":(17.3864,102.7883),
    "UVF":(13.7332,-60.9526),
    "VAR":(43.2321,27.8251),
    "VCA":(10.0851,105.7119),
    "VCE":(45.5053,12.3519),
    "VIE":(48.1103,16.5697),
    "VKO":(55.5915,37.2615),
    "VLC":(39.4893,-0.4816),
    "VLI":(-17.6994,168.3200),
    "VNO":(54.6341,25.2858),
    "VNS":(25.4524,82.8592),
    "VNT":(57.3578,21.5442),
    "VRN":(45.3957,10.8885),
    "VTE":(17.9883,102.5633),
    "VVI":(-17.6448,-63.1354),
    "VVO":(43.3989,132.1481),
    "WAW":(52.1657,20.9671),
    "WDH":(-22.4799,17.4709),
    "WLG":(-41.3272,174.8050),
    "WLS":(-13.2283,-176.1992),
    "WMI":(52.4511,20.6517),
    "WRO":(51.1027,16.8858),
    "WUH":(30.7783,114.2081),
    "XIY":(34.4471,108.7517),
    "XMN":(24.5440,118.1278),
    "YAO":(3.8372,11.5233),
    "YEG":(53.3097,-113.5797),
    "YFC":(45.8619,-66.5372),
    "YHZ":(44.8808,-63.5086),
    "YKA":(50.7022,-120.4444),
    "YLW":(49.9561,-119.3778),
    "YNB":(24.1442,38.0634),
    "YOW":(45.3225,-75.6692),
    "YQB":(46.7911,-71.3933),
    "YQM":(46.1122,-64.6786),
    "YQR":(50.4319,-104.6658),
    "YQT":(48.3719,-89.3239),
    "YUL":(45.4706,-73.7408),
    "YVA":(-11.7108,43.2439),
    "YVR":(49.1967,-123.1815),
    "YWG":(49.9100,-97.2398),
    "YXE":(52.1708,-106.6997),
    "YXS":(53.8894,-122.6797),
    "YXX":(49.0253,-122.3608),
    "YXY":(60.7096,-135.0672),
    "YYC":(51.1215,-114.0132),
    "YYG":(46.2900,-63.1211),
    "YYJ":(48.6469,-123.4258),
    "YYT":(47.6189,-52.7419),
    "YYZ":(43.6777,-79.6248),
    "YZF":(62.4628,-114.4403),
    "ZAD":(44.1083,15.3467),
    "ZAG":(45.7429,16.0688),
    "ZAM":(6.9224,122.0600),
    "ZNZ":(-6.2220,39.2249),
    "ZQN":(-45.0211,168.7392),
    "ZRH":(47.4647, 8.5492),
    "ZTH":(37.7509,20.8843),
    "ZYL":(24.9632,91.8679),
}

def _lookup_coords(code: str):
    """
    Return (lat, lon) for an airport by IATA or ICAO code.
    Searches IATA table first, then our AIRPORTS dict by ICAO field,
    then tries matching the IATA code embedded in airport names like 'London Heathrow (LHR)'.
    """
    if not code: return None
    code = code.strip().upper()
    # 1. Direct IATA lookup (most common — AviationStack returns IATA)
    if code in _IATA_COORDS:
        return _IATA_COORDS[code]
    # 2. ICAO lookup in AIRPORTS dict
    for ap_info in AIRPORTS.values():
        if ap_info.get("icao","") == code:
            return ap_info["coords"]
    # 3. IATA embedded in airport name e.g. "London Heathrow (LHR)"
    for ap_name, ap_info in AIRPORTS.items():
        if f"({code})" in ap_name:
            return ap_info["coords"]
    return None


def _distance_from_airport_codes(origin_code: str, dest_code: str):
    """
    Calculate Haversine distance between two airports.
    Accepts IATA (LHR, DOH) or ICAO (EGLL, OTHH) codes.
    Returns distance in km, or None if either airport not found.
    """
    o = _lookup_coords(origin_code)
    d = _lookup_coords(dest_code)
    if o and d:
        return haversine(o[0], o[1], d[0], d[1])
    return None


# Keep old name as alias for backward compatibility
def _icao_to_coords(icao: str):
    return _lookup_coords(icao)

def _distance_from_icao(origin_icao: str, dest_icao: str):
    return _distance_from_airport_codes(origin_icao, dest_icao)


def _route_complexity_from_distance(km: int) -> str:
    """Infer route complexity from distance (short-haul = more complex phases)."""
    if km < 1500:   return "high"    # short-haul: more takeoff/landing phases per km
    if km < 4000:   return "medium"
    return "low"                      # long-haul: mostly cruise


# ================================================================
# RISK ANALYSIS  (unified model — flight number OR manual input)
# ================================================================
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
def page_route():
    st.title("Route Planner")

    # Live conflict zone status banner
    closed = [z for z in CONFLICT_ZONES if z["status"] == "CLOSED"]
    st.markdown(f"""
    <div class="glass-card" style="border-left:4px solid #ef4444;">
        <b>📡 Live Airspace Intelligence — EASA CZIB 2026-03-R5 (28 Feb 2026)</b><br>
        <span style="color:#ef4444;font-weight:700;">CLOSED:</span>
        {", ".join(z["name"].split(" (")[0] for z in closed)}<br>
        <span style="color:#f97316;font-weight:700;">RESTRICTED:</span>
        UAE, Qatar, Bahrain, Lebanon, Afghanistan<br>
        <span style="color:#f59e0b;font-weight:700;">ELEVATED RISK:</span>
        Saudi Arabia northern zone, Jordan<br>
        <span style="color:#94a3b8;font-size:.85rem;">
        Source: EASA Conflict Zone Information Bulletins (CZIBs) — the authoritative advisories used by all European-certificated airlines.
        Conflict zones are drawn on the map and automatically avoided by the Safer/Balanced routing modes.
        </span>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    sorted_countries = sorted(COUNTRIES.keys())
    with c1:
        oc=st.selectbox("Origin Country",sorted_countries,
                        help=f"Choose from {len(sorted_countries)} countries · {len(AIRPORTS)} airports")
        oa=st.selectbox("Origin Airport",sorted(COUNTRIES[oc]))
    with c2:
        _uae_idx = sorted_countries.index("UAE") if "UAE" in sorted_countries else 0
        dc=st.selectbox("Destination Country",sorted_countries,index=_uae_idx,
                        help=f"Choose from {len(sorted_countries)} countries · {len(AIRPORTS)} airports")
        da=st.selectbox("Destination Airport",sorted(COUNTRIES[dc]))

    ac=st.selectbox("Aircraft Type",AC_LIST)
    mode=st.selectbox("Route Preference",[
        "Shortest — Direct great-circle (may cross conflict zones)",
        "Safer — Avoids all EASA conflict zones (recommended for Middle East/Ukraine)",
        "Greener — Minimises CO₂, light conflict avoidance",
        "Balanced — Compromise between distance, safety, and emissions",
    ])
    mode_key=mode.split(" —")[0]

    if st.button("Plan Route"):
        if oa==da: st.warning("Origin and destination cannot be the same."); return

        o_lat,o_lon=AIRPORTS[oa]["coords"]
        d_lat,d_lon=AIRPORTS[da]["coords"]
        o_icao=AIRPORTS[oa]["icao"]
        d_icao=AIRPORTS[da]["icao"]

        # Direct great-circle
        direct_pts=great_circle_points(o_lat,o_lon,d_lat,d_lon,n=80)
        direct_km=haversine(o_lat,o_lon,d_lat,d_lon)

        # Check if direct route hits conflict zones
        direct_hits=route_passes_through_zones(direct_pts)
        critical_hits=[z for z in direct_hits if z["level"]=="critical"]

        # Build adjusted route using real conflict-zone-aware waypoints
        if mode_key == "Shortest":
            adj_pts       = direct_pts
            adj_hits      = direct_hits
            safe_route_name = "Direct great-circle"
            adj_km        = direct_km
        else:
            safe_waypoints, safe_route_name, adj_factor = _build_safe_waypoints(
                o_lat, o_lon, d_lat, d_lon, direct_hits, mode_key
            )
            adj_pts  = avoidance_route(o_lat, o_lon, d_lat, d_lon, safe_waypoints)
            adj_hits = route_passes_through_zones(adj_pts)
            adj_km   = round(direct_km * adj_factor)

        extra_km = adj_km - direct_km

        base_co2,factor=emissions_model.estimate(ac,direct_km)
        adj_co2,_=emissions_model.estimate(ac,adj_km)
        extra_co2=round(adj_co2-base_co2,2)
        base_int=emissions_model.interpret(base_co2,direct_km)
        adj_int=emissions_model.interpret(adj_co2,adj_km)

        risk_risk={"Shortest":("Higher","Moderate"),"Safer":("Higher","Lower"),
                   "Greener":("Moderate","Moderate"),"Balanced":("Higher","Reduced")}
        base_risk,adj_risk=risk_risk[mode_key]

        # OpenSky lookup
        real_flights=0; real_types=""
        if _flight_df is not None:
            rf=_flight_df[(_flight_df["origin"]==o_icao)&(_flight_df["destination"]==d_icao)]
            real_flights=len(rf)
            if real_flights>0:
                top_tc=rf["typecode"].dropna().value_counts().head(3).index.tolist()
                real_types=", ".join(top_tc) if top_tc else "N/A"

        add_history({"Type":f"Route — {mode_key}","Aircraft":ac,"Distance (km)":adj_km,
                     "Risk Class":adj_risk,"Risk Score":"-","CO2 (kg)":adj_co2})

        # ── Conflict zone warning
        if direct_hits and mode_key=="Shortest":
            zones_str=", ".join(f'<b>{z["name"].split(" (")[0]}</b>' for z in direct_hits)
            st.markdown(f"""
            <div class="glass-card" style="border-left:4px solid #ef4444;">
                ⛔ <b>Direct route crosses active conflict zones:</b> {zones_str}<br>
                <span style="color:#94a3b8;font-size:.87rem;">
                Real airlines are currently avoiding or rerouting around these FIRs.
                Switch to <b>Safer</b> or <b>Balanced</b> mode to see the avoidance route.
                </span>
            </div>""", unsafe_allow_html=True)
        elif mode_key != "Shortest" and not adj_hits:
            st.markdown(f"""
            <div class="glass-card" style="border-left:4px solid #22c55e;">
                ✅ <b>{mode_key} route avoids all active conflict zones</b><br>
                <span style="color:#94a3b8;font-size:.87rem;">
                Routing via {safe_route_name}. This adds {extra_km:,} km but avoids EASA CZIB-restricted airspace.
                </span>
            </div>""", unsafe_allow_html=True)

        # ── Metrics
        st.subheader("Route Comparison")
        m1,m2,m3=st.columns(3)
        m1.metric("Direct Distance",f"{direct_km:,} km")
        m2.metric("Adjusted Distance",f"{adj_km:,} km")
        m3.metric("Extra Distance",f"{extra_km:,} km")
        m4,m5,m6=st.columns(3)
        m4.metric("Baseline CO₂",f"{base_co2:,.0f} kg")
        m5.metric("Adjusted CO₂",f"{adj_co2:,.0f} kg")
        m6.metric("Extra CO₂",f"{extra_co2:,.0f} kg")
        ce1,ce2=st.columns(2)
        with ce1: st.markdown(f'<div class="glass-card"><b>Baseline Emission Level:</b> <span style="color:{base_int["colour"]};font-weight:700;">{base_int["level"]}</span></div>',unsafe_allow_html=True)
        with ce2: st.markdown(f'<div class="glass-card"><b>Adjusted Emission Level:</b> <span style="color:{adj_int["colour"]};font-weight:700;">{adj_int["level"]}</span></div>',unsafe_allow_html=True)

        if _flight_df is not None:
            bd="#22c55e" if real_flights>0 else "#475569"
            body=(f"Found <b>{real_flights}</b> recorded flights on <b>{o_icao}→{d_icao}</b>. Types: <b>{real_types}</b>" if real_flights>0 else f"No flights found for {o_icao}→{d_icao} in sample.")
            st.markdown(f'<div class="glass-card" style="border-left:3px solid {bd};"><b>📡 OpenSky Flight Data (Jan–May 2019)</b><br>{body}</div>',unsafe_allow_html=True)

        st.subheader("Risk Comparison")
        st.markdown(f'<div class="glass-card"><b>Direct Route Risk:</b> {base_risk}<br><b>Adjusted Route Risk:</b> {adj_risk}</div>',unsafe_allow_html=True)

        # ── FOLIUM MAP with conflict zones
        st.subheader("Route Map")
        m=folium.Map(location=[(o_lat+d_lat)/2,(o_lon+d_lon)/2],zoom_start=3,tiles="CartoDB dark_matter")

        # Draw conflict zone polygons
        for zone in CONFLICT_ZONES:
            if zone["level"]=="critical": fill_op,weight=0.25,2
            elif zone["level"]=="high":   fill_op,weight=0.15,1.5
            else:                         fill_op,weight=0.10,1
            folium.Polygon(
                locations=zone["polygon"],
                color=zone["colour"],
                weight=weight,
                fill=True,
                fill_color=zone["fill_colour"],
                fill_opacity=fill_op,
                tooltip=f"⚠ {zone['name']} — {zone['status']}\n{zone['detail']}\nSource: {zone['source']}",
                popup=folium.Popup(
                    f"<b>{zone['name']}</b><br><b>Status:</b> {zone['status']}<br>"
                    f"{zone['detail']}<br><i>Source: {zone['source']}</i>",
                    max_width=300
                )
            ).add_to(m)

        # Airport dots
        for ap_name,ap_info in AIRPORTS.items():
            folium.CircleMarker(location=ap_info["coords"],radius=3,color="#475569",
                fill=True,fill_color="#475569",fill_opacity=0.6,tooltip=ap_name).add_to(m)

        # Origin / destination markers
        folium.Marker(location=(o_lat,o_lon),
            popup=folium.Popup(f"<b>Origin</b><br>{oa}",max_width=220),tooltip=f"Origin: {oa}",
            icon=folium.Icon(color="blue",icon="plane",prefix="fa")).add_to(m)
        folium.Marker(location=(d_lat,d_lon),
            popup=folium.Popup(f"<b>Destination</b><br>{da}",max_width=220),tooltip=f"Destination: {da}",
            icon=folium.Icon(color="red",icon="map-marker",prefix="fa")).add_to(m)

        # Direct route (always shown — dashed if it hits conflict zones)
        folium.PolyLine(direct_pts,color="#3b82f6",weight=2.5,opacity=0.7,
            dash_array="6" if direct_hits else None,
            tooltip=f"Direct: {direct_km:,} km{'  ⚠ CONFLICT ZONES' if direct_hits else ''}").add_to(m)

        # Adjusted route
        if mode_key!="Shortest":
            folium.PolyLine(adj_pts,color="#22c55e",weight=3,opacity=0.9,
                tooltip=f"{mode_key} route: {adj_km:,} km (avoidance)").add_to(m)

        components.html(folium_to_html(m),height=560,scrolling=False)

        # ── Map legend
        leg_zones=[(z["colour"],z["name"].split(" (")[0],z["status"]) for z in CONFLICT_ZONES[:6]]
        leg_html="".join(f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.2rem;"><div style="width:14px;height:14px;background:{c};border-radius:2px;"></div><span style="font-size:.8rem;color:#e5e7eb;">{n} — {s}</span></div>' for c,n,s in leg_zones)
        st.markdown(f'<div class="glass-card"><b>Map Legend</b><br><div style="display:flex;align-items:center;gap:.5rem;margin:.4rem 0;"><div style="width:20px;height:3px;background:#3b82f6;"></div><span style="font-size:.82rem;">Direct route</span>&nbsp;&nbsp;<div style="width:20px;height:3px;background:#22c55e;"></div><span style="font-size:.82rem;">{mode_key} route</span></div>{leg_html}<span style="color:#64748b;font-size:.78rem;">Click any shaded zone for details. Source: EASA CZIB 2026-03-R5.</span></div>',unsafe_allow_html=True)

        st.subheader("Interpretation")
        d_ac=AIRCRAFT_CATALOGUE.get(ac,{})
        st.markdown(f"""
        <div class="glass-card">
            <b>Route:</b> {oa} → {da} ({direct_km:,} km direct · {adj_km:,} km {mode_key.lower()})<br>
            <b>Aircraft:</b> {d_ac.get("maker","")} {ac} — {d_ac.get("engines","")}<br>
            <b>CO₂ Factor (EASA EDB v31):</b> {factor} kg/km<br><br>
            {'<b>⚠ Direct route conflicts:</b> ' + ", ".join(z["name"].split(" (")[0] for z in direct_hits) + "<br>" if direct_hits else ""}
            {'<b>✅ Adjusted route:</b> ' + safe_route_name + "<br>" if mode_key!="Shortest" else ""}
            <br>The {mode_key.lower()} route adds <b>{extra_km:,} km</b> and approximately
            <b>{extra_co2:,.0f} kg of extra CO₂</b> but {"reduces exposure to EASA-restricted conflict zones." if mode_key in ("Safer","Balanced") else "maintains the shortest path."}
        </div>""", unsafe_allow_html=True)


# ================================================================
# AIRCRAFT EXPLORER
# ================================================================
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
def page_testing():
    st.title("Testing & Evaluation")
    if risk_model.trained_on_data:
        rd=risk_model.risk_dist
        st.markdown(f'<div class="glass-card" style="border-left:3px solid #22c55e;"><b>✓ Data-Driven</b> — {risk_model.n_training:,} NTSB records, Laplace α=1. High:{rd.get("High",0):,} · Med:{rd.get("Medium",0):,} · Low:{rd.get("Low",0):,}</div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="glass-card" style="border-left:3px solid #f59e0b;"><b>⚠ Prototype Mode</b> — NTSB CSV not found at {AVIATION_CSV}</div>',unsafe_allow_html=True)

    st.subheader("Risk Model Tests")
    for s in [{"name":"Safe","weather":"low","maintenance":"good","aircraft_age":"new","route_complexity":"low","congestion":"low","expected":"Low"},
              {"name":"Moderate","weather":"medium","maintenance":"fair","aircraft_age":"mid","route_complexity":"medium","congestion":"medium","expected":"Medium"},
              {"name":"High Risk","weather":"high","maintenance":"poor","aircraft_age":"old","route_complexity":"high","congestion":"high","expected":"High"}]:
        inp={k:s[k] for k in["weather","maintenance","aircraft_age","route_complexity","congestion"]}
        res=risk_model.predict(inp); passed="✅" if res["class"]==s["expected"] else "⚠️"
        st.markdown(f'<div class="glass-card" style="margin-bottom:.75rem;"><b>{s["name"]}</b> · Expected: {s["expected"]} · Got: {res["class"]} · Score: {res["score"]}/100 · {passed}<br>Posteriors: Low={res["probabilities"]["Low"]*100:.1f}% | Med={res["probabilities"]["Medium"]*100:.1f}% | High={res["probabilities"]["High"]*100:.1f}%</div>',unsafe_allow_html=True)

    st.subheader("Fuel Efficiency Tests")
    for a in ["A320neo","A350-900","B787-9","B777-300ER","A380"]:
        m=fuel_model.compute(a,5000,0.85)
        st.markdown(f'<div class="glass-card" style="margin-bottom:.5rem;"><b>{a}</b> · 5,000 km · 85% load → {m["l100"]} L/100pkm · {m["co2_pax"]} kg CO₂/pax · {m["rating"]}</div>',unsafe_allow_html=True)

    st.subheader("Conflict Zone Coverage")
    for z in CONFLICT_ZONES:
        col={"critical":"#ef4444","high":"#f97316","elevated":"#f59e0b"}.get(z["level"],"#94a3b8")
        st.markdown(f'<div class="glass-card" style="margin-bottom:.4rem;border-left:3px solid {col};padding:.7rem 1rem;"><b>{z["name"]}</b> · <span style="color:{col};">{z["status"]}</span><br><span style="color:#94a3b8;font-size:.83rem;">{z["source"]} — {z["detail"][:100]}…</span></div>',unsafe_allow_html=True)

    st.subheader("Aims & Objectives Checklist")
    for icon,aim,ev in[
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
        st.markdown(f'<div class="glass-card" style="padding:.8rem 1.1rem;margin-bottom:.5rem;">{icon} <b>{aim}</b><br><span style="color:#94a3b8;font-size:.85rem;">→ {ev}</span></div>',unsafe_allow_html=True)


# ================================================================
# ENTRY POINT
# ================================================================
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