from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, query, market, weather, schemes, history

app = FastAPI(
    title="KrishiAI API",
    description="AI-Based Farmer Query Support and Advisory System for Kerala",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/api/auth",    tags=["Authentication"])
app.include_router(query.router,   prefix="/api/query",   tags=["AI Query"])
app.include_router(market.router,  prefix="/api/market",  tags=["Market Prices"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["Government Schemes"])
app.include_router(history.router, prefix="/api/history", tags=["Query History"])

@app.get("/")
async def root():
    return {
        "app": "KrishiAI",
        "version": "1.0.0",
        "description": "Digital Krishi Officer — AI Advisory for Kerala Farmers",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "KrishiAI Backend"}
