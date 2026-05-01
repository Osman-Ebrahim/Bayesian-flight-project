# models/globals.py — shared state, all pages do: from models.globals import *
import streamlit as st
from models.bayesian_model import (
    UnifiedBayesianModel, BayesianRiskModel, EmissionsModel,
    FuelEfficiencyModel, load_ntsb_data, load_flight_data, AVIATION_CSV
)
from data.aircraft import AIRCRAFT_CATALOGUE
from data.airports import AIRPORTS, COUNTRIES
from routing.geo_utils import risk_colour, add_history

# Load data — NO with block, plain calls so variables are module-level
_ntsb_df,   _ntsb_meta  = load_ntsb_data()
_flight_df, _flight_err = load_flight_data()

# Model instances
risk_model      = UnifiedBayesianModel(df=_ntsb_df)
emissions_model = risk_model
fuel_model      = FuelEfficiencyModel()

# Dropdown lists
AC_LIST       = sorted(AIRCRAFT_CATALOGUE.keys())
AC_LIST_SHORT = ["A319","A320","A320neo","A321neo","A330neo","A350-900","A380",
                 "B737-800","B737 MAX 8","B777-300ER","B787-8","B787-9"]
