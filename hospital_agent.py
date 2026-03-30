import os
import random
import requests


DEFAULT_LAT = 40.7580
DEFAULT_LNG = -73.9855
DEFAULT_RADIUS = 10000  # meters (10km)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_department(symptoms: str) -> str:
    """Map symptoms string to a hospital department."""
    symptoms_lower = symptoms.lower()

    department_map = {
        "orthopedic": ["bone", "fracture", "broken", "orthopedic", "joint", "spine", "back pain", "shoulder", "knee", "hip"],
        "cardiology": ["heart", "chest pain", "palpitation", "cardiac", "blood pressure", "hypertension", "shortness of breath"],
        "neurology": ["headache", "migraine", "seizure", "stroke", "numbness", "dizziness", "brain", "nerve"],
        "urology": ["kidney", "kidney stone", "urine", "urinary", "bladder", "prostate", "burning urination"],
        "gastroenterology": ["stomach", "abdomen", "nausea", "vomiting", "diarrhea", "constipation", "liver", "ulcer"],
        "pulmonology": ["cough", "breathing", "lung", "asthma", "pneumonia", "respiratory"],
        "dermatology": ["skin", "rash", "itch", "acne", "allergy", "hives"],
        "ent": ["ear", "nose", "throat", "sore throat", "hearing", "sinus", "cold", "congestion"],
        "general": ["fever", "fatigue", "weakness", "pain", "cold", "flu", "infection"],
    }

    for department, keywords in department_map.items():
        if any(kw in symptoms_lower for kw in keywords):
            return department

    return "general"


def fetch_hospitals(lat: float = DEFAULT_LAT, lng: float = DEFAULT_LNG, radius: int = DEFAULT_RADIUS) -> list[dict]:
    """Fetch nearby hospitals using the OpenStreetMap Overpass API (free, no key needed)."""
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lng});
      way["amenity"="hospital"](around:{radius},{lat},{lng});
      relation["amenity"="hospital"](around:{radius},{lat},{lng});
    );
    out center;
    """
    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=20)
    response.raise_for_status()
    data = response.json()

    hospitals = []
    seen = set()
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        if not name or name in seen:
            continue
        seen.add(name)
        hospitals.append({
            "name": name,
            "rating": None,
        })

    return hospitals


def estimate_wait(hospital: dict) -> dict:
    """Simulate patients/doctors and estimate wait time for a hospital."""
    patients = random.randint(5, 50)
    doctors = random.randint(1, 5)
    wait_time = round((patients / doctors) * 10)
    return {
        **hospital,
        "patients": patients,
        "doctors": doctors,
        "wait_time": wait_time,
    }


def select_best_hospital(hospitals_with_wait: list[dict]) -> dict:
    """Select the hospital with the minimum estimated wait time."""
    return min(hospitals_with_wait, key=lambda h: h["wait_time"])


def main(symptoms: str, lat: float = DEFAULT_LAT, lng: float = DEFAULT_LNG) -> dict:
    """
    Main agent function: given symptoms and a location, recommend the best nearby hospital.
    """
    department = get_department(symptoms)
    hospitals = fetch_hospitals(lat, lng)

    if not hospitals:
        return {
            "hospital": "No hospitals found",
            "department": department,
            "wait_time": None,
            "reason": "No hospitals were found within 10km of your location.",
        }

    hospitals_with_wait = [estimate_wait(h) for h in hospitals]
    best = select_best_hospital(hospitals_with_wait)

    reason = (
        f"{best['name']} has the shortest estimated wait of {best['wait_time']} minutes "
        f"based on ~{best['patients']} patients and {best['doctors']} doctors on duty. "
        f"Directed to the {department} department."
    )

    return {
        "hospital": best["name"],
        "department": department,
        "wait_time": best["wait_time"],
        "reason": reason,
        "all_hospitals": hospitals_with_wait,
    }


if __name__ == "__main__":
    symptoms = input("Enter your symptoms: ").strip()
    result = main(symptoms)
    print("\n--- Recommendation ---")
    print(f"Hospital   : {result['hospital']}")
    print(f"Department : {result['department']}")
    print(f"Wait Time  : {result['wait_time']} minutes")
    print(f"Reason     : {result['reason']}")
