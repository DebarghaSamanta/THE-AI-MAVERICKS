import streamlit as st
from PIL import Image
import base64
import streamlit_lottie as st_lottie
import requests
import datetime
from dotenv import load_dotenv
import os

# ---- LOAD ENV VARIABLES ----
load_dotenv()
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")

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

# ---- BACKGROUND STYLING ----
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

# ---- TITLE ----
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

# ---- FETCH DISASTER NEWS FUNCTION USING MEDIASTACK API ----
def fetch_disaster_news(from_date, to_date, max_articles=5):
    if not MEDIASTACK_API_KEY:
        st.error("⚠️ Mediastack API key not found. Please check your .env file.")
        return []

    # Define Indian news sources to filter by (Examples: 'times-of-india', 'india-today', 'ndtv', 'news24', 'hindustan-times')
    indian_sources = "times-of-india,india-today,ndtv,news24,hindustan-times"

    # Construct the Mediastack API URL with filters
    url = (
        f"http://api.mediastack.com/v1/news?"
        f"access_key={MEDIASTACK_API_KEY}&"
        f"languages=en&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"sort=published_desc&"
        f"limit={max_articles}&"
        f"keywords=disaster,flood,earthquake,cyclone,landslide,drought&"
        f"sources={indian_sources}"
    )

    # Send request to Mediastack API
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        st.error(f"⚠️ Failed to fetch disaster news from Mediastack. Status code: {response.status_code}")
        return []

# ---- ALERT: DISASTER NEWS ----
st.markdown("### 🔔 Alert: Disaster News in India")

today = datetime.date.today()
one_week_ago = today - datetime.timedelta(days=7)

# Today's news
st.markdown("#### 🔴 Latest News (Today)")
latest_news = fetch_disaster_news(today, today)
if latest_news:
    for article in latest_news:
        st.markdown(f"**[{article['title']}]({article['url']})**  \n:small_blue_diamond: {article['description']}")
else:
    st.info("No recent disaster-related news for today.")

st.divider()

# Older news
st.markdown("#### 🟡 News from the Past Week")
older_news = fetch_disaster_news(one_week_ago, today)
if older_news:
    for article in older_news:
        st.markdown(f"**[{article['title']}]({article['url']})**  \n:small_blue_diamond: {article['description']}")
else:
    st.info("No older disaster-related news found.")

# ---- FOOTER ----
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Disaster Relief AI — Empowering smarter crisis response</div>", unsafe_allow_html=True)
