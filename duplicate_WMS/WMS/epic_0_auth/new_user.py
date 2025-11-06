import streamlit as st
from epic_0_auth.hash import hash_password
from utils.db_connector import execute_query
from epic_0_auth.auth_utils import get_user_by_email

def create_new_user(email, first_name, last_name, phone, password, role_id):
    if get_user_by_email(email):
        st.error("Error: An account with this email already exists.")
        return False

    hashed_pass = hash_password(password)
    query = """
        INSERT INTO Users (role_id, first_name, last_name, email, password_hash, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (role_id, first_name, last_name, email, hashed_pass, phone)
    
    user_id = execute_query(query, params)

    if user_id:
        st.success(f"Account created successfully! Please log in.")
        return True
    else:
        st.error("Error: Could not create account.")
        return False