# data/aircraft.py

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
