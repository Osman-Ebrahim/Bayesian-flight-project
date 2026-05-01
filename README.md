# ✈️ Bayesian Aviation Decision-Support System

**BSc Computer Science Final Year Project**  
Osman Ebrahim · University of Roehampton · 2026

## 📖 Overview

A Bayesian probabilistic decision-support system for aviation risk assessment, fuel efficiency analysis, CO₂ emissions estimation, and conflict zone route planning. Built entirely in Python using Streamlit, the system trains a Naive Bayes classifier on 88,000+ real NTSB accident records and produces both a risk classification and a Bayesian-weighted CO₂ estimate in a single unified inference pass.

This project originated from an AI essay on Bayesian inference in aviation — awarded the highest grade the supervising professor had ever given — and was developed into a full-stack data science application over a five-sprint development cycle.


## 🚀 Features

| Page | Access | Description |
|------|--------|-------------|
| Home | Public | Live NTSB metrics, OpenSky stats, module overview |
| Risk Analysis | Public | Flight number lookup via AviationStack API or manual entry → Bayesian risk score + CO₂ |
| Fuel Efficiency | Public | Compare all 28 aircraft variants by L/100pkm, CO₂/pax, and ASK/kg |
| Emissions Analysis | Public | Aircraft + distance → CO₂ estimate with car and tree equivalents |
| Aircraft Explorer | Public | 360° Sketchfab engine model + EASA EDB v31 specs |
| Scenario History | Public | Review and export all past analyses as CSV |
| Ethics & Implications | Public | BCS duty mapping, AI Act compliance, academic disclaimer |
| Route Planner | **Admin** | 777 airports × 200 countries · 14 EASA CZIB conflict zone polygons · Safer / Balanced / Greener modes |
| Testing & Evaluation | **Admin** | Three risk scenarios, fuel validation, conflict zone coverage, aims checklist |


## 🧠 The Model

The **UnifiedBayesianModel** performs a single `predict()` call that returns both:
- **Risk classification** — Low / Medium / High with posterior probabilities
- **Expected CO₂** — Bayesian-weighted across risk classes using per-class overhead factors
log P(C | X) = log P(C) + Σ log P(xᵢ | C)    [Laplace smoothing α=1]
CO₂ = Σ P(C|X) × base_CO₂ × overhead(C)

Trained on **88,305 NTSB accident records** (Jan 1982 – Dec 2023) with 6 engineered features:
`weather` · `maintenance` · `aircraft_age` · `route_complexity` · `congestion` · `phase_of_flight`


## 🗂️ Project Structure
bayesian-flight-project/
├── app.py                    # Entry point — Streamlit config + page routing
├── models/
│   ├── bayesian_model.py     # UnifiedBayesianModel + FuelEfficiencyModel + data loaders
│   └── globals.py            # Module-level bootstrap — all shared state
├── routing/
│   └── geo_utils.py          # Haversine · great-circle · ray-casting · avoidance routing
├── data/
│   ├── airports.py           # 777 airports · 200 countries
│   ├── aircraft.py           # 28 variants from EASA EDB v31
│   ├── conflict_zones.py     # 14 EASA CZIB polygons
│   └── raw/                  # AviationData.csv · flightlist_*.csv.gz (not tracked in git)
├── pages/
│   ├── page_home.py
│   ├── page_risk.py
│   ├── page_route.py
│   ├── page_fuel.py
│   ├── page_emissions.py
│   ├── page_aircraft.py
│   ├── page_history.py
│   ├── page_ethics.py
│   └── page_testing.py
├── ui/
│   ├── layout.py             # render_header · get_pages · admin auth
│   └── styles.py             # inject_css · dark theme
└── utils/
└── api_client.py         # AviationStack lookup · _IATA_COORDS (490 entries)


## ⚙️ Setup and Installation

### Prerequisites
- Python 3.11
- Anaconda (recommended)

### Install dependencies

```bash
conda activate base
pip install streamlit pandas numpy folium requests
```

### Data files required (not in repo — too large)

Place the following in `data/raw/`:
- `AviationData.csv` — from [NTSB Aviation Accident Database](https://www.ntsb.gov/investigations/AccidentReports/Pages/aviation.aspx)
- `flightlist_*.csv.gz` — from [OpenSky Network](https://opensky-network.org/)

### Run the app

```bash
cd bayesian-flight-project
streamlit run app.py
```

App runs at `http://localhost:8501`

### Admin access

The Route Planner and Testing & Evaluation pages require admin login.  
Credentials are set in `ui/layout.py`.


## 📊 Data Sources

| Source | Description | Used for |
|--------|-------------|----------|
| [NTSB Aviation Accident Database](https://www.ntsb.gov) | 88,305 accident records | Model training |
| [OpenSky Network](https://opensky-network.org) | Flightlist CSVs Jan–May 2019 | Route cross-reference |
| [EASA Engine Emissions Databank v31](https://www.easa.europa.eu) | CO₂ factors for 28 aircraft | Fuel + emissions pages |
| [EASA CZIB 2026-03-R5](https://www.easa.europa.eu/en/domains/air-operations/czibs) | 14 conflict zone polygons | Route Planner avoidance |
| [AviationStack API](https://aviationstack.com) | Live flight data | Risk Analysis lookup |
| [Folium / CartoDB](https://python-visualization.github.io/folium/) | Interactive maps | Route Planner map |
| [Sketchfab](https://sketchfab.com) | 360° engine model | Aircraft Explorer |


## 🔬 Novel Findings

1. **IMC approach risk amplification** — 67.3% of fatal accidents occur during takeoff/approach/landing; IMC × approach phase produces higher High-risk classifications than Naive Bayes independence would predict
2. **Amateur-built aircraft tail risk** — 12% of NTSB records but 31% of High-risk classifications
3. **OpenSky OMDB→OMDB artefact** — 2,400+ ground movements logged as flights, resolved via same-origin-destination filtering
4. **Non-linear conflict zone overhead** — LHR→DXB crosses 5 conflict zones but produces only 27% distance overhead, consistent with real-world airline routing since February 2026


## ⚠️ Disclaimer

This system is a **prototype for academic research purposes only**. It does not constitute certified aviation guidance and must not replace licensed flight planning systems, qualified aviation personnel, or official NOTAM/CZIB advisories. All risk classifications are probabilistic estimates based on historical accident data.


## 📄 Licence

Academic project — University of Roehampton, 2026.  
All rights reserved. © Osman Ebrahim 2026.
