# In epic_1_routing/assignment_logic.py

from utils.db_connector import fetch_one, fetch_all, execute_query

# ... (all your existing functions: get_available_drivers, get_available_vehicles, etc. remain unchanged) ...

def get_available_drivers():
    """
    Finds all 'Drivers' who are NOT on an active ('Pending' or 'In Progress')
    route for today.
    """
    query = """
        SELECT u.user_id, u.first_name, u.last_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        LEFT JOIN (
            SELECT driver_id
            FROM RouteAssignments
            WHERE assigned_date = CURDATE()
            AND status IN ('Pending', 'In Progress')
        ) AS active_assignments ON u.user_id = active_assignments.driver_id
        WHERE
            r.role_name = 'Driver'
            AND active_assignments.driver_id IS NULL;
    """
    return fetch_all(query)

def get_available_vehicles():
    """
    Finds all vehicles that are NOT on an active ('Pending' or 'In Progress')
    route for today.
    """
    query = """
        SELECT v.vehicle_id, v.license_plate, v.model
        FROM Vehicles v
        LEFT JOIN (
            SELECT vehicle_id
            FROM RouteAssignments
            WHERE assigned_date = CURDATE()
            AND status IN ('Pending', 'In Progress')
        ) AS active_assignments ON v.vehicle_id = active_assignments.vehicle_id
        WHERE active_assignments.vehicle_id IS NULL;
    """
    return fetch_all(query)

def get_pending_bookings():
    """
    Finds all bookings for today that are 'Approved' and not yet part of any route.
    """
    query = """
        SELECT sb.booking_id, cp.point_name, cp.latitude, cp.longitude
        FROM ServiceBookings sb
        JOIN CollectionPoints cp ON sb.point_id = cp.point_id
        LEFT JOIN (
            SELECT rs.booking_id
            FROM RouteStops rs
            JOIN RouteAssignments ra ON rs.assignment_id = ra.assignment_id
            WHERE ra.assigned_date = CURDATE() AND rs.booking_id IS NOT NULL
        ) AS assigned_bookings ON sb.booking_id = assigned_bookings.booking_id
        WHERE
            sb.requested_date = CURDATE()
            AND sb.status = 'Approved'
            AND assigned_bookings.booking_id IS NULL;
    """
    return fetch_all(query)

def create_route_assignment(supervisor_id, driver_id, vehicle_id, booking_ids):
    """
    Creates a new route assignment (defaulting to 'Pending')
    and adds all selected bookings as stops.
    """
    try:
        default_route_id = 1 
        assignment_query = """
            INSERT INTO RouteAssignments (route_id, vehicle_id, driver_id, assigned_date, status)
            VALUES (%s, %s, %s, CURDATE(), 'Pending')
        """
        assignment_id = execute_query(assignment_query, (default_route_id, vehicle_id, driver_id))
        
        if not assignment_id:
            print("Failed to create RouteAssignment entry.")
            return False
        
        stop_query = """
            INSERT INTO RouteStops (assignment_id, point_id, booking_id, stop_order, status)
            SELECT %s, sb.point_id, sb.booking_id, %s, 'Pending'
            FROM ServiceBookings sb
            WHERE sb.booking_id = %s
        """
        
        for stop_order, booking_id in enumerate(booking_ids, 1):
            execute_query(stop_query, (assignment_id, stop_order, booking_id))
            
        return True
    except Exception as e:
        print(f"Error creating assignment: {e}")
        return False

def get_daily_booking_report():
    """
    Gets a full report of all bookings for today, including client details
    and payment status for the supervisor.
    """
    query = """
        SELECT 
            u.first_name, 
            u.last_name,
            u.phone,
            cp.point_name AS collection_point,
            sb.status AS job_status,
            COALESCE(p.status, 'Unpaid') AS payment_status,
            p.amount AS amount_paid
        FROM ServiceBookings sb
        JOIN Users u ON sb.client_id = u.user_id
        JOIN CollectionPoints cp ON sb.point_id = cp.point_id
        LEFT JOIN Payments p ON sb.booking_id = p.booking_id
        WHERE sb.requested_date = CURDATE()
        ORDER BY u.first_name;
    """
    return fetch_all(query)

# --- ADD THIS NEW FUNCTION ---
def get_active_vehicles_by_date(selected_date):
    """
    Finds all vehicles that had an assignment on a specific date.
    """
    query = """
        SELECT DISTINCT v.vehicle_id, v.license_plate, v.model
        FROM Vehicles v
        JOIN RouteAssignments ra ON v.vehicle_id = ra.vehicle_id
        WHERE ra.assigned_date = %s
    """
    return fetch_all(query, (selected_date,))