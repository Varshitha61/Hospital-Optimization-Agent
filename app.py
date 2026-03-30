import streamlit as st
from hospital_agent import main, DEFAULT_LAT, DEFAULT_LNG

st.set_page_config(page_title="Hospital Queue Agent", page_icon="🏥", layout="centered")

st.title("🏥 Hospital Queue Optimization Agent")
st.caption("Find the nearest hospital with the shortest estimated wait time.")

st.divider()

with st.form("symptom_form"):
    symptoms = st.text_input(
        "Describe your symptoms",
        placeholder="e.g. I have a fever, or broken bone",
    )
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
    with col2:
        lng = st.number_input("Longitude", value=DEFAULT_LNG, format="%.4f")

    submitted = st.form_submit_button("Find Best Hospital", type="primary", use_container_width=True)

if submitted:
    if not symptoms.strip():
        st.warning("Please enter your symptoms.")
    else:
        with st.spinner("Fetching nearby hospitals and estimating wait times..."):
            try:
                result = main(symptoms.strip(), lat, lng)
            except Exception as e:
                st.error(f"Error contacting Google Maps API: {e}")
                st.stop()

        st.success("Recommendation ready!")

        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 Hospital", result["hospital"])
        col2.metric("🩺 Department", result["department"].capitalize())
        col3.metric("⏱ Wait Time", f"{result['wait_time']} min" if result["wait_time"] is not None else "N/A")

        st.info(f"**Why this hospital?** {result['reason']}")

        if result.get("all_hospitals"):
            with st.expander("📊 All nearby hospitals (sorted by wait time)"):
                sorted_hospitals = sorted(result["all_hospitals"], key=lambda h: h["wait_time"])
                for h in sorted_hospitals:
                    rating = f"⭐ {h['rating']}" if h.get("rating") else "No rating"
                    st.write(
                        f"**{h['name']}** — {rating} | "
                        f"~{h['patients']} patients, {h['doctors']} doctors → "
                        f"**{h['wait_time']} min wait**"
                    )
