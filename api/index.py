import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from hospital_agent import main as agent_main

app = FastAPI(title="Hospital Quick Find API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    symptoms: str
    lat: float
    lng: float

@app.post("/api/recommend")
async def recommend_hospital(req: RecommendRequest):
    result = agent_main(req.symptoms, req.lat, req.lng)
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "Vercel API is running!"}
