import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(to_email, otp):
    """
    Sends a password reset OTP to the user's email.
    """
    try:
        # Get email credentials from .env
        sender_email = os.getenv('EMAIL_USER')
        sender_password = os.getenv('EMAIL_PASSWORD')
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))

        if not all([sender_email, sender_password, smtp_server, smtp_port]):
            print("Email configuration is missing in .env file.")
            return False

        # Create the email message
        subject = "Your Password Reset OTP for WMS"
        body = f"""
        Hello,

        You requested a password reset for your WMS account.
        Your One-Time Password (OTP) is: {otp}

        This OTP will expire in 10 minutes.

        If you did not request this, please ignore this email.
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        
        print(f"Successfully sent OTP to {to_email}")
        return True
    except smtplib.SMTPException as e:
        print(f"Error: Unable to send email. {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False