# In epic_3_billing/booking_logic.py

from utils.db_connector import execute_query, fetch_all

def create_booking(client_id, point_id, requested_date):
    """Creates a new service booking (US 3.1)"""
    query = """
        INSERT INTO ServiceBookings (client_id, point_id, requested_date, status)
        VALUES (%s, %s, %s, 'Approved')
    """
    booking_id = execute_query(query, (client_id, point_id, requested_date))
    return booking_id

def get_client_bookings(client_id):
    """
    Gets all bookings for a specific client, including payment status and amount.
    This now serves as the client's bill.
    """
    query = """
        SELECT 
            sb.requested_date, 
            cp.point_name,
            sb.status AS job_status, 
            p.status AS payment_status,
            p.amount AS amount_paid
        FROM ServiceBookings sb
        JOIN CollectionPoints cp ON sb.point_id = cp.point_id
        LEFT JOIN Payments p ON sb.booking_id = p.booking_id
        WHERE sb.client_id = %s
        ORDER BY sb.requested_date DESC
    """
    return fetch_all(query, (client_id,))

def get_client_collection_points(client_id):
    """Gets all collection points for a client"""
    query = "SELECT point_id, point_name FROM CollectionPoints WHERE client_id = %s"
    return fetch_all(query, (client_id,))

def add_collection_point(client_id, point_name, address, latitude, longitude):
    """
    Adds a new collection point (address) for a client.
    """
    query = """
        INSERT INTO CollectionPoints (client_id, point_name, address, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (client_id, point_name, address, latitude, longitude)
    point_id = execute_query(query, params)
    return True if point_id else False