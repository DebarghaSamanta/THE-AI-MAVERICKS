import streamlit as st
from PIL import Image
import base64
import streamlit_lottie as st_lottie
import requests

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Disaster Relief Dashboard", layout="centered")

# ---- LOAD LOTTIE ANIMATION ----
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

relief_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_twijbubv.json")

# ---- LOGO DISPLAY ----
def display_centered_logo(image_path, width=120):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <div style='text-align: center; padding: 10px;'>
                <img src='data:image/png;base64,{encoded_image}' width='{width}'/>
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("⚠️ Logo image not found. Please ensure the path is correct.")

# ---- BACKGROUND GRADIENT ----
st.markdown("""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #f7f9fc, #e4ebf5);
        font-family: 'Segoe UI', sans-serif;
    }}
    .title-container {{
        text-align: center;
        margin-bottom: 10px;
    }}
    .section-card {{
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }}
    .footer {{
        text-align: center;
        font-size: 0.8rem;
        color: #888;
        margin-top: 50px;
    }}
    </style>
""", unsafe_allow_html=True)

# ---- DISPLAY LOGO ----
display_centered_logo("E:/Supply Prediction and Route Data/images/image.png")

# ---- TITLE SECTION ----
st.markdown("<div class='title-container'><h1>🆘 AI-Based Disaster Relief Dashboard</h1><h4>An AI + Maps powered tool for fast, informed disaster response.</h4></div>", unsafe_allow_html=True)
st.divider()

# ---- RELIEF ANIMATION ----
with st.container():
    st_lottie.st_lottie(relief_animation, height=250, key="relief")

# ---- TOOL NAVIGATION ----
st.markdown("### 🚀 Choose a Tool to Begin")
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 📦 Predict Supplies")
        st.markdown("Estimate critical supplies needed for affected populations.")
        if st.button("Start Prediction", use_container_width=True):
            st.switch_page("pages/1_Supply_Prediction.py")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 🗺️ Plan Delivery Route")
        st.markdown("Find optimal supply delivery paths based on disaster zones.")
        if st.button("Start Route Planning", use_container_width=True):
            st.switch_page("pages/2_Route_Planner.py")
        st.markdown("</div>", unsafe_allow_html=True)

# ---- SIDEBAR TIP ----
st.divider()
st.info("💡 Tip: You can also navigate using the sidebar.")

# ---- FOOTER ----
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Disaster Relief AI — Empowering smarter crisis response</div>", unsafe_allow_html=True)
