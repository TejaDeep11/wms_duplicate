# This is a simple dictionary to simulate a user session.
# In a real web app, this would be handled by a session framework (e.g., Flask-Session)
SESSION = {}

def create_session(user_id, role, first_name):
    """Stores the logged-in user's data."""
    SESSION['user_id'] = user_id
    SESSION['role'] = role
    SESSION['first_name'] = first_name
    print(f"\n--- Session created for {first_name} ({role}) ---")

def get_session():
    """Retrieves the current session data."""
    return SESSION

def clear_session():
    """Logs the user out by clearing the session."""
    SESSION.clear()
    print("\n--- Session cleared. User logged out. ---")