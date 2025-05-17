"""
Test script to verify the application runs without errors.
"""
import streamlit as st

# Set page config at the very beginning
st.set_page_config(
    page_title="Test App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Test Application")
st.write("If you can see this, the page config is working correctly!")

# Add a simple form
st.header("Login Form")
with st.form("test_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")
    
    if submit:
        st.success(f"Form submitted with username: {username}")
