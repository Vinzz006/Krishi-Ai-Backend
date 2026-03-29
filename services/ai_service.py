import os
import json
import base64
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_MOCK = not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here"

if not USE_MOCK:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are KrishiAI, an expert Digital Krishi Officer for Kerala farmers.
You provide accurate, actionable agricultural advice in simple language.
Focus on: crop diseases, pest management, fertilizers, best practices, government schemes, market info.
Keep answers concise, practical, and farmer-friendly.
Format with bullet points and bold headings where helpful.
Always mention safety precautions when recommending chemicals.
If unsure, recommend consulting the local Krishi Bhavan."""

async def get_openai_response(query: str, context: dict, language: str = "en") -> str:
    lang_instruction = ""
    if language == "ml":
        lang_instruction = "Respond in Malayalam language (മലയാളം)."
    elif language == "hi":
        lang_instruction = "Respond in Hindi language."

    crop_ctx = ""
    if context.get("crop_info"):
        c = context["crop_info"]
        crop_ctx = f"\nFarmer's primary crop: {c.get('name', '')}\nLocation: {context.get('location', 'Kerala')}"

    prompt = f"""{SYSTEM_PROMPT}
{lang_instruction}
{crop_ctx}

Farmer's Question: {query}

Provide a detailed, helpful answer with:
- Clear diagnosis/solution
- Step-by-step treatment if applicable
- Preventive measures
- Any relevant government schemes
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def get_openai_image_response(query: str, image_base64: str, language: str = "en") -> str:
    lang_instruction = "Respond in Malayalam." if language == "ml" else ""
    prompt = f"""{SYSTEM_PROMPT}
{lang_instruction}
A farmer has uploaded an image of their crop and asks: "{query}"
Analyze the image carefully and:
1. Identify any visible diseases, pests, or nutrient deficiencies
2. Name the problem clearly
3. Suggest immediate treatment steps
4. Recommend preventive measures
5. Mention if this needs urgent attention"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content

def get_mock_response(query: str, context: dict, language: str = "en") -> str:
    """Smart mock responses using local knowledge base"""
    from services.crop_knowledge import format_crop_response

    category = context.get("category", "general")
    crop_info = context.get("crop_info", {})
    pest_info = context.get("pest_info", [])
    schemes = context.get("relevant_schemes", [])
    detected_crops = context.get("detected_crops", [])

    q_lower = query.lower()

    # Disease/pest specific keyword matching
    for pest in pest_info:
        pest_name = pest.get("name", "").lower()
        pest_keywords = [pest_name] + [s.lower() for s in pest.get("symptoms", [])]
        if any(kw in q_lower for kw in pest_keywords[:3]):
            ctrl = pest.get("control", {})
            symptoms_list = "\n".join(f"• {s}" for s in pest.get("symptoms", [])[:3])
            organic = "\n".join(f"• {o}" for o in ctrl.get("organic", [])[:2])
            chemical = "\n".join(f"• {c}" for c in ctrl.get("chemical", [])[:2])
            preventive = "\n".join(f"• {p}" for p in ctrl.get("preventive", [])[:2])
            severity = pest.get("severity", "medium").upper()

            ml_suffix = "\n\n🌾 *ഈ വിവരം KrishiAI വഴി ലഭിച്ചു. കൂടുതൽ സഹായത്തിന് നിങ്ങളുടെ കൃഷി ഭവൻ സന്ദർശിക്കുക.*" if language == "ml" else ""

            return f"""## 🔴 {pest['name']} — Severity: {severity}

**Symptoms Identified:**
{symptoms_list}

**🌿 Organic Control:**
{organic}

**💊 Chemical Control:**
{chemical}

**🛡️ Prevention:**
{preventive}

> ⚠️ Always wear protective gear when applying chemicals. Follow label instructions carefully.
{ml_suffix}"""

    # Fertilizer queries
    if category == "fertilizer" and crop_info:
        fert = crop_info.get("fertilizers", {})
        name = crop_info.get("name", "your crop")
        return f"""## 🌱 Fertilizer Guide for {name}

**NPK Recommendation:** {fert.get('NPK', 'As per soil test')}

**Organic Inputs:** {fert.get('organic', 'Apply 5 tonnes FYM per hectare')}

**Application Schedule:** {fert.get('schedule', 'Apply in 2-3 splits during crop growth')}

**Micronutrients:** {fert.get('micronutrients', 'Apply zinc sulfate (25 kg/ha) if deficiency is visible')}

> 💡 **Pro Tip:** Get your free Soil Health Card from Krishi Bhavan for precision fertilizer recommendations tailored to your field.

**Relevant Scheme:** Soil Health Card Scheme — Free soil testing at nearest Krishi Bhavan."""

    # Scheme queries
    if category == "scheme" and schemes:
        scheme_text = "\n\n".join([
            f"### 📋 {s['name']}\n**Benefit:** {s['benefit']}\n**Apply at:** {s['how_to_apply']}\n**Contact:** {s.get('contact', 'Nearest Krishi Bhavan')}"
            for s in schemes[:3]
        ])
        return f"""## 🏛️ Government Schemes for Farmers

{scheme_text}

> 📞 For more details, visit your nearest **Krishi Bhavan** or call **Kisan Call Centre: 1800-180-1551** (toll-free, 24/7)"""

    # Crop-specific general advice
    if crop_info:
        return format_crop_response(crop_info, category, pest_info)

    # Market query
    if category == "market":
        return """## 📊 Today's Market Overview (Kerala)

| Commodity | Market | Price |
|-----------|--------|-------|
| Rubber (RSS4) | Kottayam | ₹195/kg |
| Coconut (Ball) | Kozhikode | ₹2450/100 nuts |
| Black Pepper | Kochi | ₹680/kg |
| Banana (Nendran) | TVM | ₹55/kg |
| Paddy | Thrissur | ₹21.83/kg (MSP) |

> 📱 Check the **Market Prices** section for live rates from all Kerala mandis."""

    # General fallback
    return f"""## 🌾 KrishiAI Advisory

Thank you for your question: *"{query}"*

Based on your query, here's my advice:

• Consult your local **Krishi Bhavan** for field-specific guidance
• Call **Kisan Call Centre: 1800-180-1551** (free, 24/7 in Malayalam)
• Upload a photo of affected plants for more accurate disease diagnosis

**Common resources:**
• agrikerala.gov.in — Kerala Agriculture Department
• Soil testing: Free at every Krishi Bhavan
• Emergency Pest Alert: Contact your local Agricultural Officer

> 🤖 *For more precise AI analysis, add your OpenAI API key in the backend .env file.*"""

async def process_query(query: str, context: dict, language: str = "en", image_base64: str = None) -> dict:
    answer = None
    confidence = 0.75
    used_openai = False

    # Try OpenAI first if not explicitly in mock mode
    if not USE_MOCK:
        try:
            if image_base64:
                answer = await get_openai_image_response(query, image_base64, language)
                confidence = 0.95
            else:
                answer = await get_openai_response(query, context, language)
                confidence = 0.92
            used_openai = True
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Gracefully fall back to local knowledge base
            answer = None

    # Use local knowledge base (mock) if OpenAI unavailable or failed
    if answer is None:
        try:
            answer = get_mock_response(query, context, language)
            confidence = 0.78
            used_openai = False
        except Exception as e:
            answer = f"I encountered an error processing your query. Please try again or contact your local Krishi Bhavan.\n\n*Error: {str(e)}*"
            return {
                "answer": answer,
                "confidence": 0.0,
                "category": "error",
                "related_crops": [],
                "schemes": [],
                "escalate": True,
                "sources": []
            }

    schemes = context.get("relevant_schemes", [])
    scheme_names = [s["name"] for s in schemes[:2]]

    return {
        "answer": answer,
        "confidence": confidence,
        "category": context.get("category", "general"),
        "related_crops": context.get("detected_crops", []),
        "schemes": scheme_names,
        "escalate": confidence < 0.5,
        "sources": ["OpenAI GPT-4o", "KrishiAI Knowledge Base"] if used_openai else ["KrishiAI Knowledge Base", "Kerala Agriculture Dept"]
    }
