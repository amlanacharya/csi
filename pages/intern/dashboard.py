"""
Intern dashboard page for the attendance tracking system.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database as db
import auth
import utils
import config

@auth.require_intern
def show():
    """Display the intern dashboard."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Intern Dashboard")

    # Get current user
    user = auth.get_current_user()
    st.markdown(f"Welcome, **{user['name']}**!")

    # Current date and time
    now = datetime.now()
    current_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")

    st.markdown(f"""
    <div class="card">
        <h3>Today's Date: {current_date}</h3>
        <h3>Current Time: {current_time}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Check today's attendance status
    today_date = now.strftime("%Y-%m-%d")
    attendance = db.get_attendance(user['id'], today_date, today_date)

    # Display attendance status and check-in/out buttons
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h2 class='sub-header'>Today's Attendance</h2>", unsafe_allow_html=True)

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

    with col2:
        st.markdown("<h2 class='sub-header'>Actions</h2>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Check-in button
        if not attendance or not attendance[0]['check_in_time']:
            if st.button("Check In", key="check_in"):
                if db.record_check_in(user['id']):
                    st.success("Check-in recorded successfully!")
                    st.rerun()
                else:
                    st.error("Failed to record check-in.")

        # Check-out button
        if attendance and attendance[0]['check_in_time'] and not attendance[0]['check_out_time']:
            if st.button("Check Out", key="check_out"):
                if db.record_check_out(user['id']):
                    st.success("Check-out recorded successfully!")
                    st.rerun()
                else:
                    st.error("Failed to record check-out.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Attendance history
    st.markdown("<h2 class='sub-header'>Attendance History</h2>", unsafe_allow_html=True)

    # Date range selector
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

    # Convert dates to string format for database query
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # Get attendance data
    attendance_data = db.get_attendance(user['id'], start_str, end_str)

    if attendance_data:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(attendance_data)

        # Format the DataFrame for display
        display_df = df[['date', 'check_in_time', 'check_out_time', 'status']].copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['check_in_time'] = display_df['check_in_time'].apply(utils.format_time)
        display_df['check_out_time'] = display_df['check_out_time'].apply(utils.format_time)
        display_df.columns = ['Date', 'Check-in', 'Check-out', 'Status']

        # Display the DataFrame
        st.dataframe(display_df, use_container_width=True)

        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export to Excel"):
                st.markdown(utils.export_to_excel(display_df, "my_attendance.xlsx"), unsafe_allow_html=True)
        with col2:
            if st.button("Export to CSV"):
                st.markdown(utils.export_to_csv(display_df, "my_attendance.csv"), unsafe_allow_html=True)

        # Attendance statistics
        st.markdown("<h2 class='sub-header'>Attendance Statistics</h2>", unsafe_allow_html=True)

        # Calculate statistics
        total_days = (end_date - start_date).days + 1
        present_days = len(df[df['status'] == config.STATUS_PRESENT])
        late_days = len(df[df['status'] == config.STATUS_LATE])
        absent_days = total_days - len(df)

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

        # Attendance trend chart
        df['date'] = pd.to_datetime(df['date'])
        df['day'] = df['date'].dt.day_name()

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

        # Calendar-like attendance visualization
        st.markdown("<h3>Attendance Calendar</h3>", unsafe_allow_html=True)

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

        # Merge to get status for each day
        calendar_df = calendar_df.merge(
            attendance_df[['date_str', 'status']],
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
                    fig.add_annotation(
                        x=j,
                        y=i,
                        text=f"{day_num}<br>{status}",
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
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No attendance data available for the selected date range.")

    utils.display_footer()
