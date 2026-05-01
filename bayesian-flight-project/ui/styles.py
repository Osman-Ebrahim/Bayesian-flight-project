# ui/styles.py
import streamlit as st

def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)

_CSS = r'''
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

'''
