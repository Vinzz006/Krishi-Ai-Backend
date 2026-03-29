import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()
DATA_FILE = Path(__file__).parent.parent / "data" / "schemes.json"

@router.get("/")
async def get_schemes(type: str = None, crop: str = None):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    if type:
        schemes = [s for s in schemes if s["type"].lower() == type.lower()]

    crop_scheme_map = {
        "coconut": ["coconut-development", "pm-kisan", "fasal-bima", "agri-mechanization"],
        "rubber": ["rubber-replanting", "pm-kisan", "kisan-credit"],
        "paddy": ["pm-kisan", "fasal-bima", "kisan-credit", "soil-health-card", "kerala-karshaka"],
        "banana": ["pm-kisan", "fasal-bima", "krishi-bhavan-support"],
        "pepper": ["pm-kisan", "fasal-bima", "krishi-bhavan-support"],
    }

    if crop and crop in crop_scheme_map:
        ids = crop_scheme_map[crop]
        schemes = [s for s in schemes if s["id"] in ids]

    return {
        "status": "success",
        "count": len(schemes),
        "data": schemes
    }

@router.get("/{scheme_id}")
async def get_scheme_detail(scheme_id: str):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    for s in schemes:
        if s["id"] == scheme_id:
            return {"status": "success", "data": s}
    return {"status": "error", "message": "Scheme not found"}
