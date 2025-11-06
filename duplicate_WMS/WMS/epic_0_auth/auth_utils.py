from utils.db_connector import fetch_one

def get_user_by_email(email):
    query = """
        SELECT u.user_id, u.first_name, u.password_hash, r.role_name
        FROM Users u
        JOIN Roles r ON u.role_id = r.role_id
        WHERE u.email = %s
    """
    return fetch_one(query, (email,))