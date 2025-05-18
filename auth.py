"""
Authentication functionality for the attendance tracking system.
"""
import streamlit as st
import database as db
import config

def login(username, password):
    """
    Authenticate a user and set up session state.

    Args:
        username: The username to authenticate
        password: The password to verify

    Returns:
        bool: True if authentication successful, False otherwise
    """
    user = db.verify_user(username, password)

    if user:
        st.session_state[config.USER_SESSION_KEY] = user
        st.session_state[config.AUTH_STATUS_KEY] = True
        st.session_state[config.USER_ROLE_KEY] = user['role']
        return True

    return False

def logout():
    """Log out the current user by clearing session state."""
    st.session_state[config.USER_SESSION_KEY] = None
    st.session_state[config.AUTH_STATUS_KEY] = False
    st.session_state[config.USER_ROLE_KEY] = None

def is_authenticated():
    """Check if a user is currently authenticated."""
    return st.session_state.get(config.AUTH_STATUS_KEY, False)

def get_current_user():
    """Get the currently authenticated user."""
    return st.session_state.get(config.USER_SESSION_KEY, None)

def get_user_role():
    """Get the role of the currently authenticated user."""
    return st.session_state.get(config.USER_ROLE_KEY, None)

def require_auth(role=None):
    """
    Decorator to require authentication for a page.

    Args:
        role: Optional role requirement (admin or intern)

    Returns:
        The original function if authenticated, or redirects to login
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_authenticated():
                st.warning("Please log in to access this page.")
                st.stop()
                return

            if role and get_user_role() != role:
                st.error("You don't have permission to access this page.")
                st.stop()
                return

            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin(func):
    """Decorator to require admin role for a page."""
    return require_auth(role=config.ROLE_ADMIN)(func)

def require_intern(func):
    """Decorator to require intern role for a page."""
    return require_auth(role=config.ROLE_INTERN)(func)
