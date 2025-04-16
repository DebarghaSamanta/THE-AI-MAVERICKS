import streamlit as st
from PIL import Image
import base64
import streamlit_lottie as st_lottie
import requests
import datetime
from dotenv import load_dotenv
import os
from auth_system import check_auth

# ---- LOAD ENV VARIABLES ----
load_dotenv()
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Disaster Relief Dashboard", layout="centered")

# ---- AUTH CHECK ----
# Move auth check to the beginning before any other content
is_authenticated = check_auth()
if not is_authenticated:
    st.stop()  # Stop execution if not authenticated

# Track login time if not already set
if 'login_time' not in st.session_state:
    st.session_state.login_time = datetime.datetime.now()

# ---- HIDE SIDEBAR PAGE NAVIGATION ----
# This will hide the default sidebar page navigation
st.markdown("""
    <style>
    .css-1d391kg {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# ---- LOGOUT ----
if st.sidebar.button("🔒 Logout"):
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.rerun()

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
        st.warning("⚠ Logo image not found. Please ensure the path is correct.")

# ---- BACKGROUND STYLING ----
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #2b2b3c);
        color: #f0f0f0;
        font-family: 'Segoe UI', sans-serif;
    }
    .title-container {
        text-align: center;
        margin-bottom: 10px;
        color: #f0f0f0;
    }
    .section-card {
        background-color: #2f2f40;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        color: #ffffff;
    }
    .footer {
        text-align: center;
        font-size: 0.8rem;
        color: #aaa;
        margin-top: 50px;
    }
    .stButton>button {
        background-color: #3c3c54;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #4f4f6c;
        color: #ffffff;
    }
    .user-avatar {
        border-radius: 50%;
        width: 40px;
        height: 40px;
        object-fit: cover;
        cursor: pointer;
    }
    .user-info-container {
        position: absolute;
        top: 10px;
        left: 20px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 8px;
        background-color: rgba(47, 47, 64, 0.8);
        padding: 5px 10px;
        border-radius: 20px;
        cursor: pointer;
    }
    .user-name {
        color: white;
        font-size: 14px;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Display user avatar and name in top left
if 'user' in st.session_state:
    user_name = st.session_state.user.get("name", "User")
    user_initial = user_name[0].upper()
    
    # Create user profile button
    st.markdown(f"""
        <div class="user-info-container" onclick="parent.window.location.href='pages/3_User_Profile.py'">
            <div style="background-color: #4f4f6c; color: white; border-radius: 50%; width: 40px; height: 40px; 
                  display: flex; align-items: center; justify-content: center; font-weight: bold;">
                {user_initial}
            </div>
            <p class="user-name">{user_name}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    st.sidebar.success(f"Welcome, {user_name}!")
    
    # ---- CUSTOM SIDEBAR NAVIGATION ----
    # Only show page navigation if authenticated
    st.sidebar.markdown("### Navigation")
    if st.sidebar.button("📦 Supply Prediction"):
        st.switch_page("pages/1_Supply_Prediction.py")
    
    if st.sidebar.button("🗺 Route Planner"):
        st.switch_page("pages/2_Route_Planner.py")
    
    if st.sidebar.button("👤 User Profile"):
        st.switch_page("pages/3_User_Profile.py")

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
        st.markdown("""
            #### 📦 Predict Supplies  
            Estimate critical supplies needed for affected populations.
        """, unsafe_allow_html=True)
        if st.button("Start Prediction", use_container_width=True):
            st.switch_page("pages/1_Supply_Prediction.py")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("""
            #### 🗺 Plan Delivery Route  
            Find optimal supply delivery paths based on disaster zones.
        """, unsafe_allow_html=True)
        if st.button("Start Route Planning", use_container_width=True):
            st.switch_page("pages/2_Route_Planner.py")
        st.markdown("</div>", unsafe_allow_html=True)

# ---- TIP ----
st.divider()
if 'user' in st.session_state:
    st.info("💡 Tip: You can also navigate using the sidebar.")

# ---- FETCH DISASTER NEWS FUNCTION ----
def fetch_disaster_news(from_date, to_date, max_articles=5):
    if not MEDIASTACK_API_KEY:
        st.error("⚠ Mediastack API key not found. Please check your .env file.")
        return []

    keywords = (
        "disaster,flood,earthquake,cyclone,landslide,drought,tsunami,storm,"
        "monsoon,deluge,uttarakhand,assam,bihar,kerala,odisha,manipur,jammu"
    )

    url = (
        f"http://api.mediastack.com/v1/news?"
        f"access_key={MEDIASTACK_API_KEY}&"
        f"languages=en&"
        f"countries=in&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"sort=published_desc&"
        f"limit={max_articles}&"
        f"keywords={keywords}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        st.error(f"⚠ Failed to fetch disaster news from Mediastack. Status code: {response.status_code}")
        return []

# ---- ALERT: DISASTER NEWS ----
st.markdown("### 🔔 Alert: Disaster News in India")

today = datetime.date.today()
one_month_ago = today - datetime.timedelta(days=30)

st.markdown("#### 🔴 Latest News (Today)")
latest_news = fetch_disaster_news(today, today)
if latest_news:
    for article in latest_news:
        st.markdown(f"**[{article['title']}]({article['url']})**  \n:small_blue_diamond: {article['description']}")
else:
    st.info("No recent disaster-related news for today.")

st.divider()

st.markdown("#### 🟡 News from the Past Month")
older_news = fetch_disaster_news(one_month_ago, today)
if older_news:
    for article in older_news:
        st.markdown(f"**[{article['title']}]({article['url']})**  \n:small_blue_diamond: {article['description']}")
else:
    st.info("No disaster-related news found in the past month.")

# ---- FOOTER ----
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Disaster Relief AI — Empowering smarter crisis response</div>", unsafe_allow_html=True)