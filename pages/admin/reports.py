"""
Reports page for the attendance tracking system.
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
    """Display the reports page."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Attendance Reports")

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

    if attendance_data:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(attendance_data)

        # Format the DataFrame for display
        display_df = df[['name', 'date', 'check_in_time', 'check_out_time', 'status', 'department']].copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['check_in_time'] = display_df['check_in_time'].apply(utils.format_time)
        display_df['check_out_time'] = display_df['check_out_time'].apply(utils.format_time)
        display_df.columns = ['Name', 'Date', 'Check-in', 'Check-out', 'Status', 'Department']

        # Display the DataFrame
        st.dataframe(display_df, use_container_width=True)

        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export to Excel"):
                st.markdown(utils.export_to_excel(display_df, "attendance_report.xlsx"), unsafe_allow_html=True)
        with col2:
            if st.button("Export to CSV"):
                st.markdown(utils.export_to_csv(display_df, "attendance_report.csv"), unsafe_allow_html=True)

        # Visualizations
        st.markdown("<h2 class='sub-header'>Attendance Analysis</h2>", unsafe_allow_html=True)

        # Status distribution
        status_counts = df.groupby('status').size().reset_index(name='count')
        status_counts.columns = ['Status', 'Count']

        fig = px.pie(
            status_counts,
            values='Count',
            names='Status',
            title='Attendance Status Distribution',
            hole=0.4
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Daily attendance trend
        df['date'] = pd.to_datetime(df['date'])
        daily_counts = df.groupby([df['date'].dt.date, 'status']).size().reset_index(name='count')
        daily_counts.columns = ['Date', 'Status', 'Count']

        fig = px.line(
            daily_counts,
            x='Date',
            y='Count',
            color='Status',
            title='Daily Attendance by Status',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Count",
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
        )
        st.plotly_chart(fig, use_container_width=True)

        # Department-wise attendance
        if 'department' in df.columns:
            dept_status = df.groupby(['department', 'status']).size().reset_index(name='count')
            dept_status.columns = ['Department', 'Status', 'Count']

            fig = px.bar(
                dept_status,
                x='Department',
                y='Count',
                color='Status',
                title='Department-wise Attendance Status',
                barmode='group'
            )
            fig.update_layout(
                xaxis_title="Department",
                yaxis_title="Count",
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
            )
            st.plotly_chart(fig, use_container_width=True)

        # Individual attendance report
        st.markdown("<h2 class='sub-header'>Individual Attendance Report</h2>", unsafe_allow_html=True)

        # Get all interns
        interns = db.get_all_users(role=config.ROLE_INTERN)

        if interns:
            # Select intern
            selected_intern = st.selectbox(
                "Select Intern",
                [f"{intern['id']} - {intern['name']}" for intern in interns]
            )
            selected_id = int(selected_intern.split(" - ")[0])

            # Filter data for selected intern
            intern_df = df[df['user_id'] == selected_id]

            if not intern_df.empty:
                # Format for display
                display_intern_df = intern_df[['date', 'check_in_time', 'check_out_time', 'status']].copy()
                display_intern_df['date'] = display_intern_df['date'].dt.strftime('%Y-%m-%d')
                display_intern_df['check_in_time'] = display_intern_df['check_in_time'].apply(utils.format_time)
                display_intern_df['check_out_time'] = display_intern_df['check_out_time'].apply(utils.format_time)
                display_intern_df.columns = ['Date', 'Check-in', 'Check-out', 'Status']

                st.dataframe(display_intern_df, use_container_width=True)

                # Calculate statistics
                total_days = (end_date - start_date).days + 1
                present_days = len(intern_df[intern_df['status'] == config.STATUS_PRESENT])
                late_days = len(intern_df[intern_df['status'] == config.STATUS_LATE])
                absent_days = total_days - len(intern_df)

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    utils.display_stat_card(total_days, "Total Days")
                with col2:
                    utils.display_stat_card(present_days, "Present")
                with col3:
                    utils.display_stat_card(late_days, "Late")
                with col4:
                    utils.display_stat_card(absent_days, "Absent")

                # Export individual report
                if st.button("Export Individual Report"):
                    st.markdown(utils.export_to_excel(display_intern_df, f"attendance_report_{selected_id}.xlsx"), unsafe_allow_html=True)
            else:
                st.info("No attendance records found for the selected intern in this date range.")
    else:
        st.info("No attendance data available for the selected date range.")

    utils.display_footer()
