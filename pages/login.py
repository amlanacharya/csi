"""
Login page for the attendance tracking system.
"""
import streamlit as st
import auth
import utils
import time
import config  # Import config for debugging

def show():
    """Display the login page."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Intern Attendance Tracker")

    # Debug information (comment out in production)
    # st.sidebar.write("Session State:", st.session_state)

    # Check if we need to redirect after login
    if auth.is_authenticated():
        # If already authenticated, just stop here - main app will handle the rest
        return

    st.markdown("""
    <div class="card">
        <h2 style="text-align: center; margin-bottom: 1.5rem;">Login</h2>
    """, unsafe_allow_html=True)

    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                if auth.login(username, password):
                    st.success("Login successful!")
                    # Use a small delay to ensure the success message is shown
                    time.sleep(0.5)
                    # Use st.rerun() instead of JavaScript
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    st.info("Default admin credentials: admin / admin123")

    st.markdown("</div>", unsafe_allow_html=True)

    # Registration info
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p>New intern? Please contact your administrator to create an account.</p>
    </div>
    """, unsafe_allow_html=True)

    utils.display_footer()
