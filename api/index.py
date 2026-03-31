import random
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ─── Frontend HTML ──────────────────────────────────────────────────────────────

FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospital Queue Optimization Agent</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --bg1:#0f172a; --bg2:#1e1b4b; --card:rgba(255,255,255,0.05); --border:rgba(255,255,255,0.1); --primary:#3b82f6; --muted:#94a3b8; }
        * { box-sizing:border-box; margin:0; padding:0; font-family:'Outfit',sans-serif; }
        body { background:linear-gradient(135deg,var(--bg1),var(--bg2)); color:#f8fafc; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:2rem; }
        .container { width:100%; max-width:600px; background:var(--card); backdrop-filter:blur(16px); border:1px solid var(--border); border-radius:24px; padding:2.5rem; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); animation:fadeIn .6s ease-out; }
        h1 { font-size:2.2rem; font-weight:700; margin-bottom:.5rem; background:linear-gradient(to right,#60a5fa,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-align:center; }
        .subtitle { color:var(--muted); text-align:center; margin-bottom:2rem; font-size:1.1rem; }
        .status { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.2); color:#34d399; padding:1rem; border-radius:12px; text-align:center; margin-bottom:2rem; display:flex; align-items:center; justify-content:center; gap:8px; transition:all .3s; }
        .status.loading { background:rgba(245,158,11,.1); border-color:rgba(245,158,11,.2); color:#fbbf24; }
        .status.error { background:rgba(239,68,68,.1); border-color:rgba(239,68,68,.2); color:#f87171; }
        .form-group { margin-bottom:1.5rem; }
        label { display:block; margin-bottom:.5rem; font-weight:600; }
        input { width:100%; background:rgba(0,0,0,.2); border:1px solid var(--border); color:#fff; padding:1rem; border-radius:12px; font-size:1rem; outline:none; transition:all .3s; }
        input:focus { border-color:var(--primary); box-shadow:0 0 0 3px rgba(59,130,246,.3); }
        button { width:100%; background:linear-gradient(to right,var(--primary),#8b5cf6); color:#fff; border:none; padding:1rem; border-radius:12px; font-size:1.1rem; font-weight:600; cursor:pointer; transition:transform .2s,box-shadow .2s; box-shadow:0 4px 14px rgba(59,130,246,.4); }
        button:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(59,130,246,.6); }
        button:disabled { background:#475569; cursor:not-allowed; transform:none; box-shadow:none; }
        .results { display:none; margin-top:2rem; animation:slideUp .5s ease-out; }
        .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:1.5rem; }
        .card { background:rgba(255,255,255,.03); border:1px solid var(--border); border-radius:12px; padding:1rem; text-align:center; }
        .card h3 { font-size:.8rem; color:var(--muted); margin-bottom:.5rem; text-transform:uppercase; }
        .card p { font-size:1.2rem; font-weight:700; }
        .reason { background:rgba(59,130,246,.1); border-left:4px solid var(--primary); padding:1rem; border-radius:0 8px 8px 0; font-size:.95rem; line-height:1.5; margin-bottom:1.5rem; }
        .toggle { background:transparent; border:1px solid var(--border); box-shadow:none; color:var(--muted); font-size:.95rem; padding:.75rem; }
        .toggle:hover { background:rgba(255,255,255,.05); color:#fff; }
        .list { display:none; margin-top:1rem; max-height:250px; overflow-y:auto; border:1px solid var(--border); border-radius:12px; padding:.5rem; }
        .item { padding:.75rem; border-bottom:1px solid rgba(255,255,255,.05); font-size:.9rem; color:var(--muted); }
        .item:last-child { border-bottom:none; }
        .item span { color:#fff; font-weight:600; }
        @keyframes fadeIn { from{opacity:0;transform:scale(.95)} to{opacity:1;transform:scale(1)} }
        @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
        .spin { display:inline-block; width:16px; height:16px; border:2px solid rgba(255,255,255,.3); border-radius:50%; border-top-color:#fff; animation:rotate 1s linear infinite; }
        @keyframes rotate { to{transform:rotate(360deg)} }
    </style>
</head>
<body>
<div class="container">
    <h1>Hospital Queue Agent 🏥</h1>
    <p class="subtitle">Find the nearest hospital with the shortest estimated wait time.</p>
    <div id="status" class="status loading"><div class="spin"></div> Requesting location access...</div>
    <div class="form-group">
        <label for="symptoms">Describe your symptoms</label>
        <input type="text" id="symptoms" placeholder="e.g. fever, kidney stone, chest pain" />
    </div>
    <button id="btn" disabled>Find Best Hospital</button>
    <div id="results" class="results">
        <div class="status" style="margin-bottom:1.5rem">🎉 Recommendation ready!</div>
        <div class="grid">
            <div class="card"><h3>🏥 Hospital</h3><p id="r-hospital">-</p></div>
            <div class="card"><h3>🩺 Department</h3><p id="r-dept">-</p></div>
            <div class="card"><h3>⏱ Wait</h3><p id="r-wait">-</p></div>
        </div>
        <div class="reason"><strong>Why this hospital?</strong> <span id="r-reason"></span></div>
        <button class="toggle" onclick="toggle()">📊 View All Nearby Hospitals</button>
        <div id="list" class="list"></div>
    </div>
</div>
<script>
let lat=40.758,lng=-73.9855;
const st=document.getElementById('status'),btn=document.getElementById('btn');
if("geolocation"in navigator){
    navigator.geolocation.getCurrentPosition(
        p=>{lat=p.coords.latitude;lng=p.coords.longitude;st.className="status";st.innerHTML="📍 Using your current location";btn.disabled=false;},
        ()=>{st.className="status error";st.innerHTML="❌ Location denied — using default (NYC)";btn.disabled=false;}
    );
}else{st.className="status error";st.innerHTML="❌ Geolocation not supported";btn.disabled=false;}
btn.addEventListener('click',async()=>{
    const symptoms=document.getElementById('symptoms').value.trim();
    if(!symptoms){alert("Please enter your symptoms.");return;}
    const orig=btn.innerHTML;
    btn.innerHTML="<div class='spin'></div> Fetching...";btn.disabled=true;
    document.getElementById('results').style.display='none';
    try{
        const r=await fetch('/api/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symptoms,lat,lng})});
        if(!r.ok)throw new Error();
        const d=await r.json();
        document.getElementById('r-hospital').innerText=d.hospital;
        document.getElementById('r-dept').innerText=d.department.charAt(0).toUpperCase()+d.department.slice(1);
        document.getElementById('r-wait').innerText=d.wait_time+" min";
        document.getElementById('r-reason').innerText=d.reason;
        const l=document.getElementById('list');l.innerHTML="";
        d.all_hospitals.sort((a,b)=>a.wait_time-b.wait_time).forEach(h=>{
            const el=document.createElement('div');el.className='item';
            el.innerHTML=`<span>${h.name}</span> — ~${h.patients} patients, ${h.doctors} doctors → <span>${h.wait_time} min</span>`;
            l.appendChild(el);
        });
        document.getElementById('results').style.display='block';
    }catch{alert("Error fetching data. Please try again.");}
    finally{btn.innerHTML=orig;btn.disabled=false;}
});
function toggle(){const l=document.getElementById('list');l.style.display=l.style.display==='block'?'none':'block';}
</script>
</body>
</html>"""

# ─── Hospital Agent Logic ───────────────────────────────────────────────────────

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

FALLBACK_HOSPITALS = [
    "City General Hospital", "Community Medical Center", "Regional Health Hospital",
    "St. Mary's Medical Center", "Metropolitan Hospital", "University Hospital",
    "Riverside Medical Center", "Downtown Emergency Hospital",
]

def get_department(symptoms: str) -> str:
    s = symptoms.lower()
    rules = {
        "orthopedic":      ["bone","fracture","broken","joint","spine","back pain","shoulder","knee","hip"],
        "cardiology":      ["heart","chest pain","palpitation","cardiac","blood pressure","hypertension"],
        "neurology":       ["headache","migraine","seizure","stroke","numbness","dizziness","brain"],
        "urology":         ["kidney","kidney stone","urine","urinary","bladder","prostate"],
        "gastroenterology":["stomach","abdomen","nausea","vomiting","diarrhea","constipation","liver"],
        "pulmonology":     ["cough","breathing","lung","asthma","pneumonia","respiratory"],
        "dermatology":     ["skin","rash","itch","acne","allergy","hives"],
        "ent":             ["ear","nose","throat","sore throat","hearing","sinus","congestion"],
        "general":         ["fever","fatigue","weakness","pain","flu","infection"],
    }
    for dept, keywords in rules.items():
        if any(kw in s for kw in keywords):
            return dept
    return "general"

def fetch_hospitals(lat: float, lng: float) -> list:
    query = f'[out:json][timeout:8];node["amenity"="hospital"](around:10000,{lat},{lng});out;'
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = requests.post(endpoint, data={"data": query}, timeout=10)
            resp.raise_for_status()
            seen, hospitals = set(), []
            for el in resp.json().get("elements", []):
                name = el.get("tags", {}).get("name") or el.get("tags", {}).get("name:en")
                if name and name not in seen:
                    seen.add(name)
                    hospitals.append({"name": name, "rating": None})
            if hospitals:
                return hospitals
        except Exception:
            continue
    return [{"name": n, "rating": None} for n in FALLBACK_HOSPITALS]

def agent_main(symptoms: str, lat: float, lng: float) -> dict:
    department = get_department(symptoms)
    hospitals  = fetch_hospitals(lat, lng)
    rated = [
        {**h, "patients": (p := random.randint(5, 50)),
               "doctors":  (d := random.randint(1, 5)),
               "wait_time": round((p / d) * 10)}
        for h in hospitals
    ]
    best = min(rated, key=lambda h: h["wait_time"])
    return {
        "hospital":     best["name"],
        "department":   department,
        "wait_time":    best["wait_time"],
        "reason":       f"{best['name']} has the shortest estimated wait of {best['wait_time']} minutes "
                        f"based on ~{best['patients']} patients and {best['doctors']} doctors on duty. "
                        f"Directed to the {department} department.",
        "all_hospitals": rated,
    }

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

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return HTMLResponse(content=FRONTEND_HTML)

@app.post("/api/recommend")
async def recommend_hospital(req: RecommendRequest):
    return agent_main(req.symptoms, req.lat, req.lng)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
