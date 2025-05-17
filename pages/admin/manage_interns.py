"""
Intern management page for the attendance tracking system.
"""
import streamlit as st
import pandas as pd
import database as db
import auth
import utils
import config

@auth.require_admin
def show():
    """Display the intern management page."""
    utils.apply_custom_css()
    utils.display_logo()
    utils.display_header("Manage Interns")

    # Tabs for different management functions
    tab1, tab2, tab3 = st.tabs(["Intern List", "Add Intern", "Departments"])

    # Tab 1: Intern List
    with tab1:
        st.markdown("<h2 class='sub-header'>Intern List</h2>", unsafe_allow_html=True)

        # Get all interns
        interns = db.get_all_users(role=config.ROLE_INTERN)

        if interns:
            # Convert to DataFrame for display
            df = pd.DataFrame(interns)

            # Format the DataFrame
            display_df = df[['id', 'name', 'username', 'email', 'department', 'created_at']].copy()
            display_df.columns = ['ID', 'Name', 'Username', 'Email', 'Department', 'Joined Date']

            # Display the DataFrame
            st.dataframe(display_df, use_container_width=True)

            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Export to Excel"):
                    st.markdown(utils.export_to_excel(display_df, "interns.xlsx"), unsafe_allow_html=True)
            with col2:
                if st.button("Export to CSV"):
                    st.markdown(utils.export_to_csv(display_df, "interns.csv"), unsafe_allow_html=True)

            # Intern details and actions
            st.markdown("<h3>Intern Details</h3>", unsafe_allow_html=True)

            # Select intern
            selected_id = st.selectbox("Select Intern", [f"{intern['id']} - {intern['name']}" for intern in interns])
            selected_id = int(selected_id.split(" - ")[0])

            # Get selected intern
            selected_intern = next((intern for intern in interns if intern['id'] == selected_id), None)

            if selected_intern:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **Name:** {selected_intern['name']}<br>
                    **Username:** {selected_intern['username']}<br>
                    **Email:** {selected_intern['email']}<br>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    **Department:** {selected_intern['department'] or 'Not assigned'}<br>
                    **Joined:** {selected_intern['created_at']}<br>
                    """, unsafe_allow_html=True)

                # Actions
                st.markdown("<h4>Actions</h4>", unsafe_allow_html=True)

                # Edit intern details
                with st.expander("Edit Intern Details"):
                    with st.form("edit_intern_form"):
                        name = st.text_input("Name", value=selected_intern['name'])
                        email = st.text_input("Email", value=selected_intern['email'])

                        # Department dropdown
                        departments = [dept["name"] for dept in db.get_departments()]
                        department = st.selectbox(
                            "Department",
                            departments,
                            index=departments.index(selected_intern['department']) if selected_intern['department'] in departments else 0
                        )

                        submit = st.form_submit_button("Update")

                        if submit:
                            if db.update_user(selected_intern['id'], name, email, department):
                                st.success("Intern details updated successfully!")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update intern details.")

                # Reset password
                with st.expander("Reset Password"):
                    with st.form("reset_password_form"):
                        new_password = st.text_input("New Password", type="password")
                        confirm_password = st.text_input("Confirm Password", type="password")

                        submit = st.form_submit_button("Reset Password")

                        if submit:
                            if not new_password or not confirm_password:
                                st.error("Please enter both fields.")
                            elif new_password != confirm_password:
                                st.error("Passwords do not match.")
                            else:
                                if db.change_password(selected_intern['id'], new_password):
                                    st.success("Password reset successfully!")
                                else:
                                    st.error("Failed to reset password.")
        else:
            st.info("No interns found. Add interns using the 'Add Intern' tab.")

    # Tab 2: Add Intern
    with tab2:
        st.markdown("<h2 class='sub-header'>Add New Intern</h2>", unsafe_allow_html=True)

        with st.form("add_intern_form"):
            name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            # Department dropdown
            departments = [dept["name"] for dept in db.get_departments()]
            department = st.selectbox("Department", departments)

            submit = st.form_submit_button("Add Intern")

            if submit:
                if not name or not username or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    if db.add_user(username, password, config.ROLE_INTERN, name, email, department):
                        st.success(f"Intern '{name}' added successfully!")
                        # Clear form
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add intern. Username or email may already exist.")

    # Tab 3: Departments
    with tab3:
        st.markdown("<h2 class='sub-header'>Manage Departments</h2>", unsafe_allow_html=True)

        # Get all departments
        departments = db.get_departments()

        if departments:
            # Convert to DataFrame for display
            df = pd.DataFrame(departments)

            # Format the DataFrame
            display_df = df[['id', 'name']].copy()
            display_df.columns = ['ID', 'Department Name']

            # Display the DataFrame
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No departments found.")

        # Add new department
        st.markdown("<h3>Add New Department</h3>", unsafe_allow_html=True)

        with st.form("add_department_form"):
            dept_name = st.text_input("Department Name")
            submit = st.form_submit_button("Add Department")

            if submit:
                if not dept_name:
                    st.error("Please enter a department name.")
                else:
                    if db.add_department(dept_name):
                        st.success(f"Department '{dept_name}' added successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add department. It may already exist.")

    utils.display_footer()
