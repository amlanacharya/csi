"""
Attendance page for interns to check in and out.
"""
import streamlit as st
from datetime import datetime
import database as db
import auth
import utils
# config not used directly in this file

@auth.require_intern
def show():
    """Display the attendance page for interns."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Attendance")

    # Get current user
    user = auth.get_current_user()

    # Current date and time (using Indian time - GMT+5:30)
    now = utils.get_indian_time()
    current_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    timezone_info = "IST (GMT+5:30)"

    st.markdown(f"""
    <div class="card">
        <h3>Today's Date: {current_date}</h3>
        <h3>Current Time: {current_time} ({timezone_info})</h3>
    </div>
    """, unsafe_allow_html=True)

    # Check today's attendance status
    today_date = now.strftime("%Y-%m-%d")
    attendance = db.get_attendance(user['id'], today_date, today_date)

    # Display attendance status
    st.markdown("<h2 class='sub-header'>Today's Attendance Status</h2>", unsafe_allow_html=True)

    if attendance:
        attendance_record = attendance[0]
        check_in_time = utils.format_time(attendance_record['check_in_time']) if attendance_record['check_in_time'] else "Not checked in"
        check_out_time = utils.format_time(attendance_record['check_out_time']) if attendance_record['check_out_time'] else "Not checked out"
        status = attendance_record['status']

        st.markdown(f"""
        <div class="card">
            <p><strong>Status:</strong> {status}</p>
            <p><strong>Check-in Time:</strong> {check_in_time}</p>
            <p><strong>Check-out Time:</strong> {check_out_time}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <p><strong>Status:</strong> Not checked in</p>
            <p><strong>Check-in Time:</strong> -</p>
            <p><strong>Check-out Time:</strong> -</p>
        </div>
        """, unsafe_allow_html=True)

    # Check-in/out actions
    st.markdown("<h2 class='sub-header'>Actions</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3>Check In</h3>", unsafe_allow_html=True)

        if not attendance or not attendance[0]['check_in_time']:
            if st.button("Check In Now", key="check_in_now"):
                if db.record_check_in(user['id']):
                    utils.success_message("Check-in recorded successfully!")
                    st.rerun()
                else:
                    utils.error_message("Failed to record check-in.")
        else:
            utils.warning_message("You have already checked in today.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3>Check Out</h3>", unsafe_allow_html=True)

        if attendance and attendance[0]['check_in_time'] and not attendance[0]['check_out_time']:
            if st.button("Check Out Now", key="check_out_now"):
                if db.record_check_out(user['id']):
                    utils.success_message("Check-out recorded successfully!")
                    st.rerun()
                else:
                    utils.error_message("Failed to record check-out.")
        elif not attendance or not attendance[0]['check_in_time']:
            utils.warning_message("You need to check in first.")
        else:
            utils.warning_message("You have already checked out today.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Attendance guidelines
    st.markdown("<h2 class='sub-header'>Attendance Guidelines</h2>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Working Hours")
        st.write("Regular working hours are from 9:00 AM to 5:00 PM, Monday to Friday.")

        st.subheader("Check-in Policy")
        st.write("• All interns are expected to check in by 9:00 AM.")
        st.write("• Check-ins after 9:30 AM will be marked as \"Late\".")

        st.subheader("Check-out Policy")
        st.write("• Interns should check out after completing their work for the day.")
        st.write("• Early check-outs (before 5:00 PM) may be marked as \"Half Day\" unless approved.")

        st.subheader("Absence")
        st.write("If you are unable to attend, please notify your supervisor in advance.")

        st.markdown('</div>', unsafe_allow_html=True)

    utils.display_footer()
