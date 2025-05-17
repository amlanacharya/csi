"""
Admin dashboard page for the attendance tracking system.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database as db
import auth
import utils
import config

@auth.require_admin
def show():
    """Display the admin dashboard."""
    utils.apply_theme()
    utils.display_logo()
    utils.display_header("Admin Dashboard")
    
    # Get current user
    user = auth.get_current_user()
    st.markdown(f"Welcome, **{user['name']}**!")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date()
        )
    
    # Department filter
    departments = ["All"] + [dept["name"] for dept in db.get_departments()]
    selected_dept = st.selectbox("Department", departments)
    
    # Convert dates to string format for database query
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Get attendance data
    if selected_dept == "All":
        attendance_data = db.get_all_attendance(start_str, end_str)
    else:
        attendance_data = db.get_all_attendance(start_str, end_str, selected_dept)
    
    # Get all interns
    interns = db.get_all_users(role=config.ROLE_INTERN)
    
    # Display statistics
    st.markdown("<h2 class='sub-header'>Attendance Statistics</h2>", unsafe_allow_html=True)
    
    if attendance_data:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(attendance_data)
        
        # Calculate statistics
        total_interns = len(interns)
        active_interns = len(df['user_id'].unique())
        total_check_ins = len(df)
        
        # Calculate present, late, and absent counts
        present_count = len(df[df['status'] == config.STATUS_PRESENT])
        late_count = len(df[df['status'] == config.STATUS_LATE])
        
        # Calculate attendance rate
        if total_interns > 0:
            attendance_rate = (active_interns / total_interns) * 100
        else:
            attendance_rate = 0
        
        # Display statistics in cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            utils.display_stat_card(total_interns, "Total Interns")
        with col2:
            utils.display_stat_card(f"{attendance_rate:.1f}%", "Attendance Rate")
        with col3:
            utils.display_stat_card(present_count, "Present")
        with col4:
            utils.display_stat_card(late_count, "Late")
        
        # Attendance trend chart
        st.markdown("<h2 class='sub-header'>Attendance Trend</h2>", unsafe_allow_html=True)
        
        # Group by date and count
        df['date'] = pd.to_datetime(df['date'])
        daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='count')
        daily_counts.columns = ['Date', 'Check-ins']
        
        # Create line chart
        fig = px.line(
            daily_counts, 
            x='Date', 
            y='Check-ins',
            title='Daily Attendance',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Check-ins",
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Department distribution
        if 'department' in df.columns:
            st.markdown("<h2 class='sub-header'>Department Distribution</h2>", unsafe_allow_html=True)
            dept_counts = df.groupby('department').size().reset_index(name='count')
            dept_counts.columns = ['Department', 'Check-ins']
            
            fig = px.pie(
                dept_counts, 
                values='Check-ins', 
                names='Department',
                title='Attendance by Department',
                hole=0.4
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.markdown("<h2 class='sub-header'>Recent Activity</h2>", unsafe_allow_html=True)
        recent_df = df.sort_values('date', ascending=False).head(10)
        
        # Format the DataFrame for display
        display_df = recent_df[['name', 'date', 'check_in_time', 'check_out_time', 'status']].copy()
        display_df['date'] = display_df['date'].apply(utils.format_date)
        display_df['check_in_time'] = display_df['check_in_time'].apply(utils.format_time)
        display_df['check_out_time'] = display_df['check_out_time'].apply(utils.format_time)
        display_df.columns = ['Name', 'Date', 'Check-in', 'Check-out', 'Status']
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No attendance data available for the selected date range.")
    
    utils.display_footer()
