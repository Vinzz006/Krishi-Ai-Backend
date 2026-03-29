import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()
DATA_FILE = Path(__file__).parent.parent / "data" / "market_prices.json"

@router.get("/")
async def get_market_prices(commodity: str = None, district: str = None):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        prices = json.load(f)

    if commodity:
        prices = [p for p in prices if commodity.lower() in p["commodity"].lower()]

    return {
        "status": "success",
        "count": len(prices),
        "last_updated": "2026-03-28",
        "source": "Kerala State Agricultural Marketing Board",
        "data": prices
    }

@router.get("/summary")
async def get_market_summary():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        prices = json.load(f)

    gainers = [p for p in prices if p.get("change", 0) > 0]
    losers  = [p for p in prices if p.get("change", 0) < 0]

    return {
        "total_commodities": len(prices),
        "gainers": len(gainers),
        "losers": len(losers),
        "unchanged": len(prices) - len(gainers) - len(losers),
        "top_gainer": max(prices, key=lambda x: x.get("change", 0))["commodity"] if gainers else None,
        "top_loser": min(prices, key=lambda x: x.get("change", 0))["commodity"] if losers else None,
    }
