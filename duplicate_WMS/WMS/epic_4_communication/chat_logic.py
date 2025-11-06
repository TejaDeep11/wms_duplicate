from utils.db_connector import fetch_all, execute_query

def get_group_messages():
    """
    Gets all messages for the internal group chat, joining with user info.
    """
    query = """
        SELECT 
            gcm.message_content, 
            gcm.sent_at,
            u.first_name,
            r.role_name
        FROM GroupChatMessages gcm
        JOIN Users u ON gcm.sender_id = u.user_id
        JOIN Roles r ON u.role_id = r.role_id
        ORDER BY gcm.sent_at ASC
        LIMIT 100; -- Get the last 100 messages
    """
    return fetch_all(query)

def send_group_message(sender_id, message):
    """
    Adds a new message to the group chat.
    """
    query = """
        INSERT INTO GroupChatMessages (sender_id, message_content)
        VALUES (%s, %s)
    """
    execute_query(query, (sender_id, message))