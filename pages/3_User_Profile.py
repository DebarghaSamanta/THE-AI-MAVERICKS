import streamlit as st
import datetime
import time
from auth_system import check_auth
import pytz
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
# ---- PAGE CONFIG ----
st.set_page_config(page_title="User Profile | Disaster Relief Dashboard", layout="centered")

# ---- AUTH CHECK ----
if not check_auth():
    st.stop()

# Auto-logout after inactivity
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()

# Check if user has been inactive for more than 5 minutes (300 seconds)
if time.time() - st.session_state.last_activity > 300:
    st.session_state.clear()
    st.warning("Your session has expired due to inactivity. Please log in again.")
    st.switch_page("app.py")
else:
    # Update last activity time
    st.session_state.last_activity = time.time()

# ---- LOGOUT ----
if st.sidebar.button("🔒 Logout"):
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.switch_page("app.py")

# ---- BACKGROUND STYLING ----
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #2b2b3c);
        color: #f0f0f0;
        font-family: 'Segoe UI', sans-serif;
    }
    .avatar-circle {
        background-color: #4f4f6c;
        color: white;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0 auto 20px auto;
    }
    .profile-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .user-name {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .user-email {
        color: #ccc;
        font-size: 1.1rem;
    }
    .footer {
        text-align: center;
        font-size: 0.8rem;
        color: #aaa;
        margin-top: 50px;
    }
    .detail-card {
        background-color: #3c3c54;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .detail-label {
        color: #aaa;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }
    .detail-value {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .detail-section {
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .detail-section-title {
        font-size: 1.3rem;
        font-weight: 500;
        margin-bottom: 15px;
        color: #d8d8e6;
    }
    </style>
""", unsafe_allow_html=True)

# Get user information
user = st.session_state.user if 'user' in st.session_state else None
login_time = st.session_state.login_time if 'login_time' in st.session_state else datetime.datetime.now()

# ---- TITLE ----
st.markdown("<h1 style='text-align: center; color: #f0f0f0;'>👤 User Profile</h1>", unsafe_allow_html=True)
st.divider()

# ---- USER PROFILE DISPLAY ----
if user:
    name = user.get("name", "User")
    email = user.get("email", "No email available")
    aadhaar_number = user.get("aadhaar_number", "Not available")
    role = user.get("role", "User")
    created_at = user.get("created_at", "Not available")
    birthday = user.get("birthday", "Not available")
    gender = user.get("gender", "Not specified")
    
    # Format the login time
    indian_timezone = pytz.timezone('Asia/Kolkata')
    login_time_ist = login_time.astimezone(indian_timezone) if login_time.tzinfo else indian_timezone.localize(login_time)
    login_time_str = login_time_ist.strftime("%d %b %Y, %I:%M %p IST")
    
    # Format the account creation time if available
    if isinstance(created_at, datetime.datetime):
        created_at_ist = created_at.astimezone(indian_timezone) if created_at.tzinfo else indian_timezone.localize(created_at)
        created_at_str = created_at_ist.strftime("%d %b %Y, %I:%M %p IST")
    else:
        created_at_str = "Not available"
    
    # Format birthday if it's a string in ISO format
    if isinstance(birthday, str) and birthday != "Not available":
        try:
            birthday_date = datetime.datetime.fromisoformat(birthday).date()
            birthday_str = birthday_date.strftime("%d %b %Y")
        except ValueError:
            birthday_str = birthday
    else:
        birthday_str = str(birthday)
    
    # User's initial for avatar
    initial = name[0].upper()
    
    # Use Streamlit's native components with custom styling
    st.markdown(f"""
    <div class="profile-header">
        <div class="avatar-circle">{initial}</div>
        <div class="user-name">{name}</div>
        <div class="user-email">{email}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Personal Information Section
    st.markdown('<div class="detail-section">', unsafe_allow_html=True)
    st.markdown('<div class="detail-section-title">Personal Information</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">BIRTHDAY</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{birthday_str}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">GENDER</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{gender}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">AADHAAR NUMBER</div>', unsafe_allow_html=True)
        # Display only last 4 digits of Aadhaar for security
        masked_aadhaar = f"XXXX-XXXX-{aadhaar_number[-4:]}" if len(aadhaar_number) >= 4 else "Protected"
        st.markdown(f'<div class="detail-value">{masked_aadhaar}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Account Information Section
    st.markdown('<div class="detail-section">', unsafe_allow_html=True)
    st.markdown('<div class="detail-section-title">Account Information</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">ROLE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{role.capitalize()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">CURRENT LOGIN TIME</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{login_time_str}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="detail-label">ACCOUNT CREATED</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{created_at_str}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if the user has uploaded a government document
    if user.get("govt_document"):
        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
        st.markdown('<div class="detail-section-title">Verification Documents</div>', unsafe_allow_html=True)
        
        doc = user.get("govt_document", {})
        doc_name = doc.get("filename", "No document uploaded")
        doc_type = doc.get("content_type", "Unknown type")
        doc_size = doc.get("size", 0)
        doc_size_mb = doc_size / (1024 * 1024) if doc_size else 0
        
        with st.container():
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)
            st.markdown('<div class="detail-label">UPLOADED DOCUMENT</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-value">{doc_name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-value" style="font-size: 0.9rem; color: #aaa;">({doc_type}, {doc_size_mb:.2f} MB)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("◀ Back to Dashboard", use_container_width=True):
        st.switch_page("app.py")
else:
    st.error("⚠ User information not available. Please log in again.")
    st.button("◀ Back to Login", on_click=lambda: st.switch_page("app.py"))

# ---- FOOTER ----
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Disaster Relief AI — Empowering smarter crisis response</div>", unsafe_allow_html=True)

# JavaScript for detecting tab close/inactivity
st.markdown("""
<script>
// Set a variable in sessionStorage when page loads
sessionStorage.setItem('pageActive', 'true');

// Listen for before unload event (tab close or navigate away)
window.addEventListener('beforeunload', function() {
    sessionStorage.setItem('pageActive', 'false');
    
    // Save the logout time
    localStorage.setItem('logoutTime', Date.now());
});

// Function to check if user is inactive
let inactivityTimer;
function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(function() {
        // Save the logout time due to inactivity
        localStorage.setItem('logoutTime', Date.now());
        // Force reload to trigger rerun
        window.location.reload();
    }, 300000); // 5 minutes in milliseconds
}

// Reset timer on user activity
['click', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, resetInactivityTimer, true);
});

// Initialize the timer
resetInactivityTimer();
</script>
""", unsafe_allow_html=True)