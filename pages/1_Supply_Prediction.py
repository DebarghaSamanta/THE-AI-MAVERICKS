import streamlit as st
import pandas as pd
import pickle
import time

from auth_system import check_auth

# Force authentication check before rendering anything
is_authenticated = check_auth()

# If not authenticated, show login message and stop the page from loading
if not is_authenticated:
    st.error("🔒 Authentication required! Please log in to access this page.")
    st.info("Redirecting to login page...")
    
    # Optional: Add JavaScript to automatically redirect after a short delay
    st.markdown(
        """
        <script>
            setTimeout(function() {
                window.location.href = '/';
            }, 2000);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.stop()  # Stop rendering the rest of the page

# Continue with page content only if authenticated
# Rest of the page code goes here...
# Page config
st.set_page_config(page_title="Disaster Supply Predictor", layout="centered")

# Load trained models and their feature columns
with open("food_water_model.pkl", "rb") as f:
    food_water_model, food_water_features = pickle.load(f)

with open("supply_model.pkl", "rb") as f:
    supply_model, supply_features = pickle.load(f)

# App Title
st.title("🌪️ AI-Powered Disaster Supply Predictor")
st.markdown("Estimate emergency **food, water, medicine**, and **clothing** needs based on disaster impact details.")

st.divider()

# Collect user input in 2 columns
col1, col2 = st.columns(2)

with col1:
    severity = st.slider("Disaster Severity (1-5)", 1, 5, 3)
    area_size = st.number_input("Affected Area Size (sq km)", min_value=0.0, value=50.0)
    gender_ratio = st.number_input("Gender Ratio (Male:Female → Enter 1.2 for 1:1.2)", min_value=0.1, value=1.0)
    duration = st.number_input("Disaster Duration (in days)", min_value=1, value=7)
    disaster_type = st.selectbox("Disaster Type", ["Flood", "Storm", "Earthquake", "Drought"])

with col2:
    age_0_12 = st.number_input("Children (0-12 yrs)", min_value=0, value=100)
    age_12_60 = st.number_input("Adults (12-60 yrs)", min_value=0, value=300)
    age_60_plus = st.number_input("Elderly (60+ yrs)", min_value=0, value=50)

# Compute derived values
population_affected = age_0_12 + age_12_60 + age_60_plus
females = int((gender_ratio / (1 + gender_ratio)) * population_affected)

# Build DataFrame
input_df = pd.DataFrame({
    "Severity": [severity],
    "Area Size (sq km)": [area_size],
    "Population Affected": [population_affected],
    "Duration (days)": [duration],
    "Age 0-12": [age_0_12],
    "Age 12-60": [age_12_60],
    "Age 60+": [age_60_plus],
    "Females": [females]
})

# One-hot encode disaster type
for dtype in ["Flood", "Storm", "Earthquake", "Drought"]:
    input_df[f"Disaster Type_{dtype}"] = [1 if dtype == disaster_type else 0]

# Reindex input
food_water_input = input_df.reindex(columns=food_water_features, fill_value=0)
supply_input = input_df.reindex(columns=supply_features, fill_value=0)

# Predict Button
if st.button("🚚 Predict Supplies Needed"):
    with st.spinner("🔍 Analyzing disaster impact and calculating resources..."):
        time.sleep(2)  # Simulate processing
        predicted_food_water = food_water_model.predict(food_water_input)[0] * duration
        predicted_supply = supply_model.predict(supply_input)[0] * duration

    st.success("✅ Prediction Complete!")
    st.divider()

    # Display results in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥗 Food & Water Supply")
        st.metric("Rice (kg)", f"{predicted_food_water[0]:.2f}")
        st.metric("Vegetables (kg)", f"{predicted_food_water[1]:.2f}")
        st.metric("Dry Food (kg)", f"{predicted_food_water[2]:.2f}")
        st.metric("Water (liters)", f"{predicted_food_water[3]:.2f}")

    with col2:
        st.subheader("🩺 Medicine & Clothing")
        st.metric("Baby Food (kg)", f"{predicted_supply[0]:.2f}")
        st.metric("Elder Medicine (units)", f"{predicted_supply[1]:.2f}")
        st.metric("Sanitary Items (units)", f"{predicted_supply[2]:.2f}")
        st.metric("Clothing Sets", f"{predicted_supply[3]:.2f}")

    st.divider()
    st.info("📊 Based on your inputs, these are the **estimated needs per disaster duration**.")

