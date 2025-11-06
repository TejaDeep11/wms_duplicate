import streamlit as st
import random
import string
from utils.email_utils import send_otp_email
from epic_0_auth.auth_utils import get_user_by_email
from utils.db_connector import execute_query
from epic_0_auth.hash import hash_password

def request_password_reset(email):
    user = get_user_by_email(email)
    if not user:
        st.error("Error: No account found with that email.")
        return

    otp = ''.join(random.choices(string.digits, k=6))
    
    if send_otp_email(email, otp):
        st.session_state['otp_email'] = email
        st.session_state['otp_code'] = otp
        st.success("An OTP has been sent to your email. Please check your inbox.")
    else:
        st.error("Error: Could not send OTP email. Please check your .env settings.")

def reset_password(email, otp_attempt, new_password):
    if st.session_state.get('otp_email') == email and \
       st.session_state.get('otp_code') == otp_attempt:
        
        new_hash = hash_password(new_password)
        query = "UPDATE Users SET password_hash = %s WHERE email = %s"
        
        if execute_query(query, (new_hash, email)):
            st.success("Password reset successful! You can now log in.")
            del st.session_state['otp_email']
            del st.session_state['otp_code']
            return True
        else:
            st.error("Error: Could not update password in database.")
            return False
    else:
        st.error("Error: Invalid email or OTP.")
        return False