from fastapi import APIRouter
from routers.query import query_history

router = APIRouter()

@router.get("/")
async def get_history(farmer_id: str = "guest", limit: int = 20):
    farmer_history = [h for h in query_history if h["farmer_id"] == farmer_id]
    farmer_history = sorted(farmer_history, key=lambda x: x["timestamp"], reverse=True)
    return {
        "status": "success",
        "farmer_id": farmer_id,
        "count": len(farmer_history),
        "data": farmer_history[:limit]
    }

@router.delete("/{item_id}")
async def delete_history_item(item_id: str):
    global query_history
    query_history = [h for h in query_history if h["id"] != item_id]
    return {"status": "success", "message": "History item deleted"}

@router.delete("/")
async def clear_history(farmer_id: str = "guest"):
    global query_history
    query_history = [h for h in query_history if h["farmer_id"] != farmer_id]
    return {"status": "success", "message": "History cleared"}
