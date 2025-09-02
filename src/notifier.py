"""Notification system for transfer results"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime


class Notifier:
    """Handles notifications for transfer results"""

    def __init__(self, notification_config: Dict[str, Any]):
        self.config = notification_config
        self.logger = logging.getLogger(__name__)

    def send_completion_notification(self, results: Dict[str, Any]):
        """Send notification when transfer completes"""
        try:
            if not self.config.get("enabled", False):
                self.logger.info("Notifications disabled in config")
                return

            subject = f"File Transfer Complete - {results['successful_transfers']}/{results['total_batches']} Successful"

            message = self._format_completion_message(results)

            self._send_email(subject, message)
            self.logger.info("Completion notification sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to send completion notification: {str(e)}")

    def send_error_notification(self, error_message: str):
        """Send notification when critical error occurs"""
        try:
            if not self.config.get("enabled", False):
                return

            subject = "URGENT: File Transfer Automation Failed"
            message = f"""
File Transfer Automation encountered a critical error:

Error: {error_message}
Timestamp: {datetime.now()}

Please check the system and logs immediately.

This is an automated message from BBU File Transfer System.
            """

            self._send_email(subject, message)
            self.logger.info("Error notification sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to send error notification: {str(e)}")

    def _format_completion_message(self, results: Dict[str, Any]) -> str:
        """Format completion notification message"""
        success_rate = (
            (results["successful_transfers"] / results["total_batches"] * 100)
            if results["total_batches"] > 0
            else 0
        )

        message = f"""
BBU File Transfer Automation - Completion Report

Summary:
- Total Batches Processed: {results['total_batches']}
- Successful Transfers: {results['successful_transfers']}
- Failed Transfers: {results['failed_transfers']}
- Total Files Copied: {results['total_files_copied']}
- Success Rate: {success_rate:.1f}%

"""

        if results["successful_transfers"] > 0:
            message += "✅ Successful Batches:\n"
            for batch in results["batch_details"]:
                if batch["success"]:
                    message += (
                        f"  - {batch['batch_id']}: {batch['files_copied']} files\n"
                    )

        if results["failed_transfers"] > 0:
            message += "\n❌ Failed Batches:\n"
            for batch in results["batch_details"]:
                if not batch["success"]:
                    message += (
                        f"  - {batch['batch_id']}: {', '.join(batch['errors'])}\n"
                    )

        message += f"\nTimestamp: {datetime.now()}\n"
        message += "This is an automated message from BBU File Transfer System."

        return message

    def _send_email(self, subject: str, message: str):
        """Send email notification"""
        if "email" not in self.config:
            self.logger.warning(
                "Email configuration not found, skipping email notification"
            )
            return

        email_config = self.config["email"]

        msg = MIMEMultipart()
        msg["From"] = email_config["from_address"]
        msg["To"] = ", ".join(email_config["to_addresses"])
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Send email
        try:
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            # If authentication is needed, uncomment these lines:
            # if "username" in email_config and "password" in email_config:
            #     server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()
            self.logger.info(f"Email notification sent: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")