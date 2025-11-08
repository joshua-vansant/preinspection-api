import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "DriveCheck")
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL", "https://drivecheck.app/reset-password")

def send_reset_email(to_email: str, token: str) -> bool:
    if not SENDGRID_API_KEY:
        print("SENDGRID_API_KEY not configured")
        return False

    # reset_link = f"{FRONTEND_RESET_URL}?token={token}"
    reset_link = f"https://preinspection-api.onrender.com/auth/deep-reset?token={token}"
    # reset_link = f"drivecheck://reset-password?token={token}"

    subject = "Reset Your DriveCheck Password"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2b6cb0;">DriveCheck Password Reset</h2>
        <p>Hello,</p>
        <p>We received a request to reset your DriveCheck password. 
        Click the button below to choose a new password:</p>
        <p style="text-align: center;">
            <a href="{reset_link}" 
               style="background-color: #2b6cb0; color: white; 
                      padding: 10px 20px; text-decoration: none; 
                      border-radius: 5px;">Reset Password</a>
        </p>
        <p>If you didn’t request this, you can safely ignore this email.</p>
        <p>— The DriveCheck Team</p>
    </div>
    """

    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    # Disable click tracking so link stays exact
    tracking_settings = TrackingSettings(
        click_tracking=ClickTracking(enable=False, enable_text=False)
    )
    message.tracking_settings = tracking_settings
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Password reset email sent to {to_email}, status {response.status_code}")
        return 200 <= response.status_code < 300
    except Exception as e:
        print(f"Error sending reset email: {e}")
        return False
