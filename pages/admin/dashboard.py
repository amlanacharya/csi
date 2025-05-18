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
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Admin Dashboard")

    # Get current user
    user = auth.get_current_user()
    st.markdown(f"Welcome, **{user['name']}**!")

    # Date range selector (using Indian time)
    now = utils.get_indian_time()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=now.date() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=now.date()
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

        # Attendance Calendar
        st.markdown("<h2 class='sub-header'>Attendance Calendar</h2>", unsafe_allow_html=True)

        # Create a date range for the selected period
        date_range = pd.date_range(start=start_date, end=end_date)

        # Create a DataFrame with all dates in the range
        calendar_df = pd.DataFrame({'date': date_range})
        calendar_df['day'] = calendar_df['date'].dt.day_name()
        calendar_df['week'] = calendar_df['date'].dt.isocalendar().week
        calendar_df['month'] = calendar_df['date'].dt.month_name()
        calendar_df['day_num'] = calendar_df['date'].dt.day

        # Merge with attendance data
        calendar_df['date_str'] = calendar_df['date'].dt.strftime('%Y-%m-%d')
        attendance_df = pd.DataFrame(attendance_data)
        attendance_df['date_str'] = pd.to_datetime(attendance_df['date']).dt.strftime('%Y-%m-%d')

        # Count attendance by date and status
        status_by_date = attendance_df.groupby(['date_str', 'status']).size().reset_index(name='count')

        # Get the most common status for each date
        status_by_date = status_by_date.sort_values('count', ascending=False)
        status_by_date = status_by_date.drop_duplicates('date_str')

        # Merge to get status for each day
        calendar_df = calendar_df.merge(
            status_by_date[['date_str', 'status']],
            on='date_str',
            how='left'
        )

        # Fill missing status with 'Absent'
        calendar_df['status'].fillna(config.STATUS_ABSENT, inplace=True)

        # Define color mapping for different statuses
        color_map = {
            config.STATUS_PRESENT: '#28a745',  # Green
            config.STATUS_LATE: '#ffc107',     # Yellow
            config.STATUS_HALF_DAY: '#17a2b8', # Blue
            config.STATUS_ABSENT: '#dc3545'    # Red
        }

        # Create a numeric value for each status for the heatmap
        status_value_map = {
            config.STATUS_PRESENT: 3,
            config.STATUS_LATE: 2,
            config.STATUS_HALF_DAY: 1,
            config.STATUS_ABSENT: 0
        }

        calendar_df['status_value'] = calendar_df['status'].map(status_value_map)

        # Create a heatmap calendar
        # Group by week and day for the heatmap
        calendar_pivot = calendar_df.pivot_table(
            index='week',
            columns='day',
            values='status_value',
            aggfunc='first'
        )

        # Reorder columns to start with Monday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        calendar_pivot = calendar_pivot.reindex(columns=day_order)

        # Create the heatmap
        fig = px.imshow(
            calendar_pivot,
            labels=dict(x="Day of Week", y="Week", color="Status"),
            x=calendar_pivot.columns,
            y=calendar_pivot.index,
            color_continuous_scale=[
                [0.0, color_map[config.STATUS_ABSENT]],
                [0.33, color_map[config.STATUS_HALF_DAY]],
                [0.66, color_map[config.STATUS_LATE]],
                [1.0, color_map[config.STATUS_PRESENT]]
            ],
            title="Attendance Calendar"
        )

        # Add date annotations to the heatmap
        for i, week in enumerate(calendar_pivot.index):
            for j, day in enumerate(calendar_pivot.columns):
                day_data = calendar_df[(calendar_df['week'] == week) & (calendar_df['day'] == day)]
                if not day_data.empty:
                    day_num = day_data.iloc[0]['day_num']
                    status = day_data.iloc[0]['status']
                    count = attendance_df[attendance_df['date_str'] == day_data.iloc[0]['date_str']].shape[0]
                    fig.add_annotation(
                        x=j,
                        y=i,
                        text=f"{day_num}<br>{count} {status}",
                        showarrow=False,
                        font=dict(color="white" if status in [config.STATUS_ABSENT, config.STATUS_PRESENT] else "black")
                    )

        # Update layout
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            xaxis=dict(side="top"),
            coloraxis_showscale=False
        )

        # Add a legend/color guide
        st.markdown("<div style='display: flex; justify-content: center; margin-top: 10px;'>", unsafe_allow_html=True)
        for status, color in color_map.items():
            st.markdown(
                f"<div style='margin: 0 10px;'><span style='display: inline-block; width: 15px; height: 15px; background-color: {color}; margin-right: 5px;'></span>{status}</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

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
