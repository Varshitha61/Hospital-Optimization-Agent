import streamlit as st
from streamlit_js_eval import get_geolocation
from hospital_agent import main

st.set_page_config(page_title="Hospital Queue Agent", page_icon="🏥", layout="centered")

st.title("🏥 Hospital Queue Optimization Agent")
st.caption("Find the nearest hospital with the shortest estimated wait time.")

st.divider()

# Get browser geolocation
location = get_geolocation()

if location is None:
    st.info("📍 Requesting your location... Please allow location access when prompted by your browser.")
    st.stop()

lat = location["coords"]["latitude"]
lng = location["coords"]["longitude"]

st.caption("📍 Using your current location")

with st.form("symptom_form"):
    symptoms = st.text_input(
        "Describe your symptoms",
        placeholder="e.g. I have a fever, kidney stone, chest pain",
    )
    submitted = st.form_submit_button("Find Best Hospital", type="primary", use_container_width=True)

if submitted:
    if not symptoms.strip():
        st.warning("Please enter your symptoms.")
    else:
        with st.spinner("Fetching nearby hospitals and estimating wait times..."):
            result = main(symptoms.strip(), lat, lng)

        st.success("Recommendation ready!")

        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 Hospital", result["hospital"])
        col2.metric("🩺 Department", result["department"].capitalize())
        col3.metric("⏱ Wait Time", f"{result['wait_time']} min")

        st.info(f"**Why this hospital?** {result['reason']}")

        if result.get("all_hospitals"):
            with st.expander("📊 All nearby hospitals (sorted by wait time)"):
                sorted_hospitals = sorted(result["all_hospitals"], key=lambda h: h["wait_time"])
                for h in sorted_hospitals:
                    rating = f"⭐ {h['rating']}" if h.get("rating") else ""
                    st.write(
                        f"**{h['name']}** {rating} — "
                        f"~{h['patients']} patients, {h['doctors']} doctors → "
                        f"**{h['wait_time']} min wait**"
                    )
