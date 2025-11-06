import streamlit as st
import pandas as pd
import folium
import sys
import os
import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import All Logic ---

# Epic 0: Auth
from epic_0_auth.login import login
from epic_0_auth.new_user import create_new_user
from epic_0_auth.forgot_password import request_password_reset, reset_password

# Epic 1: Routing
from epic_1_routing.assignment_logic import (
    get_available_drivers, get_available_vehicles, 
    get_pending_bookings, create_route_assignment, 
    get_daily_booking_report, get_active_vehicles_by_date
)

# Epic 2: Operations
from epic_2_operations.tracking_logic import (
    get_live_vehicle_locations, get_driver_assignment, 
    mark_stop_complete, log_driver_location,
    get_route_history
)

# Epic 3: Billing
from epic_3_billing.booking_logic import (
    create_booking, get_client_bookings, 
    get_client_collection_points, add_collection_point
)

# --- NEW: Epic 4 Imports ---
from epic_4_communication.chat_logic import get_group_messages, send_group_message
from epic_4_communication.feedback_logic import submit_feedback, get_all_feedback


# UI Components
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation


# -----------------------------------------------------------------
# --- 1. AUTHENTICATION UI FUNCTIONS ---
# -----------------------------------------------------------------
# (show_login_page, show_signup_page, show_forgot_password_page are unchanged)

def show_login_page():
    with st.container(border=True):
        st.header("Waste Management System Login")
        with st.form(key="login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            if submit_button:
                login(email, password)
        if st.button("Forgot Password?", key="forgot_pass_btn"):
            st.session_state.auth_page = "Forgot Password"
            st.rerun()

def show_signup_page():
    with st.container(border=True):
        st.header("Create New Account")
        with st.form(key="signup_form"):
            email = st.text_input("Email")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            role_options = {"Supervisor": 2, "Driver": 3, "Client": 4}
            role_name = st.selectbox("Select your role:", role_options.keys())
            submit_button = st.form_submit_button("Create Account")
            if submit_button:
                role_id = role_options[role_name]
                success = create_new_user(email, first_name, last_name, phone, password, role_id)
                if success:
                    st.session_state.auth_page = "Login"
                    st.rerun()

def show_forgot_password_page():
    with st.container(border=True):
        st.header("Reset Password")
        with st.form(key="request_otp_form"):
            email = st.text_input("Enter your account email")
            submit_otp_request = st.form_submit_button("Send Reset OTP")
            if submit_otp_request:
                request_password_reset(email)
        st.divider()
        with st.form(key="reset_password_form"):
            st.subheader("Enter OTP and New Password")
            email_otp = st.text_input("Email (for verification)", value=st.session_state.get('otp_email', ''))
            otp_attempt = st.text_input("OTP from email")
            new_password = st.text_input("New Password", type="password")
            submit_reset = st.form_submit_button("Reset Password")
            if submit_reset:
                success = reset_password(email_otp, otp_attempt, new_password)
                if success:
                    st.session_state.auth_page = "Login"
                    st.rerun()

# -----------------------------------------------------------------
# --- 2. SHARED CHAT UI FUNCTION ---
# -----------------------------------------------------------------

def show_internal_chat_ui():
    """
    A re-usable UI component for the internal group chat.
    Used by both Supervisor and Driver.
    """
    st.subheader("Internal Group Chat")
    
    # Chat message container
    chat_container = st.container(height=400)
    messages = get_group_messages()
    if messages is None:
        messages = []
        
    for msg in messages:
        actor_name = f"{msg['first_name']} ({msg['role_name']})"
        with chat_container.chat_message(name=actor_name):
            st.write(msg['message_content'])
            st.caption(f"{msg['sent_at']}")

    # Chat input
    message_content = st.text_input("Send a message to the group...")
    if st.button("Send Message", key="send_group_message"):
        if message_content:
            send_group_message(st.session_state['user_id'], message_content)
            st.rerun()
        else:
            st.warning("Please type a message.")

# -----------------------------------------------------------------
# --- 3. DASHBOARD UI FUNCTIONS ---
# -----------------------------------------------------------------

def dashboard_supervisor():
    st.header(f"Supervisor Dashboard")
    st.write(f"Welcome, {st.session_state['first_name']}!")

    if st.button("Logout", key="logout_sup"):
        st.session_state.clear()
        st.rerun()

    # --- UPDATED: Added new tabs ---
    tab_list = [
        "Route Assignment", 
        "Live Fleet Map", 
        "Route History",
        "Daily Booking Report",
        "Internal Chat",
        "Client Feedback"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_list)

    with tab1:
        st.subheader("Assign Routes for Today")
        with st.form("assignment_form"):
            drivers_list = get_available_drivers()
            vehicles_list = get_available_vehicles()
            bookings_list = get_pending_bookings()
            drivers = drivers_list if drivers_list is not None else []
            vehicles = vehicles_list if vehicles_list is not None else []
            bookings = bookings_list if bookings_list is not None else []
            driver_options = {d['user_id']: f"{d['first_name']} {d['last_name']}" for d in drivers}
            vehicle_options = {v['vehicle_id']: f"{v['license_plate']} ({v['model']})" for v in vehicles}
            booking_options = {b['booking_id']: f"{b['point_name']} (Booking #{b['booking_id']})" for b in bookings}

            selected_driver = st.selectbox("1. Select Driver", options=driver_options.keys(), format_func=lambda x: driver_options.get(x, "N/A"))
            selected_vehicle = st.selectbox("2. Select Vehicle", options=vehicle_options.keys(), format_func=lambda x: vehicle_options.get(x, "N/A"))
            selected_bookings = st.multiselect("3. Select Bookings to Assign", options=booking_options.keys(), format_func=lambda x: booking_options.get(x, "N/A"))

            submitted = st.form_submit_button("Create and Assign Route")
            if submitted:
                if not selected_driver or not selected_vehicle or not selected_bookings:
                    st.error("Please fill all fields and select at least one booking.")
                else:
                    success = create_route_assignment(st.session_state['user_id'], selected_driver, selected_vehicle, selected_bookings)
                    if success:
                        st.success("Route assigned successfully!")
                    else:
                        st.error("Failed to create route assignment.")

    with tab2:
        st.subheader("Live Vehicle Map")
        if st.button("Refresh Map"):
            st.rerun()
        locations = get_live_vehicle_locations()
        if not locations:
            st.warning("No live vehicle data available.")
        else:
            valid_locations = [loc for loc in locations if loc and loc.get('latitude') and loc.get('longitude')]
            if not valid_locations:
                st.warning("No valid location data to display.")
            else:
                map_center = [valid_locations[0]['latitude'], valid_locations[0]['longitude']]
                m = folium.Map(location=map_center, zoom_start=12)
                for loc in valid_locations:
                    folium.Marker(
                        [loc['latitude'], loc['longitude']],
                        tooltip=loc['license_plate'],
                        popup=f"{loc['license_plate']} @ {loc['timestamp']}"
                    ).add_to(m)
                st_folium(m, width='100%')

    with tab3:
        st.subheader("View Historical Routes")
        selected_date = st.date_input("Select a date to review", datetime.date.today() - datetime.timedelta(days=1))
        vehicles_list = get_active_vehicles_by_date(selected_date)
        vehicles = vehicles_list if vehicles_list is not None else []
        vehicle_options = {v['vehicle_id']: f"{v['license_plate']} ({v['model']})" for v in vehicles}

        if not vehicle_options:
            st.warning(f"No vehicles were active on {selected_date}.")
        else:
            selected_vehicle_id = st.selectbox(
                "Select a vehicle that was active on this date",
                options=vehicle_options.keys(),
                format_func=lambda x: vehicle_options.get(x, "N/A")
            )
            if selected_vehicle_id:
                history = get_route_history(selected_vehicle_id, selected_date)
                stops = history.get('stops')
                path = history.get('path')
                if not stops:
                    st.warning("No completed stops found for this vehicle on this date.")
                else:
                    st.write("**Completed Stops**")
                    stops_df = pd.DataFrame(stops)
                    stops_df['latitude'] = stops_df['latitude'].astype(float)
                    stops_df['longitude'] = stops_df['longitude'].astype(float)
                    st.dataframe(stops_df[['completed_at', 'point_name', 'collected_volume_kg']], use_container_width=True)
                    st.write("**Route Playback Map**")
                    map_center = [stops_df.iloc[0]['latitude'], stops_df.iloc[0]['longitude']]
                    m_history = folium.Map(location=map_center, zoom_start=13)
                    for _, stop in stops_df.iterrows():
                        folium.Marker(
                            [stop['latitude'], stop['longitude']],
                            tooltip=f"Stop: {stop['point_name']}",
                            popup=f"{stop['point_name']} @ {stop['completed_at']}",
                            icon=folium.Icon(color='green')
                        ).add_to(m_history)
                    if path:
                        path_coords = [(float(p['latitude']), float(p['longitude'])) for p in path]
                        folium.PolyLine(
                            path_coords,
                            color='blue',
                            weight=5,
                            opacity=0.7,
                            tooltip="Actual GPS Path"
                        ).add_to(m_history)
                    st_folium(m_history, width='100%')

    with tab4:
        st.subheader("Today's Booking & Payment Report")
        if st.button("Refresh Report"):
            st.rerun()
        report_data_list = get_daily_booking_report()
        report_data = report_data_list if report_data_list is not None else []
        if not report_data:
            st.warning("No bookings found for today.")
        else:
            df = pd.DataFrame(report_data)
            df = df[['first_name', 'last_name', 'phone', 'collection_point', 'job_status', 'payment_status', 'amount_paid']]
            st.dataframe(df, use_container_width=True)

    # --- NEW: Internal Chat Tab ---
    with tab5:
        show_internal_chat_ui()
        
    # --- NEW: Client Feedback Tab ---
    with tab6:
        st.subheader("View Client Feedback")
        if st.button("Refresh Feedback"):
            st.rerun()
            
        feedback_list = get_all_feedback()
        feedback = feedback_list if feedback_list is not None else []
        
        if not feedback:
            st.info("No client feedback has been submitted yet.")
        else:
            df = pd.DataFrame(feedback)
            df = df[['created_at', 'rating', 'comment', 'first_name', 'last_name', 'email']]
            st.dataframe(df, use_container_width=True)


def dashboard_driver():
    st.header(f"Driver App")
    st.write(f"Welcome, {st.session_state['first_name']}!")

    if st.button("Logout", key="logout_drv"):
        st.session_state.clear()
        st.rerun()
        
    # --- UPDATED: Added tabs ---
    tab1, tab2 = st.tabs(["My Stops", "Internal Chat"])
    
    with tab1:
        st.write("Getting your live location (this may require permission)...")
        location = streamlit_geolocation()
        if location is None or location.get('latitude') is None:
            st.warning("Please allow location access to use this app.")
            st.stop()

        driver_lat = location['latitude']
        driver_lon = location['longitude']
        st.success(f"Your current location: {driver_lat:.4f}, {driver_lon:.4f}")
        log_driver_location(st.session_state['user_id'], driver_lat, driver_lon)
        st.divider()

        st.subheader("Your Assigned Stops for Today")
        stops_list = get_driver_assignment(st.session_state['user_id'])
        stops = stops_list if stops_list is not None else []

        if not stops:
            st.success("No more stops for today. Great job!")
        else:
            for stop in stops:
                st.subheader(stop['point_name'])
                st.write(stop['address'])
                with st.form(key=f"form_stop_{stop['route_stop_id']}"):
                    weight = st.number_input("Enter Weight (KG)", min_value=0.0, format="%.2f", key=f"weight_{stop['route_stop_id']}")
                    amount = float(weight) * 3.0
                    st.info(f"Amount to Collect: ₹{amount:.2f}")
                    submitted = st.form_submit_button("Confirm Cash Payment & Mark Complete")
                    if submitted:
                        if weight <= 0:
                            st.error("Weight must be greater than zero.")
                        else:
                            result = mark_stop_complete(
                                st.session_state['user_id'],
                                stop['route_stop_id'],
                                driver_lat,
                                driver_lon,
                                weight
                            )
                            if "complete" in result:
                                st.success(result)
                                st.rerun()
                            else:
                                st.error(result)
                st.divider()

            stops_df = pd.DataFrame(stops)
            if not stops_df.empty:
                stops_df['latitude'] = stops_df['latitude'].astype(float)
                stops_df['longitude'] = stops_df['longitude'].astype(float)
                st.subheader("Remaining Stops Map")
                st.map(stops_df[['latitude', 'longitude']])

    with tab2:
        # --- NEW: Internal Chat Tab ---
        show_internal_chat_ui()
        

def dashboard_client():
    st.header(f"Client Portal")
    st.write(f"Welcome, {st.session_state['first_name']}!")

    if st.button("Logout", key="logout_cli"):
        st.session_state.clear()
        st.rerun()

    # --- UPDATED: Added "Give Feedback" tab ---
    tab1, tab2, tab3 = st.tabs(["Book Service", "My Bookings & Bills", "Give Feedback"])

    with tab1:
        st.subheader("Manage Your Service")
        points_list = get_client_collection_points(st.session_state['user_id'])
        points = points_list if points_list is not None else []
        if not points:
            st.warning("You have no registered collection points. Please add one to get started.")
            with st.form("add_first_point_form"):
                st.write("**Add Your First Collection Point**")
                point_name = st.text_input("Address Label (e.g., 'Home', 'Office')")
                address = st.text_area("Full Address")
                latitude = st.number_input("Latitude (e.g., 17.4435)", format="%.4f")
                longitude = st.number_input("Longitude (e.g., 78.3838)", format="%.4f")
                submitted = st.form_submit_button("Save Address")
                if submitted:
                    if not all([point_name, address, latitude, longitude]):
                        st.error("Please fill out all fields.")
                    else:
                        success = add_collection_point(st.session_state['user_id'], point_name, address, latitude, longitude)
                        if success:
                            st.success("Address added successfully! You can now book a service.")
                            st.rerun()
                        else:
                            st.error("Failed to add address.")
        else:
            st.subheader("Book a New Waste Collection")
            point_options = {p['point_id']: p['point_name'] for p in points}
            with st.form("booking_form"):
                selected_point = st.selectbox("Select Collection Point", options=point_options.keys(), format_func=lambda x: point_options.get(x, "N/A"))
                selected_date = st.date_input("Select Date", min_value=datetime.date.today())
                submitted = st.form_submit_button("Book Service")
                if submitted:
                    booking_id = create_booking(st.session_state['user_id'], selected_point, selected_date)
                    if booking_id:
                        st.success(f"Booking successful! Your Booking ID is {booking_id}.")
                    else:
                        st.error("Failed to create booking.")
            st.divider()
            with st.expander("Add a new collection point (address)"):
                with st.form("add_new_point_form"):
                    st.write("**Add a New Collection Point**")
                    point_name = st.text_input("Address Label (e.g., 'Home', 'Office')", key="new_name")
                    address = st.text_area("Full Address", key="new_addr")
                    latitude = st.number_input("Latitude (e.g., 17.4435)", format="%.4f", key="new_lat")
                    longitude = st.number_input("Longitude (e.g., 78.3838)", format="%.4f", key="new_lon")
                    submitted_new = st.form_submit_button("Save New Address")
                    if submitted_new:
                        if not all([point_name, address, latitude, longitude]):
                            st.error("Please fill out all fields.")
                        else:
                            success = add_collection_point(st.session_state['user_id'], point_name, address, latitude, longitude)
                            if success:
                                st.success("New address added!")
                                st.rerun()
                            else:
                                st.error("Failed to add new address.")

    with tab2:
        st.subheader("Your Bookings & Bills")
        bookings_list = get_client_bookings(st.session_state['user_id'])
        bookings = bookings_list if bookings_list is not None else []
        if not bookings:
            st.write("You have no booking history.")
        else:
            st.write("Here is your complete history of service and payments.")
            st.dataframe(bookings, use_container_width=True)

    # --- NEW: Give Feedback Tab ---
    with tab3:
        st.subheader("Give Feedback on Our Service")
        with st.form("feedback_form"):
            st.write("We value your feedback. Please let us know how we did.")
            rating = st.slider("Your Rating (1=Poor, 5=Excellent)", 1, 5, 5)
            comment = st.text_area("Your comments (optional)")
            
            feedback_submitted = st.form_submit_button("Submit Feedback")
            
            if feedback_submitted:
                success = submit_feedback(st.session_state['user_id'], rating, comment)
                if success:
                    st.success("Thank you for your feedback!")
                    st.balloons()
                else:
                    st.error("Sorry, we couldn't save your feedback. Please try again.")

def dashboard_admin():
    st.header(f"Admin Panel")
    st.write(f"Welcome, {st.session_state['first_name']}!")
    if st.button("Logout", key="logout_adm"):
        st.session_state.clear()
        st.rerun()
    st.write("Admin features (like user management, audit logs) would go here.")


# -----------------------------------------------------------------
# --- 4. MAIN APPLICATION ROUTER ---
# -----------------------------------------------------------------
# (This main function is unchanged)
def main():
    if st.session_state.get('logged_in'):
        st.set_page_config(page_title="WMS Dashboard", layout="wide")
    else:
        st.set_page_config(page_title="WMS Login", layout="centered")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['user_id'] = None
        st.session_state['first_name'] = None

    if 'auth_page' not in st.session_state:
        st.session_state['auth_page'] = "Login"

    if st.session_state['logged_in']:
        role = st.session_state['role']
        if role == 'Administrator':
            dashboard_admin()
        elif role == 'Supervisor':
            dashboard_supervisor()
        elif role == 'Driver':
            dashboard_driver()
        elif role == 'Client':
            dashboard_client()
        else:
            st.error("Unknown role. Logging out.")
            st.session_state.clear()
            st.rerun()
    else:
        st.sidebar.title("Navigation")
        if st.sidebar.button("Login", use_container_width=True):
            st.session_state.auth_page = "Login"
            st.rerun()
        if st.sidebar.button("Sign Up", use_container_width=True):
            st.session_state.auth_page = "Sign Up"
            st.rerun()

        if st.session_state.auth_page == "Login":
            show_login_page()
        elif st.session_state.auth_page == "Sign Up":
            show_signup_page()
        elif st.session_state.auth_page == "Forgot Password":
            show_forgot_password_page()

if __name__ == "__main__":
    main()