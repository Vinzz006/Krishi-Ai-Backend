import uuid
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import base64

from models.schemas import QueryRequest, AIResponse
from services.crop_knowledge import build_context
from services.ai_service import process_query

router = APIRouter()

# In-memory history store
query_history = []

@router.post("/", response_model=AIResponse)
async def handle_query(request: QueryRequest):
    """Main AI query endpoint — handles text and image queries"""
    context = build_context(
        query=request.query,
        crop_type=request.crop_type,
        location=request.location
    )

    result = await process_query(
        query=request.query,
        context=context,
        language=request.language.value,
        image_base64=request.image_base64
    )

    # Store in history
    history_item = {
        "id": str(uuid.uuid4()),
        "farmer_id": request.farmer_id or "guest",
        "query": request.query,
        "response": result["answer"],
        "timestamp": datetime.now().isoformat(),
        "category": result["category"],
        "query_type": request.query_type.value
    }
    query_history.append(history_item)

    return AIResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        category=result["category"],
        related_crops=result["related_crops"],
        schemes=result["schemes"],
        escalate=result["escalate"],
        sources=result["sources"]
    )

@router.post("/image")
async def handle_image_query(
    query: str = Form(default="What disease does this plant have?"),
    language: str = Form(default="en"),
    farmer_id: Optional[str] = Form(default=None),
    image: UploadFile = File(...)
):
    """Image-based disease detection endpoint"""
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    context = build_context(query=query)
    result = await process_query(
        query=query,
        context=context,
        language=language,
        image_base64=image_base64
    )

    return AIResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        category=result["category"],
        related_crops=result["related_crops"],
        schemes=result["schemes"],
        escalate=result["escalate"],
        sources=result["sources"]
    )
