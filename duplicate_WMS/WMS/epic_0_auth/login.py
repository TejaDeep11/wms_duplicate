import streamlit as st
from epic_0_auth.auth_utils import get_user_by_email
from epic_0_auth.hash import check_password

def login(email, password):
    if not email or not password:
        st.error("Please enter both email and password.")
        return

    user = get_user_by_email(email)

    if not user:
        st.error("Login Failed: No account found with that email.")
        return

    if check_password(password, user['password_hash']):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['user_id']
        st.session_state['role'] = user['role_name']
        st.session_state['first_name'] = user['first_name']
        st.rerun()
    else:
        st.error("Login Failed: Incorrect password.")