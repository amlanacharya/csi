"""
Configuration settings for the attendance tracking system.
"""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DB_PATH = os.path.join(BASE_DIR, "data", "attendance.db")

# Application settings
APP_NAME = "Intern Attendance Tracker"
COMPANY_NAME = "Corporate Organization"
LOGO_PATH = os.path.join(BASE_DIR, "static", "logo.png")

# Session state keys
USER_SESSION_KEY = "user"
AUTH_STATUS_KEY = "authenticated"
USER_ROLE_KEY = "user_role"

# Roles
ROLE_ADMIN = "admin"
ROLE_INTERN = "intern"

# Attendance status
STATUS_PRESENT = "Present"
STATUS_ABSENT = "Absent"
STATUS_HALF_DAY = "Half Day"
STATUS_LATE = "Late"

# Time settings
WORK_START_TIME = "09:00"  # 9 AM
WORK_END_TIME = "17:00"    # 5 PM
LATE_THRESHOLD = 30        # Minutes

# Initialize session state
def init_session_state():
    """Initialize the session state variables."""
    if USER_SESSION_KEY not in st.session_state:
        st.session_state[USER_SESSION_KEY] = None
    if AUTH_STATUS_KEY not in st.session_state:
        st.session_state[AUTH_STATUS_KEY] = False
    if USER_ROLE_KEY not in st.session_state:
        st.session_state[USER_ROLE_KEY] = None
