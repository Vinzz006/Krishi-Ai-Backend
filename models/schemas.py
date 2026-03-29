from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Language(str, Enum):
    english = "en"
    malayalam = "ml"
    hindi = "hi"

class QueryType(str, Enum):
    text = "text"
    image = "image"
    voice = "voice"

class QueryRequest(BaseModel):
    query: str
    language: Language = Language.english
    query_type: QueryType = QueryType.text
    farmer_id: Optional[str] = None
    crop_type: Optional[str] = None
    location: Optional[str] = None
    season: Optional[str] = None
    image_base64: Optional[str] = None

class TreatmentDetail(BaseModel):
    organic: List[str] = []
    chemical: List[str] = []
    preventive: List[str] = []

class AIResponse(BaseModel):
    answer: str
    confidence: float
    category: str
    treatments: Optional[TreatmentDetail] = None
    related_crops: List[str] = []
    schemes: List[str] = []
    escalate: bool = False
    sources: List[str] = []

class LoginRequest(BaseModel):
    mobile: str
    otp: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    farmer_id: Optional[str] = None

class FarmerProfile(BaseModel):
    farmer_id: str
    name: str
    mobile: str
    location: str
    district: str
    primary_crop: str
    land_area_acres: float
    preferred_language: Language = Language.english

class HistoryItem(BaseModel):
    id: str
    farmer_id: str
    query: str
    response: str
    timestamp: str
    category: str
    query_type: QueryType = QueryType.text
