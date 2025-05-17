# Intern Attendance Tracker

A Python and Streamlit-based daily attendance tracking system for interns at a corporate organization.

## Features

- **User Authentication**: Secure login for interns and administrators
- **Daily Check-in/Check-out**: Record attendance with timestamps
- **Attendance History**: View and analyze past attendance records
- **Dashboard**: Visual representation of attendance statistics
- **Export Capabilities**: Download attendance records in Excel or CSV format
- **Admin Panel**: Manage intern profiles and review attendance data

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd intern-attendance-tracker
   ```

2. Create a virtual environment and activate it:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Add your company logo:
   - Place your company logo (preferably in PNG format) in the `static` folder
   - Name it `logo.png` or update the `LOGO_PATH` in `config.py`

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```

2. Access the application in your web browser at `http://localhost:8501`

3. Default admin credentials:
   - Username: `admin`
   - Password: `admin123`

## System Structure

- `app.py`: Main application entry point
- `config.py`: Configuration settings
- `database.py`: Database operations
- `auth.py`: Authentication functionality
- `utils.py`: Utility functions
- `pages/`: Directory containing different pages
  - `login.py`: Login page
  - `admin/`: Admin pages
    - `dashboard.py`: Admin dashboard
    - `manage_interns.py`: Intern management
    - `reports.py`: Attendance reports
  - `intern/`: Intern pages
    - `dashboard.py`: Intern dashboard
    - `attendance.py`: Check-in/out functionality
- `static/`: Static assets (logo, etc.)
- `data/`: Database and data files

## Customization

You can customize various aspects of the application by modifying the following files:

- `config.py`: Change application settings, company name, work hours, etc.
- `utils.py`: Modify the theme and styling
- `static/logo.png`: Replace with your company logo

## Security Considerations

- The default admin password should be changed immediately after the first login
- The application uses password hashing for security
- For production deployment, consider adding additional security measures

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For any issues or questions, please contact [your-email@example.com]
