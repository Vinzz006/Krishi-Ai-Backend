import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

CROPS = load_json("crops.json")
PESTS = load_json("pests.json")
SCHEMES = load_json("schemes.json")

KEYWORDS = {
    "paddy": ["paddy", "rice", "നെല്ല്", "rice cultivation", "blast", "hopper"],
    "coconut": ["coconut", "തേങ്ങ", "copra", "coconut palm", "rhinoceros"],
    "banana": ["banana", "വാഴ", "നേന്ദ്ര", "plantain", "bunchy top"],
    "rubber": ["rubber", "റബ്ബർ", "latex", "tapping"],
    "pepper": ["pepper", "കുരുമുളക്", "spice", "black pepper", "foot rot", "quick wilt"],
    "tapioca": ["tapioca", "കപ്പ", "cassava", "yuca"],
    "ginger": ["ginger", "ഇഞ്ചി", "rhizome", "soft rot"],
    "vegetable": ["vegetable", "പച്ചക്കറി", "bitter gourd", "snake gourd", "tomato", "okra"],
}

DISEASE_KEYWORDS = [
    "disease", "pest", "infection", "rot", "wilt", "blight", "spot", "moth",
    "insect", "fungus", "virus", "bacteria", "yellowing", "dying", "damage",
    "hopper", "beetle", "caterpillar", "mite", "aphid", "weevil", "bore"
]

FERTILIZER_KEYWORDS = [
    "fertilizer", "nutrient", "nitrogen", "phosphorus", "potassium", "npk",
    "deficiency", "manure", "compost", "organic", "urea", "feeding", "feed"
]

SCHEME_KEYWORDS = [
    "scheme", "subsidy", "government", "pm kisan", "insurance", "loan",
    "credit", "pension", "support", "benefit", "apply", "yojana", "grant"
]

WEATHER_KEYWORDS = [
    "weather", "rain", "monsoon", "drought", "flood", "temperature", "climate",
    "forecast", "humidity", "wind", "season"
]

MARKET_KEYWORDS = [
    "price", "market", "rate", "sell", "mandi", "value", "cost", "profit", "income"
]

def detect_crop(query: str) -> list:
    q = query.lower()
    detected = []
    for crop, keys in KEYWORDS.items():
        if any(k in q for k in keys):
            detected.append(crop)
    return detected

def detect_category(query: str) -> str:
    q = query.lower()
    if any(k in q for k in DISEASE_KEYWORDS):
        return "disease_pest"
    if any(k in q for k in FERTILIZER_KEYWORDS):
        return "fertilizer"
    if any(k in q for k in SCHEME_KEYWORDS):
        return "scheme"
    if any(k in q for k in WEATHER_KEYWORDS):
        return "weather"
    if any(k in q for k in MARKET_KEYWORDS):
        return "market"
    return "general"

def get_crop_info(crop_id: str) -> dict:
    for crop in CROPS:
        if crop["id"] == crop_id:
            return crop
    return {}

def get_pest_info(crop_id: str) -> list:
    return [p for p in PESTS if p.get("crop") == crop_id]

def get_relevant_schemes(crop_id: str = None) -> list:
    if not crop_id:
        return SCHEMES[:4]
    crop_map = {
        "coconut": ["coconut-development", "pm-kisan", "fasal-bima"],
        "rubber": ["rubber-replanting", "pm-kisan"],
        "paddy": ["pm-kisan", "fasal-bima", "kisan-credit", "soil-health-card"],
        "banana": ["pm-kisan", "fasal-bima", "krishi-bhavan-support"],
        "pepper": ["pm-kisan", "fasal-bima", "krishi-bhavan-support"],
    }
    ids = crop_map.get(crop_id, ["pm-kisan", "fasal-bima", "kisan-credit"])
    return [s for s in SCHEMES if s["id"] in ids]

def build_context(query: str, crop_type: str = None, location: str = None) -> dict:
    detected_crops = detect_crop(query)
    if crop_type and crop_type not in detected_crops:
        detected_crops.insert(0, crop_type)

    category = detect_category(query)
    primary_crop = detected_crops[0] if detected_crops else None

    crop_info = get_crop_info(primary_crop) if primary_crop else {}
    pest_info = get_pest_info(primary_crop) if primary_crop else []
    relevant_schemes = get_relevant_schemes(primary_crop)

    return {
        "detected_crops": detected_crops,
        "category": category,
        "crop_info": crop_info,
        "pest_info": pest_info,
        "relevant_schemes": relevant_schemes,
        "location": location or "Kerala",
    }

def format_crop_response(crop_info: dict, category: str, pest_info: list) -> str:
    name = crop_info.get("name", "this crop")

    if category == "disease_pest":
        if pest_info:
            p = pest_info[0]
            ctrl = p.get("control", {})
            return (
                f"**{p['name']}** detected for {name}.\n\n"
                f"**Symptoms:** {', '.join(p.get('symptoms', [])[:2])}\n\n"
                f"**Organic Control:** {'; '.join(ctrl.get('organic', [])[:2])}\n\n"
                f"**Chemical Control:** {'; '.join(ctrl.get('chemical', [])[:2])}\n\n"
                f"**Prevention:** {'; '.join(ctrl.get('preventive', [])[:2])}"
            )
        return f"For {name}, monitor regularly for {', '.join(crop_info.get('common_diseases', [])[:3])}. Use IPM practices."

    if category == "fertilizer":
        fert = crop_info.get("fertilizers", {})
        npk = fert.get("NPK", "As per soil test")
        org = fert.get("organic", "Apply compost 5 tonnes/ha")
        return (
            f"**Fertilizer Recommendation for {name}:**\n\n"
            f"**NPK:** {npk}\n\n"
            f"**Organic:** {org}\n\n"
            f"**Schedule:** {fert.get('schedule', 'Apply in splits — basal + top dressings')}\n\n"
            f"💡 *Get a Soil Health Card (free) from your Krishi Bhavan for customized recommendations.*"
        )

    tips = crop_info.get("tips", [])
    return (
        f"**Advisory for {name}:**\n\n"
        + "\n".join(f"• {t}" for t in tips[:4])
        + f"\n\n**Season:** {', '.join(crop_info.get('season', ['Check locally']))}"
    )
