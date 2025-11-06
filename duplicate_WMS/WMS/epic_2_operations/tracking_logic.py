# In epic_2_operations/tracking_logic.py

from utils.db_connector import fetch_all, fetch_one, execute_query
from utils.geo_utils import calculate_distance
from epic_3_billing.payment_logic import process_cash_payment

# ... (all your existing functions: get_live_vehicle_locations, get_driver_assignment, etc. remain unchanged) ...

def get_live_vehicle_locations():
    """Gets the most recent location of all active vehicles (US 2.1)"""
    query = """
        SELECT v.license_plate, vl.latitude, vl.longitude, vl.timestamp
        FROM VehicleLocations vl
        JOIN (
            SELECT vehicle_id, MAX(timestamp) AS max_time
            FROM VehicleLocations
            GROUP BY vehicle_id
        ) AS latest ON vl.vehicle_id = latest.vehicle_id AND vl.timestamp = latest.max_time
        JOIN Vehicles v ON vl.vehicle_id = v.vehicle_id
    """
    return fetch_all(query)

def get_driver_assignment(driver_id):
    """Gets the pending stops for a driver's active assignment (US 2.3)"""
    query = """
        SELECT rs.route_stop_id, cp.point_name, cp.address, cp.latitude, cp.longitude, rs.status
        FROM RouteStops rs
        JOIN RouteAssignments ra ON rs.assignment_id = ra.assignment_id
        JOIN CollectionPoints cp ON rs.point_id = cp.point_id
        WHERE ra.driver_id = %s
        AND ra.assigned_date = CURDATE()
        AND rs.status = 'Pending'
        ORDER BY rs.stop_order ASC
    """
    return fetch_all(query, (driver_id,))

def _check_and_complete_assignment(assignment_id):
    """
    Private helper function. Checks if all stops for an assignment are done.
    If so, marks the main RouteAssignment as 'Completed'.
    """
    if not assignment_id:
        return

    check_query = """
        SELECT COUNT(*) as pending_count
        FROM RouteStops
        WHERE assignment_id = %s AND status = 'Pending'
    """
    result = fetch_one(check_query, (assignment_id,))
    
    if result and result['pending_count'] == 0:
        complete_query = """
            UPDATE RouteAssignments
            SET status = 'Completed'
            WHERE assignment_id = %s
        """
        execute_query(complete_query, (assignment_id,))
        print(f"Assignment {assignment_id} marked as completed.")

def log_driver_location(driver_id, driver_lat, driver_lon):
    """
    Finds the driver's active vehicle and logs their current location.
    This is called on every reload of the driver's dashboard.
    """
    try:
        vehicle_query = """
            SELECT vehicle_id FROM RouteAssignments
            WHERE driver_id = %s 
              AND assigned_date = CURDATE() 
              AND status IN ('Pending', 'In Progress')
            LIMIT 1
        """
        assignment = fetch_one(vehicle_query, (driver_id,))
        vehicle_id = assignment.get('vehicle_id') if assignment else None
        
        if vehicle_id:
            log_location_query = """
                INSERT INTO VehicleLocations (vehicle_id, latitude, longitude, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            execute_query(log_location_query, (vehicle_id, driver_lat, driver_lon))
            return True
        return False
    except Exception as e:
        print(f"Error logging driver location: {e}")
        return False

def mark_stop_complete(driver_id, route_stop_id, driver_lat, driver_lon, weight):
    """
    Marks a stop as complete, logs cash payment, and checks if assignment is finished.
    """
    
    stop_query = """
        SELECT cp.latitude, cp.longitude, rs.booking_id, rs.assignment_id
        FROM RouteStops rs
        JOIN CollectionPoints cp ON rs.point_id = cp.point_id
        WHERE rs.route_stop_id = %s
    """
    stop = fetch_one(stop_query, (route_stop_id,))
    if not stop:
        return "Error: Stop not found."

    booking_id_to_update = stop['booking_id']
    assignment_id_to_check = stop['assignment_id']
    stop_coords = (stop['latitude'], stop['longitude'])
    driver_coords = (driver_lat, driver_lon)
    
    distance = calculate_distance(driver_coords, stop_coords)
    if distance > 100:
        return f"Verification Failed. You are {distance:.0f} meters away. Must be within 100m."

    vehicle_query = """
        SELECT vehicle_id FROM RouteAssignments
        WHERE driver_id = %s AND assigned_date = CURDATE() AND status IN ('Pending', 'In Progress')
        LIMIT 1
    """
    assignment = fetch_one(vehicle_query, (driver_id,))
    vehicle_id = assignment.get('vehicle_id') if assignment else None
    
    if vehicle_id:
        log_location_query = """
            INSERT INTO VehicleLocations (vehicle_id, latitude, longitude, timestamp)
            VALUES (%s, %s, %s, NOW())
        """
        execute_query(log_location_query, (vehicle_id, driver_lat, driver_lon))

    if booking_id_to_update:
        amount = float(weight) * 3.0
        payment_success = process_cash_payment(booking_id_to_update, amount)
        if not payment_success:
            return "Error: Could not process cash payment."

    update_stop_query = """
        UPDATE RouteStops
        SET status = 'Completed',
            completed_at = NOW(),
            verification_gps_lat = %s,
            verification_gps_lon = %s,
            collected_volume_kg = %s
        WHERE route_stop_id = %s
    """
    execute_query(update_stop_query, (driver_lat, driver_lon, weight, route_stop_id))
    
    if booking_id_to_update:
        update_booking_query = """
            UPDATE ServiceBookings
            SET status = 'Completed'
            WHERE booking_id = %s
        """
        execute_query(update_booking_query, (booking_id_to_update,))
    
    _check_and_complete_assignment(assignment_id_to_check)
    
    return "Stop marked complete! Payment logged."

# --- ADD THIS NEW FUNCTION ---
def get_route_history(vehicle_id, selected_date):
    """
    Gets all completed stops and the full GPS path for a vehicle
    on a specific date (US 2.2).
    """
    
    # 1. Get all completed stops
    stops_query = """
        SELECT 
            cp.point_name, 
            rs.completed_at, 
            rs.verification_gps_lat AS latitude,
            rs.verification_gps_lon AS longitude,
            rs.collected_volume_kg
        FROM RouteStops rs
        JOIN CollectionPoints cp ON rs.point_id = cp.point_id
        JOIN RouteAssignments ra ON rs.assignment_id = ra.assignment_id
        WHERE ra.vehicle_id = %s
          AND ra.assigned_date = %s
          AND rs.status = 'Completed'
        ORDER BY rs.completed_at;
    """
    
    # 2. Get the full GPS path from VehicleLocations
    path_query = """
        SELECT latitude, longitude
        FROM VehicleLocations
        WHERE vehicle_id = %s
          AND DATE(timestamp) = %s
        ORDER BY timestamp;
    """
    
    stops = fetch_all(stops_query, (vehicle_id, selected_date))
    path = fetch_all(path_query, (vehicle_id, selected_date))
    
    return {"stops": stops, "path": path}