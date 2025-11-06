from utils.db_connector import fetch_all, execute_query

def submit_feedback(client_id, rating, comment):
    """
    Saves new client feedback to the database.
    """
    query = """
        INSERT INTO ClientFeedback (client_id, rating, comment)
        VALUES (%s, %s, %s)
    """
    feedback_id = execute_query(query, (client_id, rating, comment))
    return True if feedback_id else False

def get_all_feedback():
    """
    Retrieves all feedback, joining with client info for the supervisor.
    """
    query = """
        SELECT 
            cf.rating,
            cf.comment,
            cf.created_at,
            u.first_name,
            u.last_name,
            u.email
        FROM ClientFeedback cf
        JOIN Users u ON cf.client_id = u.user_id
        ORDER BY cf.created_at DESC
    """
    return fetch_all(query)