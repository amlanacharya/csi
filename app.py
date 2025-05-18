"""
Main application file for the Intern Attendance Tracker.
"""
import streamlit as st
# No need for os and Path imports

# Set page config at the very beginning
st.set_page_config(
    page_title="Intern Attendance Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import configuration and utilities
import config
import utils
import auth
import database as db

# Import pages
from pages import login
from pages.admin import dashboard as admin_dashboard
from pages.admin import manage_interns
from pages.admin import reports
from pages.intern import dashboard as intern_dashboard
from pages.intern import attendance

# Initialize database
db.init_db()

# Initialize session state
if "initialized" not in st.session_state:
    config.init_session_state()
    st.session_state.initialized = True

# Debug information (comment out in production)
# st.sidebar.write("Session State:", st.session_state)

def main():
    """Main application entry point."""
    # Apply custom CSS
    utils.apply_custom_css()

    # Check if user is authenticated
    if not auth.is_authenticated():
        # Show login page
        login.show()
    else:
        # Show sidebar navigation
        with st.sidebar:
            utils.display_logo()
            st.markdown("---")

            # Get current user and role
            user = auth.get_current_user()
            role = auth.get_user_role()

            st.markdown(f"**Welcome, {user['name']}!**")
            st.markdown(f"Role: {role.capitalize()}")
            st.markdown("---")

            # Navigation options based on role
            if role == config.ROLE_ADMIN:
                # Admin navigation
                st.markdown("### Navigation")
                page = st.radio(
                    "Go to",
                    ["Dashboard", "Manage Interns", "Reports"],
                    label_visibility="collapsed"
                )

                st.markdown("---")
                if st.button("Logout"):
                    auth.logout()
                    # Use st.rerun() instead of JavaScript
                    st.rerun()
            else:
                # Intern navigation
                st.markdown("### Navigation")
                page = st.radio(
                    "Go to",
                    ["Dashboard", "Attendance"],
                    label_visibility="collapsed"
                )

                st.markdown("---")
                if st.button("Logout"):
                    auth.logout()
                    # Use st.rerun() instead of JavaScript
                    st.rerun()

        # Display selected page
        if role == config.ROLE_ADMIN:
            if page == "Dashboard":
                admin_dashboard.show()
            elif page == "Manage Interns":
                manage_interns.show()
            elif page == "Reports":
                reports.show()
        else:
            if page == "Dashboard":
                intern_dashboard.show()
            elif page == "Attendance":
                attendance.show()

if __name__ == "__main__":
    main()
