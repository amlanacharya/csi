"""
Utility functions for the attendance tracking system.
"""
import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import base64
from io import BytesIO
import config

def format_time(timestamp):
    """Format timestamp for display."""
    if not timestamp:
        return "-"

    if isinstance(timestamp, str):
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return timestamp
    else:
        dt = timestamp

    return dt.strftime("%I:%M %p")

def format_date(date_val):
    """Format date for display."""
    if not date_val:
        return "-"

    # Handle pandas Timestamp objects
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%b %d, %Y")

    # Handle string dates
    if isinstance(date_val, str):
        try:
            dt = datetime.strptime(date_val, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")
        except ValueError:
            return date_val

    # Return as is for other types
    return str(date_val)

def get_date_range(days=30):
    """Get date range for filtering (default: last 30 days)."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def export_to_excel(df, filename="export.xlsx"):
    """
    Export DataFrame to Excel file and provide download link.

    Args:
        df: Pandas DataFrame to export
        filename: Name of the Excel file

    Returns:
        Download link for the Excel file
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        # Auto-adjust columns' width
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)

    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel file</a>'
    return href

def export_to_csv(df, filename="export.csv"):
    """
    Export DataFrame to CSV file and provide download link.

    Args:
        df: Pandas DataFrame to export
        filename: Name of the CSV file

    Returns:
        Download link for the CSV file
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href

def apply_custom_css():
    """Apply custom CSS to the Streamlit app."""
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .stat-card {
            text-align: center;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f4f8;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1E3A8A;
        }
        .stat-label {
            font-size: 1rem;
            color: #4B5563;
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
            color: #6B7280;
            font-size: 0.875rem;
        }
        .stButton button {
            background-color: #1E3A8A;
            color: white;
            border-radius: 0.25rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton button:hover {
            background-color: #1e40af;
        }
        .success-alert {
            padding: 1rem;
            background-color: #d1fae5;
            color: #065f46;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        .warning-alert {
            padding: 1rem;
            background-color: #fef3c7;
            color: #92400e;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        .error-alert {
            padding: 1rem;
            background-color: #fee2e2;
            color: #b91c1c;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_theme():
    """Apply theme to the Streamlit app (for backward compatibility)."""
    apply_custom_css()

def display_logo():
    """Display the company logo."""
    if os.path.exists(config.LOGO_PATH):
        st.image(config.LOGO_PATH, width=200)
    else:
        st.title(config.COMPANY_NAME)

def display_header(title):
    """Display a header with the given title."""
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)

def display_subheader(title):
    """Display a subheader with the given title."""
    st.markdown(f'<h2 class="sub-header">{title}</h2>', unsafe_allow_html=True)

def display_card(content):
    """Display content in a card."""
    st.markdown(f'<div class="card">{content}</div>', unsafe_allow_html=True)

def display_stat_card(value, label):
    """Display a statistic in a card."""
    st.markdown(f'''
    <div class="stat-card">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    ''', unsafe_allow_html=True)

def display_footer():
    """Display the footer."""
    st.markdown(f'''
    <div class="footer">
        <p>{config.APP_NAME} &copy; {datetime.now().year} {config.COMPANY_NAME}. All rights reserved.</p>
    </div>
    ''', unsafe_allow_html=True)

def success_message(message):
    """Display a success message."""
    st.markdown(f'<div class="success-alert">{message}</div>', unsafe_allow_html=True)

def warning_message(message):
    """Display a warning message."""
    st.markdown(f'<div class="warning-alert">{message}</div>', unsafe_allow_html=True)

def error_message(message):
    """Display an error message."""
    st.markdown(f'<div class="error-alert">{message}</div>', unsafe_allow_html=True)
