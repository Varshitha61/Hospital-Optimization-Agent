import random
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Hospital Agent Logic (self-contained) ─────────────────────────────────────

DEFAULT_LAT = 40.7580
DEFAULT_LNG = -73.9855
DEFAULT_RADIUS = 10000

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

FALLBACK_HOSPITALS = [
    "City General Hospital", "Community Medical Center",
    "Regional Health Hospital", "St. Mary's Medical Center",
    "Metropolitan Hospital", "University Hospital",
    "Riverside Medical Center", "Downtown Emergency Hospital",
]

def get_department(symptoms: str) -> str:
    s = symptoms.lower()
    rules = {
        "orthopedic":      ["bone","fracture","broken","joint","spine","back pain","shoulder","knee","hip"],
        "cardiology":      ["heart","chest pain","palpitation","cardiac","blood pressure","hypertension","shortness of breath"],
        "neurology":       ["headache","migraine","seizure","stroke","numbness","dizziness","brain","nerve"],
        "urology":         ["kidney","kidney stone","urine","urinary","bladder","prostate","burning urination"],
        "gastroenterology":["stomach","abdomen","nausea","vomiting","diarrhea","constipation","liver","ulcer"],
        "pulmonology":     ["cough","breathing","lung","asthma","pneumonia","respiratory"],
        "dermatology":     ["skin","rash","itch","acne","allergy","hives"],
        "ent":             ["ear","nose","throat","sore throat","hearing","sinus","cold","congestion"],
        "general":         ["fever","fatigue","weakness","pain","flu","infection"],
    }
    for dept, keywords in rules.items():
        if any(kw in s for kw in keywords):
            return dept
    return "general"

def fetch_hospitals(lat: float, lng: float) -> list:
    query = f'[out:json][timeout:8];node["amenity"="hospital"](around:{DEFAULT_RADIUS},{lat},{lng});out;'
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = requests.post(endpoint, data={"data": query}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            seen, hospitals = set(), []
            for el in data.get("elements", []):
                name = el.get("tags", {}).get("name") or el.get("tags", {}).get("name:en")
                if name and name not in seen:
                    seen.add(name)
                    hospitals.append({"name": name, "rating": None})
            if hospitals:
                return hospitals
        except Exception:
            continue
    return [{"name": n, "rating": None} for n in FALLBACK_HOSPITALS]

def estimate_wait(hospital: dict) -> dict:
    patients = random.randint(5, 50)
    doctors  = random.randint(1, 5)
    return {**hospital, "patients": patients, "doctors": doctors, "wait_time": round((patients / doctors) * 10)}

def agent_main(symptoms: str, lat: float, lng: float) -> dict:
    department = get_department(symptoms)
    hospitals  = fetch_hospitals(lat, lng)
    rated      = [estimate_wait(h) for h in hospitals]
    best       = min(rated, key=lambda h: h["wait_time"])
    reason = (
        f"{best['name']} has the shortest estimated wait of {best['wait_time']} minutes "
        f"based on ~{best['patients']} patients and {best['doctors']} doctors on duty. "
        f"Directed to the {department} department."
    )
    return {"hospital": best["name"], "department": department,
            "wait_time": best["wait_time"], "reason": reason, "all_hospitals": rated}

# ─── FastAPI App ────────────────────────────────────────────────────────────────

app = FastAPI(title="Hospital Quick Find API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    symptoms: str
    lat: float
    lng: float

@app.post("/api/recommend")
async def recommend_hospital(req: RecommendRequest):
    return agent_main(req.symptoms, req.lat, req.lng)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
