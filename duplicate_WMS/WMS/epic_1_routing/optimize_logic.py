from utils.db_connector import fetch_all, fetch_one, execute_query
from utils.geo_utils import calculate_distance

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

def mark_stop_complete(driver_id, route_stop_id, driver_lat, driver_lon):
    """Marks a stop as complete after checking GPS (US 2.3 & 2.4)"""
    
    stop_query = """
        SELECT cp.latitude, cp.longitude
        FROM RouteStops rs
        JOIN CollectionPoints cp ON rs.point_id = cp.point_id
        WHERE rs.route_stop_id = %s
    """
    stop = fetch_one(stop_query, (route_stop_id,))
    if not stop:
        return "Error: Stop not found."

    stop_coords = (stop['latitude'], stop['longitude'])
    driver_coords = (driver_lat, driver_lon)
    distance = calculate_distance(driver_coords, stop_coords)

    # US 2.4: The 100-meter check
    if distance > 515302:
        return f"Verification Failed. You are {distance:.0f} meters away. Must be within 100m."

    # US 2.3: Mark as complete
    update_query = """
        UPDATE RouteStops
        SET status = 'Completed',
            completed_at = NOW(),
            verification_gps_lat = %s,
            verification_gps_lon = %s
        WHERE route_stop_id = %s
    """
    execute_query(update_query, (driver_lat, driver_lon, route_stop_id))
    return "Stop marked complete!"