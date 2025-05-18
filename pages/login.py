"""
Login page for the attendance tracking system.
"""
import streamlit as st
import auth
import utils
# config not used directly in this file

def show():
    """Display the login page."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Intern Attendance Tracker")

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
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Registration info
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p>New intern? Please contact your administrator to create an account.</p>
    </div>
    """, unsafe_allow_html=True)

    utils.display_footer()
