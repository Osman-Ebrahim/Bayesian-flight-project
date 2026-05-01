# models/bayesian_model.py

import os,math,gzip,glob
import pandas as pd
import streamlit as st
from data.aircraft import AIRCRAFT_CATALOGUE

def _find_data_raw():
    """
    Locate data/raw by searching:
    1. Up to 4 parent folders from models/
    2. Sibling folder 'bayesian-flight-project/data/raw' (where datasets live)
    3. Fallback to cwd/data/raw
    """
    here = os.path.abspath(os.path.dirname(__file__))
    candidate = here
    for _ in range(4):
        # Direct match inside this folder
        p = os.path.join(candidate, "data", "raw")
        if os.path.isdir(p):
            return p
        # Sibling bayesian-flight-project folder (case variants)
        for sibling_name in ["bayesian-flight-project", "Bayesian-flight-project",
                              "bayesian_flight_project"]:
            s = os.path.join(candidate, sibling_name, "data", "raw")
            if os.path.isdir(s):
                return s
        candidate = os.path.dirname(candidate)
    return os.path.join(os.getcwd(), "data", "raw")

DATA_RAW     = _find_data_raw()
AVIATION_CSV = os.path.join(DATA_RAW, "archive", "AviationData.csv")
NTSB_CSV     = os.path.join(DATA_RAW, "archive", "NTSB_database.csv")
FLIGHT_GLOB  = os.path.join(DATA_RAW, "flightlist_*.csv")


# ================================================================

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