import streamlit as st
import requests
import urllib.parse
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os

# ---------------- LOAD ENV VARS ----------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------------- Suggestion API ----------------
def get_place_suggestions(input_text):
    if not input_text:
        return []
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "key": GOOGLE_API_KEY,
        "types": "geocode",
        "components": "country:in",
    }
    response = requests.get(url, params=params)
    predictions = response.json().get("predictions", [])
    return [p["description"] for p in predictions]

# ---------------- Geocoding ----------------
def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            return f"{location['lat']},{location['lng']}"
    return None

# ---------------- Route Info ----------------
def get_route_info(origin, destination, waypoints, mode):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_API_KEY,
        "alternatives": "true"
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    response = requests.get(url, params=params)
    data = response.json()
    if data["status"] == "OK":
        leg = data["routes"][0]["legs"][0]
        return leg["distance"]["text"], leg["duration"]["text"]
    return None, None

# ---------------- Page Config ----------------
st.set_page_config(layout="wide")
st.title("🚗 Google Maps Style Route Planner")

# ---------------- Layout ----------------
left, right = st.columns([1, 2])

with left:
    st.subheader("📍 Enter Route Info")

    # SOURCE INPUT
    src_input = st.text_input("Start Location")
    src_suggestions = get_place_suggestions(src_input)
    src_selected = st.selectbox("Select Start Location", src_suggestions, key="src") if src_suggestions else src_input

    # DESTINATION INPUT
    dest_input = st.text_input("End Location")
    dest_suggestions = get_place_suggestions(dest_input)
    dest_selected = st.selectbox("Select End Location", dest_suggestions, key="dest") if dest_suggestions else dest_input

    # VIA POINTS
    via_points_input = st.text_area("Via Points (comma-separated)", placeholder="E.g. Durgapur, Asansol")
    via_points = [v.strip() for v in via_points_input.split(",") if v.strip()]

    # MODE
    mode = st.selectbox("Travel Mode", ["driving", "walking", "bicycling", "transit"])

    # Button
    show = st.button("🚀 Show Route")

with right:
    if show and src_selected and dest_selected:
        origin_coords = geocode_address(src_selected)
        dest_coords = geocode_address(dest_selected)
        waypoint_coords = [geocode_address(wp) for wp in via_points if wp]

        if not origin_coords or not dest_coords:
            st.error("❌ Could not geocode start or destination location.")
        else:
            # Optional: Get distance and time
            dist, time = get_route_info(origin_coords, dest_coords, waypoint_coords, mode)

            # Embed map
            map_url = f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_API_KEY}"
            map_url += f"&origin={urllib.parse.quote(origin_coords)}"
            map_url += f"&destination={urllib.parse.quote(dest_coords)}"
            map_url += f"&mode={mode}"
            if waypoint_coords:
                map_url += f"&waypoints={'|'.join(map(str, waypoint_coords))}"

            components.html(
                f"""
                <iframe
                    width="100%"
                    height="600"
                    frameborder="0"
                    style="border:0"
                    src="{map_url}"
                    allowfullscreen>
                </iframe>
                """,
                height=600,
            )
