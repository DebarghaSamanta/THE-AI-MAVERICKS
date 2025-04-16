import streamlit as st
import os
import hashlib
import smtplib
import random
import string
import pymongo
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")

# Debug check for environment variables
def check_env_vars():
    missing_vars = []
    if not EMAIL_ADDRESS:
        missing_vars.append("EMAIL_ADDRESS")
    if not EMAIL_PASSWORD:
        missing_vars.append("EMAIL_PASSWORD")
    if not MONGO_URI:
        missing_vars.append("MONGO_URI")
    
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

# MongoDB setup
def get_db_connection():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["disaster_relief_db"]
        return db
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database collections
def init_db():
    db = get_db_connection()
    if db is not None:
        # Create users collection if it doesn't exist
        if "users" not in db.list_collection_names():
            users = db["users"]
            users.create_index("email", unique=True)
            users.create_index("aadhaar_number", unique=True)
        return db
    return None

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Validate Aadhaar number (basic validation)
def validate_aadhaar(aadhaar):
    # Basic validation: 12 digits
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return False
    return True

# Validate document file
def validate_document(uploaded_file):
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Get file size in MB
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    # Check file size (limit to 5MB)
    if file_size_mb > 5:
        return False, f"File size too large: {file_size_mb:.2f}MB. Maximum allowed: 5MB"
    
    # Check file type
    file_type = uploaded_file.type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    
    if file_type not in allowed_types:
        return False, f"File type {file_type} not allowed. Allowed types: PDF, JPEG, PNG"
    
    return True, "File is valid"

# Save document to database as base64
def save_document(uploaded_file):
    if uploaded_file is None:
        return None
    
    # Read file as bytes and convert to base64
    file_bytes = uploaded_file.getvalue()
    file_base64 = base64.b64encode(file_bytes).decode("utf-8")
    
    # Create document data
    document_data = {
        "filename": uploaded_file.name,
        "content_type": uploaded_file.type,
        "size": uploaded_file.size,
        "content": file_base64,
        "uploaded_at": datetime.now()
    }
    
    return document_data

# Improved email sending function with detailed error handling
def send_email(receiver_email, subject, body):
    if not check_env_vars():
        return False
    
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = receiver_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        st.write(f"Attempting to send email to {receiver_email}...")
        
        # Try using SSL first (most common)
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, receiver_email, message.as_string())
                st.success(f"Email sent successfully to {receiver_email}")
                return True
        except Exception as ssl_error:
            st.warning(f"SSL connection failed: {ssl_error}. Trying TLS...")
            
            # Try using TLS as fallback
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, receiver_email, message.as_string())
                    st.success(f"Email sent successfully to {receiver_email} using TLS")
                    return True
            except Exception as tls_error:
                st.error(f"TLS connection also failed: {tls_error}")
                return False
                
    except Exception as e:
        st.error(f"Error preparing email: {e}")
        return False

# Check if email already exists
def email_exists(email):
    db = init_db()
    if db is None:
        return True  # Error case, assume email exists to prevent registration
    
    users = db["users"]
    return users.find_one({"email": email}) is not None

# Check if Aadhaar number already exists
def aadhaar_exists(aadhaar):
    db = init_db()
    if db is None:
        return True  # Error case, assume Aadhaar exists to prevent registration
    
    users = db["users"]
    return users.find_one({"aadhaar_number": aadhaar}) is not None

# Save user data after OTP verification
def save_verified_user(user_data):
    db = init_db()
    if db is None:
        return False, "Database connection error"
    
    users = db["users"]
    
    try:
        users.insert_one(user_data)
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration failed: {e}"

# User login with email or Aadhaar
def login_user(identifier, password, is_email=True):
    db = init_db()
    if db is None:
        return False, "Database connection error"
    
    users = db["users"]
    
    hashed_password = hash_password(password)
    
    # Search by email or Aadhaar number based on is_email flag
    query = {"email": identifier} if is_email else {"aadhaar_number": identifier}
    query["password"] = hashed_password
    
    user = users.find_one(query)
    
    if not user:
        return False, "Invalid credentials"
    
    # Set login time for session tracking
    st.session_state.login_time = datetime.now()
    
    # Initialize last activity time for auto-logout
    st.session_state.last_activity = time.time()
    
    return True, user

# Password reset functions
def request_password_reset(identifier, is_email=True):
    db = init_db()
    if db is None:
        return False, "Database connection error"
    
    users = db["users"]
    
    # Search by email or Aadhaar number
    query = {"email": identifier} if is_email else {"aadhaar_number": identifier}
    user = users.find_one(query)
    
    if not user:
        return False, f"{'Email' if is_email else 'Aadhaar number'} not registered"
    
    # Generate reset token and expiry
    reset_token = generate_otp(8)
    token_expiry = datetime.now() + timedelta(hours=1)
    
    result = users.update_one(
        query,
        {"$set": {"reset_token": reset_token, "reset_token_expiry": token_expiry}}
    )
    
    if result.modified_count == 0:
        return False, "Failed to create reset token"
    
    # Return reset token along with email for sending reset instructions
    return True, (reset_token, user["email"])

def reset_password(email, token, new_password):
    db = init_db()
    if db is None:
        return False, "Database connection error"
    
    users = db["users"]
    user = users.find_one({"email": email})
    
    if not user or user.get("reset_token") != token:
        return False, "Invalid reset token"
    
    # Check if token is expired
    token_expiry = user.get("reset_token_expiry")
    if not token_expiry or datetime.now() > token_expiry:
        return False, "Reset token expired"
    
    # Update password
    hashed_password = hash_password(new_password)
    result = users.update_one(
        {"email": email},
        {
            "$set": {"password": hashed_password},
            "$unset": {"reset_token": "", "reset_token_expiry": ""}
        }
    )
    
    if result.modified_count == 0:
        return False, "Password reset failed"
    
    return True, "Password reset successful"

# Auth UI components
def auth_ui():
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    
    # Set up session timeout check
    if 'last_activity' in st.session_state:
        # Check if user has been inactive for more than 5 minutes (300 seconds)
        if time.time() - st.session_state.last_activity > 300:
            st.session_state.clear()
            st.warning("Your session has expired due to inactivity. Please log in again.")
            st.session_state.auth_page = 'login'
        else:
            # Update last activity time
            st.session_state.last_activity = time.time()
    
    if st.session_state.auth_page == 'login':
        login_page()
    elif st.session_state.auth_page == 'signup':
        signup_page()
    elif st.session_state.auth_page == 'verify':
        verify_page()
    elif st.session_state.auth_page == 'forgot_password':
        forgot_password_page()
    elif st.session_state.auth_page == 'reset_password':
        reset_password_page()

def login_page():
    st.markdown("### 🔐 Login")
    
    with st.form("login_form"):
        # Add option to choose login method
        login_method = st.radio("Login with:", options=["Email", "Aadhaar Number"])
        
        # Adjust input field label based on login method
        identifier_label = "Email" if login_method == "Email" else "Aadhaar Number"
        identifier = st.text_input(identifier_label)
        
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not identifier or not password:
                st.error("Please fill in all fields")
            else:
                # Check if login is using email or Aadhaar
                is_email = (login_method == "Email")
                
                # If using Aadhaar, validate format
                if not is_email and not validate_aadhaar(identifier):
                    st.error("Invalid Aadhaar number format. Should be 12 digits.")
                else:
                    success, result = login_user(identifier, password, is_email)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign Up Instead"):
            st.session_state.auth_page = 'signup'
            st.rerun()
    
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.auth_page = 'forgot_password'
            st.rerun()

def signup_page():
    st.markdown("### 📝 Sign Up")
    
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        
        # New field for Aadhaar number
        aadhaar = st.text_input("Aadhaar Number (12 digits)")
        
        # Upload government ID document
        st.write("Upload Government ID Document (PDF, JPG, PNG - Max 5MB)")
        govt_doc = st.file_uploader("", type=["pdf", "jpg", "jpeg", "png"])
        
        if govt_doc is not None:
            file_size_mb = govt_doc.size / (1024 * 1024)
            st.write(f"File: {govt_doc.name} ({file_size_mb:.2f} MB)")
        
        # Birthday and gender fields
        col1, col2 = st.columns(2)
        with col1:
            birthday = st.date_input("Birthday", min_value=datetime(1900, 1, 1), max_value=datetime.now())
        with col2:
            gender = st.selectbox("Gender", options=["Male", "Female", "Other", "Prefer not to say"])
        
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            # Validate all required fields
            if not name or not email or not aadhaar or not password or not confirm_password:
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif not validate_aadhaar(aadhaar):
                st.error("Invalid Aadhaar number format. Should be 12 digits.")
            elif govt_doc is None:
                st.error("Please upload a government ID document")
            else:
                # Validate document file
                doc_valid, doc_message = validate_document(govt_doc)
                if not doc_valid:
                    st.error(doc_message)
                    return
                
                # Check if email or Aadhaar already exists
                if email_exists(email):
                    st.error("Email already registered")
                elif aadhaar_exists(aadhaar):
                    st.error("Aadhaar number already registered")
                else:
                    # Process and store document
                    document_data = save_document(govt_doc)
                    
                    # Store user data in session state temporarily
                    st.session_state.temp_user_data = {
                        "name": name,
                        "email": email,
                        "aadhaar_number": aadhaar,
                        "govt_document": document_data,
                        "birthday": birthday.isoformat(),  # Store date as ISO format string
                        "gender": gender,
                        "password": hash_password(password),
                        "role": "user",
                        "created_at": datetime.now()
                    }
                    
                    # Generate and store OTP for verification
                    otp = generate_otp()
                    st.session_state.verification_otp = otp
                    st.session_state.verification_email = email
                    
                    # Send verification email
                    email_subject = "Disaster Relief Dashboard - Verify Your Account"
                    email_body = f"""
                    Hello {name},

                    Thank you for registering with the Disaster Relief Dashboard.
                    Your verification code is: {otp}

                    This code will expire in 30 minutes.

                    Best regards,
                    Disaster Relief Dashboard Team
                    """
                    
                    if send_email(email, email_subject, email_body):
                        st.success("Please check your email for the verification code.")
                        st.session_state.auth_page = 'verify'
                        st.rerun()
                    else:
                        st.error("Failed to send verification email. Please try again later.")
    
    if st.button("Already have an account? Login"):
        st.session_state.auth_page = 'login'
        st.rerun()

def verify_page():
    st.markdown("### ✅ Verify Your Account")
    
    email = st.session_state.verification_email if 'verification_email' in st.session_state else ""
    st.info(f"A verification code has been sent to {email}")
    
    with st.form("verify_form"):
        otp = st.text_input("Enter Verification Code")
        submit = st.form_submit_button("Verify")
        
        if submit:
            if not otp:
                st.error("Please enter the verification code")
            else:
                stored_otp = st.session_state.get('verification_otp')
                if stored_otp and otp == stored_otp:
                    # Save the user data to the database only after OTP verification
                    if 'temp_user_data' in st.session_state:
                        success, message = save_verified_user(st.session_state.temp_user_data)
                        if success:
                            # Clear temporary data and verification info
                            del st.session_state.temp_user_data
                            del st.session_state.verification_otp
                            del st.session_state.verification_email
                            
                            st.success("Account verified and registration completed successfully!")
                            st.session_state.auth_page = 'login'
                            st.rerun()
                        else:
                            st.error(f"Failed to save user data: {message}")
                    else:
                        st.error("User data not found. Please try signing up again.")
                else:
                    st.error("Invalid verification code. Please try again.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Resend Code"):
            otp = generate_otp()
            st.session_state.verification_otp = otp
            
            # Get name from temp_user_data
            name = st.session_state.temp_user_data.get("name", "")
            email = st.session_state.verification_email
            
            email_subject = "Disaster Relief Dashboard - Your New Verification Code"
            email_body = f"""
            Hello {name},

            Your new verification code is: {otp}

            This code will expire in 30 minutes.

            Best regards,
            Disaster Relief Dashboard Team
            """
            
            if send_email(email, email_subject, email_body):
                st.success("New verification code sent!")
            else:
                st.error("Failed to send email. Please try again later.")
    
    with col2:
        if st.button("Back to Login"):
            # Clear temporary data if user cancels
            if 'temp_user_data' in st.session_state:
                del st.session_state.temp_user_data
            if 'verification_otp' in st.session_state:
                del st.session_state.verification_otp
            if 'verification_email' in st.session_state:
                del st.session_state.verification_email
                
            st.session_state.auth_page = 'login'
            st.rerun()

def forgot_password_page():
    st.markdown("### 🔑 Reset Password")
    
    with st.form("forgot_password_form"):
        # Add option to choose recovery method
        recovery_method = st.radio("Recover with:", options=["Email", "Aadhaar Number"])
        
        # Adjust input field label based on recovery method
        identifier_label = "Enter Your Email" if recovery_method == "Email" else "Enter Your Aadhaar Number"
        identifier = st.text_input(identifier_label)
        
        submit = st.form_submit_button("Send Reset Code")
        
        if submit:
            if not identifier:
                st.error(f"Please enter your {'email' if recovery_method == 'Email' else 'Aadhaar number'}")
            else:
                # Check if using Aadhaar for recovery
                is_email = (recovery_method == "Email")
                
                # If using Aadhaar, validate format
                if not is_email and not validate_aadhaar(identifier):
                    st.error("Invalid Aadhaar number format. Should be 12 digits.")
                else:
                    success, result = request_password_reset(identifier, is_email)
                    if success:
                        reset_token, email = result
                        
                        # Send password reset email
                        email_subject = "Disaster Relief Dashboard - Reset Your Password"
                        email_body = f"""
                        Hello,

                        You requested a password reset for your Disaster Relief Dashboard account.
                        Your password reset code is: {reset_token}

                        This code will expire in 1 hour.

                        If you did not request this reset, please ignore this email.

                        Best regards,
                        Disaster Relief Dashboard Team
                        """
                        
                        if send_email(email, email_subject, email_body):
                            st.success("Password reset code sent to your email!")
                            st.session_state.reset_email = email
                            st.session_state.auth_page = 'reset_password'
                            st.rerun()
                        else:
                            st.error("Failed to send email. Please try again later.")
                    else:
                        st.error(result)  # This will be the error message
    
    if st.button("Back to Login"):
        st.session_state.auth_page = 'login'
        st.rerun()

def reset_password_page():
    st.markdown("### 🔑 Create New Password")
    
    email = st.session_state.reset_email if 'reset_email' in st.session_state else ""
    st.info(f"Enter the reset code sent to {email}")
    
    with st.form("reset_password_form"):
        token = st.text_input("Reset Code")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Reset Password")
        
        if submit:
            if not token or not new_password or not confirm_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters long")
            else:
                success, message = reset_password(email, token, new_password)
                if success:
                    st.success(message)
                    # Clear reset email from session
                    if 'reset_email' in st.session_state:
                        del st.session_state.reset_email
                    st.session_state.auth_page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    if st.button("Back to Login"):
        st.session_state.auth_page = 'login'
        st.rerun()

# Check if user is logged in
def check_auth():
    # Update last activity time if user is logged in
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        # Check for session timeout
        if 'last_activity' in st.session_state:
            # Check if user has been inactive for more than 5 minutes (300 seconds)
            if time.time() - st.session_state.last_activity > 300:
                # Clear session and redirect to login
                st.session_state.clear()
                st.warning("Your session has expired due to inactivity. Please log in again.")
                auth_ui()
                return False
            else:
                # Update last activity time
                st.session_state.last_activity = time.time()
                return True
        else:
            # Initialize last activity time if not present
            st.session_state.last_activity = time.time()
            return True
    else:
        auth_ui()
        return False

# Include JavaScript for handling tab close events
def include_session_timeout_js():
    # JavaScript to handle page visibility change and tab close
    st.markdown("""
    <script>
    // Function to handle visibility change (tab switch)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
            // User switched away from tab
            localStorage.setItem('tabHiddenTime', Date.now());
        } else {
            // User returned to tab - check if timeout occurred
            const hiddenTime = localStorage.getItem('tabHiddenTime');
            if (hiddenTime) {
                const timeAway = Date.now() - parseInt(hiddenTime);
                // If away for more than 5 minutes (300000 ms)
                if (timeAway > 300000) {
                    // Force reload to trigger rerun and session check
                    window.location.reload();
                }
                // Clear the hidden time
                localStorage.removeItem('tabHiddenTime');
            }
        }
    });

    // Track user activity
    let inactivityTimer;
    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(function() {
            // Force reload after 5 minutes of inactivity
            window.location.reload();
        }, 300000); // 5 minutes
    }

    // Reset timer on user activity
    ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetInactivityTimer, true);
    });

    // Initialize the timer
    resetInactivityTimer();
    </script>
    """, unsafe_allow_html=True)