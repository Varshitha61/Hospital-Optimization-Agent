import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from api import hospital_agent

app = FastAPI(title="Hospital Quick Find API")

# Allow CORS so our static frontend can communicate seamlessly with the backend
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
    # Call the exact same agent logic you used in Streamlit!
    result = hospital_agent.main(req.symptoms, req.lat, req.lng)
    return result

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/api/health")
async def health_check():
    return {"status": "Vercel API is running!"}

# Serve the frontend locally from the public directory
if os.path.exists("public"):
    app.mount("/public", StaticFiles(directory="public"), name="public")
    @app.get("/")
    async def serve_index():
        return FileResponse("public/index.html")
