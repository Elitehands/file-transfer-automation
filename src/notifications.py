"""Email notifications for transfer results"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_completion_email(results: Dict[str, Any],
                          config: Dict[str, Any]) -> bool:
    """Send completion notification email"""
    notifications = config.get("notifications", {})

    if not notifications.get("enabled", False):
        logger.info("Email notifications disabled")
        return True

    try:
        subject = (
            f"File Transfer Complete - {results['successful_transfers']}/"
            f"{results['total_batches']} Successful"
        )
        message = _format_email_message(results)

        return _send_email(subject, message, notifications)

    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False


def _format_email_message(results: Dict[str, Any]) -> str:
    """Format completion email message"""
    success_rate = (
        results["successful_transfers"] / results["total_batches"] * 100
        if results["total_batches"] > 0 else 0
    )

    message = f"""File Transfer Automation - Completion Report

Summary:
- Total Batches: {results['total_batches']}
- Successful: {results['successful_transfers']}
- Failed: {results['failed_transfers']}
- Files Copied: {results['total_files_copied']}
- Success Rate: {success_rate:.1f}%

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from File Transfer System.
"""
    return message


def _send_email(subject: str, message: str,
                notifications: Dict[str, Any]) -> bool:
    """Send email using SMTP"""
    smtp_config = notifications.get("smtp", {})
    recipients = notifications.get("recipients", [])

    if not recipients:
        logger.warning("No email recipients configured")
        return False

    try:
        username = os.getenv("SMTP_USERNAME")
        password = os.getenv("SMTP_PASSWORD")

        if not username or not password:
            logger.warning(
                "SMTP credentials not found in environment variables"
            )
            return False

        msg = MIMEMultipart()
        msg["From"] = smtp_config.get("from_address", username)
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(
            smtp_config.get("server", "smtp.gmail.com"),
            smtp_config.get("port", 587)
        )
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {len(recipients)} recipients")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def test_email_notification():
    """Test email sending with your Gmail account"""
    print("Testing email notification...")

    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    if not username or not password:
        print("❌ Set environment variables first:")
        print("SMTP_USERNAME=Jibolasherpad@gmail.com")
        print("SMTP_PASSWORD=dhan tyit amsz tojk")
        return False

    config = {
        "notifications": {
            "enabled": True,
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "from_address": username
            },
            "recipients": [username]
        }
    }

    results = {
        "total_batches": 2,
        "successful_transfers": 2,
        "failed_transfers": 0,
        "total_files_copied": 10
    }

    success = send_completion_email(results, config)
    if success:
        print("✅ Email test successful! Check your inbox.")
    else:
        print("❌ Email test failed. Check logs for details.")

    return success


if __name__ == "__main__":
    test_email_notification()