
"""
Reddit Pulse - Utility Functions Module
========================================
This module provides helper functions for the Reddit Pulse application,
including OTP generation and email sending functionality.

Author: Reddit Pulse Team
License: MIT
"""

import smtplib
from email.mime.text import MIMEText
import random


def generate_otp():
    """
    Generate a 4-digit one-time password (OTP) for email verification.

    Returns:
        str: A random 4-digit string (e.g., '7342', '0158')

    Example:
        >>> otp = generate_otp()
        >>> print(otp)
        '4829'
    """
    return str(random.randint(1000, 9999))


def send_otp_email(receiver_email, otp_code):
    """
    Send an OTP verification code to a user's email address.

    This function uses Gmail's SMTP server with SSL encryption to send
    verification emails for user registration.

    Args:
        receiver_email (str): Recipient's email address
        otp_code (str): 4-digit OTP code to send

    Returns:
        bool: True if email sent successfully, False otherwise

    Security Notes:
        - Uses Gmail App Password (NOT regular account password)
        - Password should be stored in environment variables in production
        - Current password is application-specific and has limited scope

    Error Handling:
        - Catches SMTP connection errors
        - Gracefully handles server disconnections
        - Returns False on any failure (login error, network issue, etc.)

    Example:
        >>> success = send_otp_email('user@example.com', '1234')
        >>> if success:
        ...     print("Email sent!")
    """
    # Gmail account credentials
    sender = "redditpulse55@gmail.com"
    password = "agbb bcnx nyts xytz" # Gmail App Password (not account password)

    # Compose email message
    msg = MIMEText(f"Your Verification Code is: {otp_code}")
    msg['Subject'] = "Reddit Pulse Verification"
    msg['From'] = sender
    msg['To'] = receiver_email

    try:
        # Connect to Gmail's SMTP server with SSL encryption
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)

        # Send the email
        server.sendmail(sender, receiver_email, msg.as_string())

        # Attempt to close connection gracefully
        # If Gmail has already closed the connection, we ignore the error
        # since the email was already sent successfully
        try:
            server.quit()
        except Exception:
            pass  # Connection already closed by server

        return True

    except Exception as e:
        # Critical error occurred (login failed, network error, etc.)
        print(f"CRITICAL MAIL ERROR: {e}")
        return False
